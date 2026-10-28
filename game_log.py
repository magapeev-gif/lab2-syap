"""Логирование событий игры в файл game_flight.log («чёрный ящик»)."""
import logging
from constants import LOG_FILE, LOG_LEVEL

_logger = logging.getLogger("chronos")


def setup_logging():
    """
    Подключает запись в файл. Каждая строка лога:
        2026-03-05 14:21:07 | INFO | Шаг игрока: клетка (2, 1)
    Режим "a" - файл не затирается, записи дописываются в конец.
    FileHandler сбрасывает буфер после КАЖДОЙ записи, поэтому при аварийном
    завершении программы уже записанные события не теряются.
    Если файл недоступен для записи, игра не падает: лог просто отключается.
    """
    _logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    _logger.propagate = False
    try:
        handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    except OSError as e:
        print(f"Не удалось открыть лог-файл {LOG_FILE.name}: {e}. Логирование отключено.")
        _logger.addHandler(logging.NullHandler())
        return
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    _logger.addHandler(handler)


def log_event(message, level=logging.INFO):
    """Единая точка записи события (остальные модули не знают про logging)."""
    _logger.log(level, message)


def log_exception(message):
    """Пишет сообщение вместе с трассировкой ошибки (уровень ERROR)."""
    _logger.exception(message)
