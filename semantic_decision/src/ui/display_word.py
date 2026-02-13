"""
RSVP word presentation utilities.
"""

import pygame
import utils.config as cfg


pygame.font.init

def show_word(screen: pygame.Surface, word: str, is_target: bool = False) -> None:
    """
    Display a single word centered on the screen.
    
    :param screen: Current display surface
    :param word: Word to display
    :param is_target: Whether this is the target word (can be styled differently)
    """
    screen.fill(cfg.BLACK_RGB)
 
    font = pygame.font.Font(cfg.FONT, 64)
    text_surface = font.render(word, True, cfg.WHITE_RGB)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

6
def show_fixation(screen: pygame.Surface) -> None:
    """
    Display fixation cross centered on screen.
    
    :param screen: Current display surface
    """
    screen.fill(cfg.BLACK_RGB)
    
    font = pygame.font.Font(cfg.FONT, 72)
    text_surface = font.render("+", True, cfg.WHITE_RGB)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    screen.blit(text_surface, text_rect)
    pygame.display.flip()