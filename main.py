
import sys
import logging
import pygame
from constants import *
from level import Level
from player import Player
from light import compute_light
import ui
import storage
import game_log


def new_game():
    """
    Level.json перечитывается при КАЖДОМ старте игры: файл можно править,
    не перезапуская программу. warning - текст проблемы (или None).
    """
    config, warning = storage.load_level_config()
    level = Level(config)
    return level, Player(*level.player_start), warning


def cell_of(point):
    return (point[0] // TILE_SIZE, point[1] // TILE_SIZE)


def finish_game(win, level, time_left, shifts):
    """Фиксирует итог партии: пишет в лог и возвращает данные для CSV."""
    elapsed = level.time_limit - max(time_left, 0)
    status = STATUS_WIN if win else STATUS_LOSE
    game_log.log_event(f"{status}: время {elapsed:.1f} с, сдвигов стен {shifts}")
    return {"status": status, "time": elapsed, "shifts": shifts}


def main():
    game_log.setup_logging()
    game_log.log_event("Игра запущена")

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    big_font = pygame.font.Font(None, 64)

    # уровень читаем сразу при старте: меню покажет предупреждение, если файл плохой
    config, config_warning = storage.load_level_config()
    menu_time_limit = config["time_limit"]

    state = STATE_MENU
    level = player = None
    lit_cells, polygon = set(), []
    time_left = menu_time_limit
    shifts = 0                  # сколько стен сдвинулось за партию
    last_cell = None            # для лога: пишем шаг, только когда клетка сменилась
    result = None               # итог партии для экрана имени и CSV
    player_name = ""
    records, records_note = [], ""
    debug = False
    dt = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_log.log_event("Игра закрыта")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    debug = not debug
                    game_log.log_event(f"Режим отладки: {'вкл' if debug else 'выкл'}")
                match state:
                    case "MENU":
                        if event.key == pygame.K_RETURN:
                            level, player, config_warning = new_game()
                            menu_time_limit = level.time_limit
                            time_left = level.time_limit
                            shifts = 0
                            last_cell = cell_of(player.center)
                            state = STATE_PLAY
                            game_log.log_event(
                                f"Новая игра: старт {level.player_start}, выход {level.exit_cell}, "
                                f"лимит {level.time_limit} с")
                        elif event.key == pygame.K_r:
                            records = storage.load_top_records()
                            records_note = ""
                            state = STATE_RECORDS
                    case "PLAY":
                        if event.key == pygame.K_ESCAPE:
                            game_log.log_event("Игра прервана игроком (ESC)")
                            state = STATE_MENU
                    case "WIN" | "LOSE":
                        if event.key == pygame.K_RETURN:
                            player_name = ""
                            state = STATE_NAME
                    case "NAME":
                        if event.key == pygame.K_RETURN:
                            name = player_name.strip() or "Аноним"
                            saved = storage.save_record(name, result["status"],
                                                        result["time"], result["shifts"])
                            records = storage.load_top_records()
                            records_note = "" if saved else "Не удалось сохранить результат (см. game_flight.log)"
                            state = STATE_RECORDS
                        elif event.key == pygame.K_ESCAPE:
                            game_log.log_event("Результат не сохранён (ESC)")
                            state = STATE_MENU
                        elif event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        elif event.unicode and event.unicode.isprintable() and len(player_name) < NAME_MAX_LEN:
                            player_name += event.unicode
                    case "RECORDS":
                        if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                            state = STATE_MENU


        if state == STATE_PLAY:
            time_left -= dt
            player.update(pygame.key.get_pressed(), pygame.mouse.get_pos(), level, dt)

            cell = cell_of(player.center)
            if cell != last_cell:                       # шаг игрока в лог
                game_log.log_event(f"Шаг игрока: клетка {cell}")
                last_cell = cell

            lit_cells, polygon = compute_light(level, *player.center, player.alpha)
            moved = level.update(dt, lit_cells, player.rect)
            shifts += len(moved)
            for src, dst in moved:                      # видно только при LOG_LEVEL = "DEBUG"
                game_log.log_event(f"Стена сдвинута {src} -> {dst}", logging.DEBUG)

            ex, ey = level.exit_cell
            exit_rect = pygame.Rect(ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player.rect.colliderect(exit_rect):
                state = STATE_WIN
                result = finish_game(True, level, time_left, shifts)
            elif time_left <= 0:
                state = STATE_LOSE
                result = finish_game(False, level, time_left, shifts)


        if state == STATE_MENU:
            ui.draw_menu(screen, font, big_font, small_font, menu_time_limit, config_warning)
        elif state == STATE_NAME:
            ui.draw_name_input(screen, font, big_font, player_name, result)
        elif state == STATE_RECORDS:
            ui.draw_records(screen, font, big_font, records, records_note)
        else:
            screen.fill(COLORS["bg"])

            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            if len(polygon) > 2:
                pygame.draw.polygon(overlay, COLORS["light"], polygon)
            screen.blit(overlay, (0, 0))
            level.draw(screen, lit_cells, debug)
            player.draw(screen)
            shadow = level.count_walls() - len(lit_cells)
            ui.draw_hud(screen, font, max(time_left, 0), shadow)
            if state in (STATE_WIN, STATE_LOSE):
                ui.draw_end(screen, font, big_font, state == STATE_WIN, time_left)

        pygame.display.flip()
        dt = clock.tick(FPS) / 1000.0       


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # необработанная ошибка тоже попадает в лог (с трассировкой), потом падаем как раньше
        game_log.log_exception("Необработанная ошибка")
        raise
