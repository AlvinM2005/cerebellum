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
        pygame.display.set_caption(f"Tapping Experiment - Self-Paced Phase - Press SPACE {NUM_SELF_PACED_TAPS} times at your own rhythm")
        pygame.display.flip()
    
    time.sleep(1)
    
    print(f"Starting self-paced phase - press SPACE {NUM_SELF_PACED_TAPS} times at your own rhythm")

    # Play the stimuli
    while len(keypress_times) < NUM_SELF_PACED_TAPS:
        key_logging(start_ticks, keypress_times)
        # Print progress every 5 taps
        if len(keypress_times) % 5 == 0 and len(keypress_times) > 0:
            print(f"Self-paced progress: {len(keypress_times)}/{NUM_SELF_PACED_TAPS} taps completed")

    print("Result: ", keypress_times)
    print("Self paced sequence completed.")
    print()

    return keypress_times
