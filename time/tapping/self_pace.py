import pygame
import time
from meta_parameters import *
from synchronize import key_logging

# Run self paced sequence
def run_self_paced_trial(start_ticks):
    # Prepare for key loggings
    keypress_times = []

    # Create an empty screen
    screen = pygame.display.get_surface()  # Get current display surface
    if screen is not None:
        screen.fill(GRAY_RGB)
        pygame.display.flip()
    
    time.sleep(1)

    # Play the stimuli
    while len(keypress_times) < NUM_SYNCHRONIZED_TAPS:
        key_logging(start_ticks, keypress_times)

    print("Result: ", keypress_times)
    print("Self paced sequence completed.")
    print()

    return keypress_times
