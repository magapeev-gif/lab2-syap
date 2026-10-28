"""Игрок: движение по WASD и угол взгляда по мыши."""
import math
import pygame
from constants import *


class Player:
    def __init__(self, gx, gy):
   
        self.x = gx * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) / 2
        self.y = gy * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) / 2
        self.rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
        self.alpha = 0.0                  

    @property
    def center(self):
        return self.rect.center

    def update(self, keys, mouse_pos, level, dt):

        cx, cy = self.center
        self.alpha = math.atan2(mouse_pos[1] - cy, mouse_pos[0] - cx)

        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        if dx and dy:                     
            dx *= 0.7071
            dy *= 0.7071

        self._move(dx * PLAYER_SPEED * dt, 0, level)
        self._move(0, dy * PLAYER_SPEED * dt, level)

    def _move(self, dx, dy, level):
        nx, ny = self.x + dx, self.y + dy
        test = pygame.Rect(int(nx), int(ny), PLAYER_SIZE, PLAYER_SIZE)
        if not level.blocked(test):     
            self.x, self.y = nx, ny
            self.rect = test

    def draw(self, surface):
        pygame.draw.circle(surface, COLORS["player"], self.rect.center, PLAYER_SIZE // 2)

        cx, cy = self.rect.center
        tip = (cx + math.cos(self.alpha) * 18, cy + math.sin(self.alpha) * 18)
        pygame.draw.line(surface, COLORS["text"], (cx, cy), tip, 2)