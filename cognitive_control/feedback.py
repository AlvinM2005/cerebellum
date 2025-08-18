import pygame
import os
from meta_parameters import *

# Get feedback icons
script_dir = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_PATH = os.path.join(script_dir, "stimuli", "feedback")

CORRECT_IMG_RAW = pygame.image.load(os.path.join(FEEDBACK_PATH, "feedback_correct.png"))
INCORRECT_IMG_RAW = pygame.image.load(os.path.join(FEEDBACK_PATH, "feedback_incorrect.png"))

CORRECT_IMG = pygame.transform.smoothscale(CORRECT_IMG_RAW, (
    CORRECT_IMG_RAW.get_width() // 5,
    CORRECT_IMG_RAW.get_height() // 5
))
INCORRECT_IMG = pygame.transform.smoothscale(INCORRECT_IMG_RAW, (
    INCORRECT_IMG_RAW.get_width() // 5,
    INCORRECT_IMG_RAW.get_height() // 5
))

# Show feedback (temporary placeholder - will be changed to use images later)
def show_feedback(screen, correct, timeout, background):
    from framework import get_scaled_stimulus
    
    font = pygame.font.SysFont(None, 48)
    screen_rect = screen.get_rect()

    center_x = screen_rect.centerx
    center_y = screen_rect.centery + 200

    # Scale and center the background stimulus
    background_scaled = get_scaled_stimulus(background, screen)
    background_rect = background_scaled.get_rect(center=screen_rect.center)
    screen.blit(background_scaled, background_rect)
    
    if timeout:
        text = font.render("Too Slow", True, YELLOW_RGB)
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect)
    else:
        img = CORRECT_IMG if correct else INCORRECT_IMG
        img_rect = img.get_rect(center=(center_x, center_y))
        screen.blit(img, img_rect)
    
    pygame.display.flip()
    pygame.time.wait(FEEDBACK_DURATION)
