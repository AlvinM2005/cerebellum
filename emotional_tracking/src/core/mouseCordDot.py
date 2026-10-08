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
        screen_x = int((self.x + 1) / 2 * self.screen.get_width())
        screen_y = int((1 - (self.y + 1) / 2) * self.screen.get_height())
        pygame.mouse.set_pos(screen_x, screen_y)

    def get_pos(self) -> tuple[float, float]:
        mx, my = pygame.mouse.get_pos()
        w, h = self.screen.get_size()
        self.x = (mx / w) * 2 - 1
        self.y = 1 - (my / h) * 2
        return (self.x, self.y)

    def clamp(self, limit: float = 0.4):
        x, y = self.get_pos()
        clamped_x = max(-limit, min(limit, x))
        clamped_y = max(-limit, min(limit, y))
        if clamped_x != x or clamped_y != y:
            self.set_pos((clamped_x, clamped_y))
        return (clamped_x, clamped_y)