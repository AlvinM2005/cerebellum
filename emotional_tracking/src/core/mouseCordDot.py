import pygame
import random
import numpy as np
import pandas as pd
from pathlib import Path

class MouseCordDot:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.x = 0.0
        self.y = 0.0

    def set_pos(self, pos: tuple[float, float]):
        self.x, self.y = pos
        # Pixels run 0..w-1, so map [-1, 1] onto that range (the inverse of get_pos)
        w, h = self.screen.get_size()
        screen_x = round((self.x + 1) / 2 * (w - 1))
        screen_y = round((1 - (self.y + 1) / 2) * (h - 1))
        pygame.mouse.set_pos(screen_x, screen_y)

    def get_pos(self) -> tuple[float, float]:
        mx, my = pygame.mouse.get_pos()
        w, h = self.screen.get_size()
        # Divide by w-1 / h-1 (the last pixel index) so the far edges map to exactly -1 and 1
        self.x = (mx / (w - 1)) * 2 - 1
        self.y = 1 - (my / (h - 1)) * 2
        return (self.x, self.y)

    def clamp(self, limit: float = 0.4):
        x, y = self.get_pos()
        clamped_x = max(-limit, min(limit, x))
        clamped_y = max(-limit, min(limit, y))
        if clamped_x != x or clamped_y != y:
            self.set_pos((clamped_x, clamped_y))
        return (clamped_x, clamped_y)