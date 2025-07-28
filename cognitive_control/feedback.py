import pygame
import os
from meta_parameters import *

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get feedback icons
FEEDBACK_PATH = os.path.join(SCRIPT_DIR, "stimuli", "feedback") + os.sep

CORRECT_IMG_RAW = pygame.image.load(os.path.join(FEEDBACK_PATH, "feedback_correct.png"))
INCORRECT_IMG_RAW = pygame.image.load(os.path.join(FEEDBACK_PATH, "feedback_incorrect.png"))

CORRECT_IMG = pygame.transform.scale(CORRECT_IMG_RAW, (
    CORRECT_IMG_RAW.get_width() // 3,
    CORRECT_IMG_RAW.get_height() // 3
))
INCORRECT_IMG = pygame.transform.scale(INCORRECT_IMG_RAW, (
    INCORRECT_IMG_RAW.get_width() // 3,
    INCORRECT_IMG_RAW.get_height() // 3
))

# Show feedback (temporary placeholder - will be changed to use images later)
def show_feedback(screen, correct, timeout, background):
    font = pygame.font.SysFont(None, 72)
    screen_rect = screen.get_rect()

    center_x = screen_rect.centerx
    center_y = screen_rect.centery - 300

    screen.blit(background, (0, 0))
    
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
