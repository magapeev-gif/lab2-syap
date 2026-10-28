"""Работа с файлами: уровень (JSON) и таблица рекордов (CSV)."""
import csv
import json
import logging
from collections import deque
from datetime import datetime

from constants import *
import game_log

# Уровень по умолчанию. Используется, если level.json отсутствует или повреждён.
DEFAULT_CONFIG = {
    "level": [
        "11111111111111111111",
        "10000000010000000001",
        "10111110010111011101",
        "10100000000100000001",
        "10101111110101111101",
        "10000000000000000001",
        "11110111111011110111",
        "10000100000000100001",
        "10111101111110101101",
        "10000000000000100001",
        "10111111011110111101",
        "10000000010000000001",
        "10111101010111111101",
        "10000001000000000001",
        "11111111111111111111",
    ],
    "player_start": list(PLAYER_START),
    "exit": list(EXIT_CELL),
    "time_limit": TIME_LIMIT,
    "wall_shift_interval": WALL_SHIFT_INTERVAL,
}

# Заголовки CSV (порядок = порядок колонок в файле)
F_NAME, F_STATUS, F_TIME, F_SHIFTS, F_DATE = "Имя", "Статус", "Время, с", "Сдвигов стен", "Дата"
RECORD_FIELDS = [F_NAME, F_STATUS, F_TIME, F_SHIFTS, F_DATE]


# ---------------------------------------------------------------- уровень (JSON)

def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _parse_cell(value, name, grid):
    """Проверяет координаты [x, y]: формат, границы, что клетка - пол."""
    if not isinstance(value, (list, tuple)) or len(value) != 2 or not all(_is_int(v) for v in value):
        raise ValueError(f"'{name}' должен быть списком [x, y] из двух целых чисел")
    gx, gy = value
    if not (1 <= gx <= GRID_COLUMNS - 2 and 1 <= gy <= GRID_ROWS - 2):
        raise ValueError(f"'{name}' = {list(value)} вне игрового поля "
                         f"(x: 1..{GRID_COLUMNS - 2}, y: 1..{GRID_ROWS - 2})")
    if grid[gy][gx] != TILE_FLOOR:
        raise ValueError(f"'{name}' = {list(value)} указывает на стену")
    return (gx, gy)


