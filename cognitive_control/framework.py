import pygame
from meta_parameters import *
from stimuli import *
from instructions import *

GlobalParticipantName = ""

# Toggle fullscreen function
def toggle_fullscreen(screen):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    screen_info = pygame.display.Info()

    if screen.get_flags() & pygame.FULLSCREEN:
        # Switch to windowed mode
        # Use 80% of screen size for windowed mode to ensure it fits
        window_width = int(screen_info.current_w * 0.8)
        window_height = int(screen_info.current_h * 0.8)

        # Ensure minimum size but not larger than screen
        SCREEN_WIDTH = max(1024, min(window_width, screen_info.current_w - 100))
        SCREEN_HEIGHT = max(768, min(window_height, screen_info.current_h - 100))

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Switched to windowed mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        # Switch to fullscreen mode
        SCREEN_WIDTH = screen_info.current_w
        SCREEN_HEIGHT = screen_info.current_h
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print(f"Switched to fullscreen mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Show Participant ID input page
def get_participant_id(screen):
    font = pygame.font.SysFont(None, 48)
    input_text = ""
    active = True

    global GlobalParticipantName

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
                if event.key == pygame.K_ESCAPE:
                    toggle_fullscreen(screen)
                elif event.key == pygame.K_RETURN and input_text != "":
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
    GlobalParticipantName = input_text
    print("entered participant ID:", GlobalParticipantName)
    return input_text

def GetParticipantId():
    return GlobalParticipantName

# Show one instruction page, then call next_func
def show_instruction(screen, instruction_page, next_func):
    screen.blit(instruction_page, (0, 0))
    pygame.display.flip()

    pygame.event.clear()
    page_start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - page_start_time < READ_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_fullscreen(screen)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_fullscreen(screen)
                elif event.key == pygame.K_SPACE:
                    waiting = False

    next_func()

# Reusable recursive flow handler
def run_instruction_sequence(screen, flow, all_results, all_acc, final_callback, index=0):
    if index >= len(flow):
        final_callback()
        return

    page, task_func = flow[index]

    def next_step():
        if task_func:
            results, acc = task_func(screen)
            all_results.extend(results)
            all_acc.append(acc)
        run_instruction_sequence(screen, flow, all_results, all_acc, final_callback, index + 1)

    show_instruction(screen, page, next_step)
