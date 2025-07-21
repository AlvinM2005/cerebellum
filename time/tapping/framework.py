import pygame
from meta_parameters import *

# Get participant id
def get_participant_id(screen):
    font = pygame.font.SysFont(None, 48)
    input_text = ""
    active = True

    while active:
        screen.fill(GRAY_RGB)
        prompt = font.render("Enter Participant ID (press enter when completed):", True, BLACK_RGB)
        text_surface = font.render(input_text, True, BLACK_RGB)
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_text != "":
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

    return input_text