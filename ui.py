"""Интерфейс: меню, HUD, экраны победы/поражения, ввод имени, таблица рекордов."""
import textwrap
import pygame
from constants import *


def _center(surface, font, text, y, color=None):
    img = font.render(text, True, color or COLORS["text"])
    surface.blit(img, img.get_rect(center=(WINDOW_WIDTH // 2, y)))


def draw_menu(surface, font, big_font, small_font, time_limit, warning=None):
    surface.fill(COLORS["bg"])
    _center(surface, big_font, "CHRONOS LIGHT", 170)
    _center(surface, font, "Лабиринт тёмен. Стены двигаются, пока на них не падает свет.", 250)
    _center(surface, font, "WASD - движение, мышь - направление фонарика", 290)
    _center(surface, font, f"Дойдите до зелёного выхода за {int(time_limit)} секунд", 330)
    _center(surface, font, "F1 - показать тёмные стены (отладка)   ENTER - старт", 400)
    _center(surface, font, "R - таблица рекордов", 435)
    if warning:                                   # проблема с level.json (см. storage.py)
        for i, line in enumerate(textwrap.wrap(warning, 80)):
            _center(surface, small_font, line, 510 + i * 22, COLORS["warning"])


def draw_hud(surface, font, time_left, shadow_count):
    text = f"Время: {int(time_left)}с    Стен в тени: {shadow_count}"
    surface.blit(font.render(text, True, COLORS["text"]), (10, 8))


def draw_end(surface, font, big_font, win, time_left):

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    _center(surface, big_font, "ВЫ ВЫБРАЛИСЬ!" if win else "ВРЕМЯ ВЫШЛО", 250)
    if win:
        _center(surface, font, f"Осталось времени: {int(time_left)}с", 310)
    _center(surface, font, "ENTER - ввести имя и сохранить результат", 370)


def draw_name_input(surface, font, big_font, name, result):
    """Экран ввода имени. result = {"status", "time", "shifts"}."""
    surface.fill(COLORS["bg"])
    _center(surface, big_font, "ВВЕДИТЕ ИМЯ", 170)
    _center(surface, font, f"{result['status']}. Время: {result['time']:.1f} с", 250)
    box = pygame.Rect(0, 0, 360, 44)
    box.center = (WINDOW_WIDTH // 2, 320)
    pygame.draw.rect(surface, COLORS["text"], box, 2)
    blink = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "     # мигающий курсор
    _center(surface, font, name + blink, 320)
    _center(surface, font, "ENTER - сохранить   ESC - не сохранять", 400)


def draw_records(surface, font, big_font, records, note=""):
    """records - список (имя, время, дата) из storage.load_top_records()."""
    surface.fill(COLORS["bg"])
    _center(surface, big_font, "РЕКОРДЫ", 100)
    if not records:
        _center(surface, font, "Пока нет сохранённых побед", 250)
    for i, (name, time_sec, date) in enumerate(records, start=1):
        y = 190 + (i - 1) * 40
        surface.blit(font.render(f"{i}. {name}", True, COLORS["text"]), (160, y))
        surface.blit(font.render(f"{time_sec:.1f} с", True, COLORS["text"]), (460, y))
        surface.blit(font.render(date, True, COLORS["text"]), (560, y))
    if note:
        _center(surface, font, note, 470, COLORS["warning"])
    _center(surface, font, "ENTER - в меню", 540)