def _exit_reachable(grid, start, goal):
    """Поиск в ширину по клеткам-полу: можно ли дойти от старта до выхода."""
    queue, seen = deque([start]), {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (x + dx, y + dy)
            if nxt not in seen and grid[nxt[1]][nxt[0]] == TILE_FLOOR:
                seen.add(nxt)
                queue.append(nxt)
    return False


def validate_config(raw):
    """
    Проверяет содержимое JSON и возвращает нормализованный словарь:
        grid (список списков 0/1), player_start, exit, time_limit, wall_shift_interval.
    При любой проблеме бросает ValueError с понятным описанием.
    Валидация нужна потому, что файл могли отредактировать вручную:
    неверный размер матрицы или выход внутри стены приведут к падению или
    к игре, которую невозможно пройти.
    """
    if not isinstance(raw, dict):
        raise ValueError("корень JSON должен быть объектом {...}")
    if "level" not in raw:
        raise ValueError("отсутствует обязательный ключ 'level'")

    # 1) матрица плиток: ровно GRID_ROWS строк по GRID_COLUMNS клеток, значения 0/1
    rows = raw["level"]
    if not isinstance(rows, list) or len(rows) != GRID_ROWS:
        raise ValueError(f"'level' должен содержать {GRID_ROWS} строк")
    grid = []
    for y, row in enumerate(rows):
        cells = list(row) if isinstance(row, str) else row     # "0110" или [0, 1, 1, 0]
        if not isinstance(cells, list) or len(cells) != GRID_COLUMNS:
            raise ValueError(f"'level'[{y}]: нужно {GRID_COLUMNS} клеток")
        try:
            parsed = [int(c) for c in cells]
        except (TypeError, ValueError):
            raise ValueError(f"'level'[{y}]: допустимы только значения 0 и 1")
        if any(v not in (TILE_FLOOR, TILE_WALL) for v in parsed):
            raise ValueError(f"'level'[{y}]: допустимы только значения 0 и 1")
        grid.append(parsed)

    # 2) внешняя рамка обязана быть стеной (она не двигается и не даёт выйти за поле)
    border_ok = (all(v == TILE_WALL for v in grid[0]) and all(v == TILE_WALL for v in grid[-1])
                 and all(r[0] == TILE_WALL and r[-1] == TILE_WALL for r in grid))
    if not border_ok:
        raise ValueError("внешняя рамка уровня должна состоять из стен (1)")

    # 3) старт и выход (необязательные ключи - берём значения по умолчанию)
    start = _parse_cell(raw.get("player_start", list(PLAYER_START)), "player_start", grid)
    goal = _parse_cell(raw.get("exit", list(EXIT_CELL)), "exit", grid)
    if start == goal:
        raise ValueError("старт и выход совпадают")
    if not _exit_reachable(grid, start, goal):
        raise ValueError("выход недостижим от стартовой клетки")

    # 4) числовые параметры
    time_limit = raw.get("time_limit", TIME_LIMIT)
    shift = raw.get("wall_shift_interval", WALL_SHIFT_INTERVAL)
    if not _is_number(time_limit) or time_limit <= 0:
        raise ValueError("'time_limit' должен быть положительным числом")
    if not _is_number(shift) or shift <= 0:
        raise ValueError("'wall_shift_interval' должен быть положительным числом")

    return {"grid": grid, "player_start": start, "exit": goal,
            "time_limit": time_limit, "wall_shift_interval": shift}


def load_level_config(path=LEVEL_FILE):
    """
    Читает level.json. Возвращает (config, warning).
    warning = None, если всё хорошо; иначе - текст проблемы, а config -
    уровень по умолчанию (игра не падает, а предупреждает игрока и пишет в лог).
    Порядок except важен: JSONDecodeError и UnicodeDecodeError - потомки
    ValueError, поэтому их нужно ловить раньше общего ValueError.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        config = validate_config(raw)
    except FileNotFoundError:
        warning = f"Файл {path.name} не найден. Используется уровень по умолчанию."
    except json.JSONDecodeError as e:
        warning = (f"Файл {path.name} повреждён (строка {e.lineno}, символ {e.colno}: {e.msg}). "
                   f"Используется уровень по умолчанию.")
    except UnicodeDecodeError:
        warning = f"Файл {path.name} не в кодировке UTF-8. Используется уровень по умолчанию."
    except ValueError as e:                      # не прошла validate_config
        warning = f"Ошибка в {path.name}: {e}. Используется уровень по умолчанию."
    except OSError as e:                         # нет прав, это папка и т.п.
        warning = f"Не удалось прочитать {path.name}: {e}. Используется уровень по умолчанию."
    else:
        game_log.log_event(f"Уровень загружен из {path.name}")
        return config, None

    print(warning)
    game_log.log_event(warning, logging.ERROR)
    return validate_config(DEFAULT_CONFIG), warning


# ---------------------------------------------------------------- рекорды (CSV)

def save_record(name, status, time_sec, shifts, path=RECORDS_FILE):
    """
    Дописывает результат в CSV. Первый запуск (файла нет или он пустой) -
    сначала пишется строка заголовков. Возвращает True/False (получилось ли).
    """
    try:
        is_new = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(RECORD_FIELDS)
            writer.writerow([name, status, round(time_sec, 1), shifts,
                             datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except OSError as e:
        game_log.log_event(f"Не удалось сохранить рекорд: {e}", logging.ERROR)
        print(f"Не удалось записать {path.name}: {e}")
        return False
    game_log.log_event(f"Рекорд сохранён: {name}, {status}, {round(time_sec, 1)} с")
    return True


def load_top_records(limit=RECORDS_TOP, path=RECORDS_FILE):
    """
    Возвращает до `limit` лучших ПОБЕД (самое быстрое время сверху) как
    список кортежей (имя, время, дата). Нет файла / файл повреждён -> [].
    Строки с неверными данными пропускаются, а не роняют игру.
    """
    if not path.exists():
        return []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        game_log.log_event(f"Не удалось прочитать рекорды: {e}", logging.ERROR)
        return []

    wins = []
    for row in rows:
        try:
            if row[F_STATUS] == STATUS_WIN:
                wins.append((row[F_NAME], float(row[F_TIME]), row[F_DATE]))
        except (KeyError, ValueError, TypeError):
            continue                              # битая строка - пропускаем
    wins.sort(key=lambda r: r[1])
    return wins[:limit]
