import pygame
from meta_parameters import *

# Feedback durations (in ms)
FEEDBACK_DURATION = 1000  # 1 second

# Feedback colors
GREEN_RGB = (0, 255, 0)
RED_RGB = (255, 0, 0)
YELLOW_RGB = (255, 255, 0)

# Show feedback (temporary placeholder - will be changed to use images later)
def show_feedback(screen, correct, timeout):
    font = pygame.font.SysFont(None, 72)
    
    if correct:
        text = font.render("Correct", True, GREEN_RGB)
    elif timeout:
        text = font.render("Too Slow", True, YELLOW_RGB)
    else:
        text = font.render("Incorrect", True, RED_RGB)
    
    screen.fill(GRAY_RGB)
    screen.blit(text, text.get_rect(center=screen.get_rect().center))
    pygame.display.flip()
    pygame.time.wait(FEEDBACK_DURATION)
