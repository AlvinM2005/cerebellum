import pygame
import time
from meta_parameters import *

# Key logging
def key_logging(start_ticks, keypress_times):
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            print(f"Key pressed: {pygame.key.name(event.key)}")  # Debug: show any key press
            if event.key == pygame.K_SPACE:
                now = pygame.time.get_ticks()
                elapsed = now - start_ticks
                keypress_times.append(elapsed)
                print(f"[SPACE] pressed at {elapsed} ms (tap #{len(keypress_times)})")
                return True  # Return True when SPACE is pressed
    return False  # Return False when no ESC press detected

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
        # Add a title to make window more visible
        pygame.display.set_caption("Tapping Experiment - Synchronized Phase - Press SPACE to the rhythm")
        pygame.display.flip()
    
    time.sleep(1)

    # Continuous audio playback until 12 ESC presses
    target_taps = 12  # Always 12 taps regardless of MODE
    last_audio_time = pygame.time.get_ticks()
    
    print(f"Starting synchronized phase - press SPACE {target_taps} times to the rhythm")
    
    # Play first stimulus immediately
    stimulus.play()
    print(f"Audio stimulus #{len(keypress_times) + 1} played")
    
    # Main loop - continue until we get 12 ESC presses
    while len(keypress_times) < target_taps:
        current_time = pygame.time.get_ticks()
        
        # Check for key presses continuously
        key_logging(start_ticks, keypress_times)
        
        # Play audio stimulus every SYNCHRONIZED_INTERVAL ms
        if current_time - last_audio_time >= SYNCHRONIZED_INTERVAL:
            stimulus.play()
            last_audio_time = current_time
            print(f"Audio stimulus played (taps received: {len(keypress_times)}/{target_taps})")
        
        # Small delay to prevent excessive CPU usage
        pygame.time.wait(10)
    
    print(f"Synchronized sequence completed after {len(keypress_times)} taps.")
    print("Result: ", keypress_times)
    print()

    return keypress_times
