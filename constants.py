"""Все настройки игры в одном месте."""
from pathlib import Path

# --- Файлы (ЛР 2) ---
# Пути строим от папки проекта, а не от текущей директории запуска:
# так игра находит файлы одинаково на Windows, macOS и Linux.
BASE_DIR = Path(__file__).resolve().parent
LEVEL_FILE = BASE_DIR / "level.json"        # описание уровня (читаем)
LOG_FILE = BASE_DIR / "game_flight.log"     # «чёрный ящик» (дописываем)
RECORDS_FILE = BASE_DIR / "records.csv"     # таблица рекордов (дописываем)
LOG_LEVEL = "INFO"                          # "DEBUG" - дополнительно пишет каждый сдвиг стены

# --- Окно ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
TITLE = "Chronos Light - ЛР 2"

# --- Сетка ---
TILE_SIZE = 40
GRID_COLUMNS = WINDOW_WIDTH // TILE_SIZE    # 20
GRID_ROWS = WINDOW_HEIGHT // TILE_SIZE      # 15

# --- Тайлы ---
TILE_FLOOR = 0
TILE_WALL = 1

# Ниже - значения ПО УМОЛЧАНИЮ. Если в level.json нет ключей
# "time_limit" / "wall_shift_interval" / "player_start" / "exit", берутся они.

# --- Игрок ---
PLAYER_SIZE = 22
PLAYER_SPEED = 150          
PLAYER_START = (1, 1)       
EXIT_CELL = (18, 13)        

# --- Фонарик ---
LIGHT_HALF_ANGLE = 30       
LIGHT_RAY_COUNT = 61        
LIGHT_RANGE = 240           
LIGHT_STEP = 2              

# --- Стены ---
WALL_SHIFT_INTERVAL = 3.0  

# --- Игра ---
TIME_LIMIT = 90             

# --- Цвета ---
COLORS = {
    "bg": (0, 0, 0),
    "wall_lit": (255, 255, 255),
    "wall_debug": (60, 60, 60),
    "light": (255, 240, 150, 55),  
    "player": (40, 140, 255),
    "exit": (30, 160, 70),
    "text": (255, 255, 255),
    "warning": (255, 200, 60),
}

# --- Состояния ---
STATE_MENU = "MENU"
STATE_PLAY = "PLAY"
STATE_WIN = "WIN"
STATE_LOSE = "LOSE"
STATE_NAME = "NAME"          # ввод имени после игры
STATE_RECORDS = "RECORDS"    # таблица рекордов

# --- Рекорды ---
STATUS_WIN = "Победа"
STATUS_LOSE = "Поражение"
NAME_MAX_LEN = 16
RECORDS_TOP = 5