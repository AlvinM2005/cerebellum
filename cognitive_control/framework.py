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

        new_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Switched to windowed mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        # Switch to fullscreen mode
        SCREEN_WIDTH = screen_info.current_w
        SCREEN_HEIGHT = screen_info.current_h
        new_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print(f"Switched to fullscreen mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    # Update the global screen reference and meta_parameters
    import framework
    framework.screen = new_screen
    import meta_parameters
    meta_parameters.SCREEN_WIDTH = SCREEN_WIDTH
    meta_parameters.SCREEN_HEIGHT = SCREEN_HEIGHT
    
    return new_screen

# Show Participant ID input page
def get_participant_id(screen):
    font = pygame.font.SysFont(None, 48)
    input_text = ""
    active = True

    global GlobalParticipantName

    while active:
        screen.fill(GRAY_RGB)
        screen_rect = screen.get_rect()
        
        prompt = font.render("Enter Participant ID (press enter when completed):", True, BLACK_RGB)
        text_surface = font.render(input_text, True, BLACK_RGB)
        
        # Center text using dynamic screen dimensions
        screen.blit(prompt, (screen_rect.centerx - prompt.get_width() // 2, screen_rect.centery - 100))
        screen.blit(text_surface, (screen_rect.centerx - text_surface.get_width() // 2, screen_rect.centery))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    screen = toggle_fullscreen(screen)
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

# Scale stimulus to fit screen while maintaining aspect ratio
def get_scaled_stimulus(image, screen):
    """
    Scale an image to fit within 90% of the screen size while maintaining aspect ratio.
    This ensures proper centering and display across different screen resolutions.
    """
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Target area is 90% of screen size
    target_width = int(screen_width * 0.9)
    target_height = int(screen_height * 0.9)
    
    # Get original image dimensions
    img_width = image.get_width()
    img_height = image.get_height()
    
    # Calculate scaling factor to fit within target area while maintaining aspect ratio
    scale_x = target_width / img_width
    scale_y = target_height / img_height
    scale_factor = min(scale_x, scale_y)
    
    # Calculate new dimensions
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)
    
    # Scale the image using smooth scaling to prevent pixelation
    scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
    
    return scaled_image

# Show instruction flow handler
def run_instruction_flow(screen, instruction_flow, all_results, all_acc, next_segment_func):
    """
    Handle a sequence of instructions and practice/block tasks
    instruction_flow: list of tuples (type, content) where type is "instruction" or "practice"/"block"
    """
    def process_flow(index):
        if index >= len(instruction_flow):
            next_segment_func()
            return
        
        flow_type, content = instruction_flow[index]
        
        if flow_type == "instruction":
            # Show instruction page
            show_instruction(screen, content, lambda: process_flow(index + 1))
        elif flow_type in ["practice", "block"]:
            # Run practice or block
            results, acc = content(screen)
            all_results.extend(results)
            all_acc.append(acc)
            process_flow(index + 1)
    
    process_flow(0)

# Show one instruction page, then call next_func
def show_instruction(screen, instruction_page, next_func):
    # Clear screen with gray background
    screen.fill(GRAY_RGB)
    
    # Scale instruction image to fit screen properly
    scaled_instruction = get_scaled_stimulus(instruction_page, screen)
    
    # Center the instruction on screen
    screen_rect = screen.get_rect()
    instruction_rect = scaled_instruction.get_rect(center=screen_rect.center)
    
    # Display the scaled and centered instruction
    screen.blit(scaled_instruction, instruction_rect)
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
                    screen = toggle_fullscreen(screen)
                    # Redraw instruction after screen change
                    screen.fill(GRAY_RGB)
                    scaled_instruction = get_scaled_stimulus(instruction_page, screen)
                    screen_rect = screen.get_rect()
                    instruction_rect = scaled_instruction.get_rect(center=screen_rect.center)
                    screen.blit(scaled_instruction, instruction_rect)
                    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    screen = toggle_fullscreen(screen)
                    # Redraw instruction after screen change
                    screen.fill(GRAY_RGB)
                    scaled_instruction = get_scaled_stimulus(instruction_page, screen)
                    screen_rect = screen.get_rect()
                    instruction_rect = scaled_instruction.get_rect(center=screen_rect.center)
                    screen.blit(scaled_instruction, instruction_rect)
                    pygame.display.flip()
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
