"""Лабиринт: матрица клеток и динамический сдвиг невидимых стен."""
import random
import pygame
from constants import *


DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Level:
    def __init__(self, config):
        """config - словарь, уже проверенный storage.validate_config()."""
        self.grid = [row[:] for row in config["grid"]]      # копия: игра меняет сетку
        self.player_start = config["player_start"]
        self.exit_cell = config["exit"]
        self.time_limit = config["time_limit"]
        self.wall_shift_interval = config["wall_shift_interval"]
        self.timers = {}


    def is_wall(self, gx, gy):
        if 0 <= gx < GRID_COLUMNS and 0 <= gy < GRID_ROWS:
            return self.grid[gy][gx] == TILE_WALL
        return True                      

    def is_movable_zone(self, gx, gy):
        """Внешняя рамка двигаться не может."""
        return 1 <= gx <= GRID_COLUMNS - 2 and 1 <= gy <= GRID_ROWS - 2

    def blocked(self, rect):

        corners = [(rect.left, rect.top), (rect.right - 1, rect.top),
                   (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1)]
        return any(self.is_wall(x // TILE_SIZE, y // TILE_SIZE) for x, y in corners)

    def count_walls(self):
        return sum(row.count(TILE_WALL) for row in self.grid)


    def _try_shift(self, gx, gy, player_rect):
     
        dirs = DIRECTIONS[:]
        random.shuffle(dirs)        
        for dx, dy in dirs:
            tx, ty = gx + dx, gy + dy
            if not self.is_movable_zone(tx, ty):
                continue                
            if self.grid[ty][tx] != TILE_FLOOR:
                continue                
            if (tx, ty) == self.exit_cell:
                continue                
            cell = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if cell.colliderect(player_rect):
                continue        
            self.grid[gy][gx] = TILE_FLOOR
            self.grid[ty][tx] = TILE_WALL
            return (tx, ty)
        return None              

    def update(self, dt, lit_cells, player_rect):
  

        walls = [(x, y) for y in range(1, GRID_ROWS - 1)
                 for x in range(1, GRID_COLUMNS - 1) if self.grid[y][x] == TILE_WALL]

        self.timers = {c: t for c, t in self.timers.items() if c in walls}
        moved = []                                           # [(откуда, куда), ...]

        for cell in walls:
            if cell in lit_cells:
                self.timers[cell] = 0.0                     
                continue
            self.timers[cell] = self.timers.get(cell, 0.0) + dt   
            if self.timers[cell] >= self.wall_shift_interval:
                new_cell = self._try_shift(cell[0], cell[1], player_rect)
                self.timers.pop(cell, None)
                if new_cell:
                    self.timers[new_cell] = 0.0
                    moved.append((cell, new_cell))
        return moved


    def draw(self, surface, lit_cells, debug=False):
        for (gx, gy) in lit_cells:                           
            r = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, COLORS["wall_lit"], r)
        if debug:                                        
            for y, row in enumerate(self.grid):
                for x, tile in enumerate(row):
                    if tile == TILE_WALL and (x, y) not in lit_cells:
                        r = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(surface, COLORS["wall_debug"], r)
        ex, ey = self.exit_cell                                   
        pygame.draw.rect(surface, COLORS["exit"],
                         (ex * TILE_SIZE + 6, ey * TILE_SIZE + 6, TILE_SIZE - 12, TILE_SIZE - 12))