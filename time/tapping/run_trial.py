import pygame
from framework import *
from synchronize import *
from self_pace import *

# Show welcome screen
def show_welcom_screen(screen):
    # Render welcome text
    font = pygame.font.SysFont(None, 60)
    welcome_text = font.render("Press [SPACE] to begin.", True, WHITE_RGB)
    text_rect = welcome_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    screen.fill(GRAY_RGB)
    screen.blit(welcome_text, text_rect)
    pygame.display.flip()

    # Press [SPACE] to continue
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Run trials
def run_trial(screen, start_ticks):
    # Show welcome screen
    show_welcom_screen(screen)

    # Run the synchronized sequence
    synchronized_results = run_synchronized_trial(start_ticks)

    # Show welcome screen
    pygame.event.clear()
    show_welcom_screen(screen)

    # Run the self paced sequence
    self_paced_results = run_self_paced_trial(start_ticks)

    return synchronized_results, self_paced_results
