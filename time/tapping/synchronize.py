import pygame
import time
from meta_parameters import *

# Key logging
def key_logging(start_ticks, keypress_times):
    responded = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif responded == False and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            now = pygame.time.get_ticks()
            elapsed = now - start_ticks
            keypress_times.append(elapsed)
            print(f"[SPACE] pressed at {elapsed} ms")
            responded = True

# Run synchronized sequence
def run_synchronized_trial(start_ticks):
    # Initialize mixer
    pygame.mixer.init()

    # Load stimulus
    stimulus = pygame.mixer.Sound(STIMULI_PATH)

    # Prepare for key loggings
    keypress_times = []

    # Create an empty screen
    screen = pygame.display.get_surface()  # Get current display surface
    if screen is not None:
        screen.fill(GRAY_RGB)
        pygame.display.flip()
    
    time.sleep(1)

    # Play the stimuli
    for _ in range(NUM_SYNCHRONIZED_TAPS):
        stimulus.play()
        temp = len(keypress_times)
        key_logging(start_ticks, keypress_times)
        if len(keypress_times) == temp:
            keypress_times.append(None)
            print("No response")
        time.sleep(SYNCHRONIZED_INTERVAL / 1000.0)  # Convert ms to seconds

    print("Result: ", keypress_times)
    print("Synchronized sequence completed.")
    print()

    return keypress_times
