"""Алгоритм конуса света: лучи в секторе alpha +- 30 градусов."""
import math
from constants import *


def compute_light(level, px, py, alpha):
    """
    px, py - позиция игрока (пиксели), alpha - угол взгляда (радианы).
    Возвращает:
      lit_cells - множество клеток-стен, попавших под свет,
      polygon   - точки многоугольника освещённой зоны (для рисования).
    """
    lit_cells = set()
    polygon = [(px, py)]
    half = math.radians(LIGHT_HALF_ANGLE)

    for i in range(LIGHT_RAY_COUNT):
        
        t = i / (LIGHT_RAY_COUNT - 1)
        angle = alpha - half + t * 2 * half
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        end_x, end_y = px, py
        d = 0
        while d <= LIGHT_RANGE:
            x = px + cos_a * d            
            y = py + sin_a * d
            gx, gy = int(x) // TILE_SIZE, int(y) // TILE_SIZE
            end_x, end_y = x, y
            if level.is_wall(gx, gy):
                lit_cells.add((gx, gy))    
                break                    
            d += LIGHT_STEP
        polygon.append((end_x, end_y))

    return lit_cells, polygon