import pygame
from meta_parameters import *

# Key to string (conversion for readability)
def key_to_str(key):
    if key is None:
        return None
    elif key == pygame.K_v:
        return "v"
    elif key == pygame.K_m:
        return "m"
    elif key == pygame.K_d:
        return "d"
    elif key == pygame.K_k:
        return "k"
    elif key == pygame.K_g:
        return "g"
    elif key == pygame.K_SPACE:
        return "space"
    elif key == pygame.K_RETURN:
        return "return"
    else:
        return str(key)

# Toggle fullscreen function
def toggle_fullscreen(screen_param):
    """Toggle between fullscreen and windowed mode"""
    # Import the global variables from main
    import main
    screen_info = pygame.display.Info()

    if screen_param.get_flags() & pygame.FULLSCREEN:
        # Switch to windowed mode
        # Use 80% of screen size for windowed mode to ensure it fits
        window_width = int(screen_info.current_w * 0.8)
        window_height = int(screen_info.current_h * 0.8)

        # Ensure minimum size but not larger than screen
        main.SCREEN_WIDTH = max(1024, min(window_width, screen_info.current_w - 100))
        main.SCREEN_HEIGHT = max(768, min(window_height, screen_info.current_h - 100))

        main.screen = pygame.display.set_mode((main.SCREEN_WIDTH, main.SCREEN_HEIGHT))
        print(f"Switched to windowed mode: {main.SCREEN_WIDTH}x{main.SCREEN_HEIGHT}")
    else:
        # Switch to fullscreen mode
        main.SCREEN_WIDTH = screen_info.current_w
        main.SCREEN_HEIGHT = screen_info.current_h
        main.screen = pygame.display.set_mode((main.SCREEN_WIDTH, main.SCREEN_HEIGHT), pygame.FULLSCREEN)
        print(f"Switched to fullscreen mode: {main.SCREEN_WIDTH}x{main.SCREEN_HEIGHT}")
    
    return main.screen

# Show instruction
def show_next_page(screen, instruction_path, func=None, times=None):
    # Display the instruction
    image = pygame.image.load(instruction_path)
    screen.fill((128, 128, 128))  # Fill with gray background
    
    # Center the image on screen
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    img_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(image, img_rect)
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

# Show Participant ID input page
def get_participant_id(screen):
    font = pygame.font.SysFont(None, 48)
    input_text = ""
    active = True
    
    # Get current screen dimensions
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    while active:
        screen.fill(GRAY_RGB)
        prompt = font.render("Enter Participant ID (press enter when completed):", True, BLACK_RGB)
        text_surface = font.render(input_text, True, BLACK_RGB)
        screen.blit(prompt, (screen_width // 2 - prompt.get_width() // 2, screen_height // 2 - 100))
        screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, screen_height // 2))
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
                elif event.key == pygame.K_ESCAPE:
                    toggle_fullscreen(screen)
                else:
                    input_text += event.unicode

    return input_text
