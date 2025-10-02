import csv
import os.path
from datetime import datetime

import pygame
import time
from meta_parameters import *
from stimuli import *
from framework import *


# Run synchronized sequence
def run_synchronized(screen, start_tick, target_key, max_key_press, stimulus_path):
    pygame.event.clear()
    time.sleep(1) # Delay for 1 second before playing the first sound (for participants to prepare)

    sound_ticks = []
    key_responses = []
    valid_key_pressed_num = 0
    sound_index = 0

    while valid_key_pressed_num < max_key_press:
        sound_index += 1
        
        # Play sound
        stimulus = pygame.mixer.Sound(stimulus_path)
        stimulus.play()
        current_sound_tick = pygame.time.get_ticks()
        sound_ticks.append(current_sound_tick - start_tick)
        print(f"\nSound {sound_index} played at {current_sound_tick - start_tick} ms")

        responded = False
        current_response = [None, None]
        key_was_pressed = False  # Track if key was pressed using key state
        
        # Listen to keyboard input for exactly 600ms with improved event handling
        while pygame.time.get_ticks() - current_sound_tick < SYNCHRONIZED_INTERVAL:
            # Process all pending events in queue
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        toggle_fullscreen(screen)
                    elif event.key == target_key and responded == False:
                        response_tick = pygame.time.get_ticks() - start_tick
                        key_pressed = key_to_str(event.key)
                        current_response = [key_pressed, response_tick]
                        responded = True
                        valid_key_pressed_num += 1
                        print(f"  -> {key_pressed} pressed at {response_tick} ms ({valid_key_pressed_num}/{max_key_press})")
            
            # Also check keyboard state as backup method
            if not responded:
                keys = pygame.key.get_pressed()
                if keys[target_key] and not key_was_pressed:
                    response_tick = pygame.time.get_ticks() - start_tick
                    key_pressed = key_to_str(target_key)
                    current_response = [key_pressed, response_tick]
                    responded = True
                    valid_key_pressed_num += 1
                    key_was_pressed = True
                    print(f"  -> {key_pressed} pressed at {response_tick} ms (via key state) ({valid_key_pressed_num}/{max_key_press})")
                elif not keys[target_key]:
                    key_was_pressed = False
            
            # Small delay to prevent excessive CPU usage while maintaining responsiveness
            pygame.time.wait(1)
        
        # Always add exactly one response per sound
        key_responses.append(current_response)
        if not responded:
            print(f"  -> No response detected for sound {sound_index}")

    pygame.time.delay(10) # Prevent CPU overuse

    return sound_ticks, key_responses

# Run self-paced sequence
def run_self_paced(screen, start_tick, target_key, max_key_press):
    last_tick = start_tick
    key_responses = []

    while len(key_responses) < max_key_press:
        for event in pygame.event.get():
            response_tick = pygame.time.get_ticks() - start_tick
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_fullscreen(screen)
                elif event.key == target_key and response_tick - last_tick > TREMOR_INTERVAL:
                    last_tick = response_tick
                    key_pressed = key_to_str(event.key)
                    key_responses.append([key_pressed, response_tick])
                    print(f"{key_pressed} pressed at {response_tick} ms ({len(key_responses)}/{max_key_press})")

    pygame.time.delay(10) # Prevent CPU overuse

    return key_responses

# Run trial (synchronized + self-paced)
def run_trial(screen, start_tick, target_key, max_synchronized_key_press, max_self_paced_key_press, stimulus_path):
    synchronized_sound_ticks, synchronized_key_responses = run_synchronized(screen, start_tick, target_key, max_synchronized_key_press, stimulus_path)
    self_paced_key_responses = run_self_paced(screen, start_tick, target_key, max_self_paced_key_press)
    return synchronized_sound_ticks, synchronized_key_responses, self_paced_key_responses

'''
=== Result Format ===
[block, trial, tap_num, type, pace_ms, synchronized_sound_ticks_ms, key_response, response_tick_ms, interval_ms, trial_type, key_correct, group]
- block: section name (practice / block)
- trial: the i-th trial (counting from the beginning)
- tap_num: the i-th tapping (counting from the beginning) = row index
- type: synchronized / self-paced
- pace_ms: = SYNCHRONIZED_INTERVAL (in milliseconds)
- synchronized_sound_ticks_ms:
    - [For (type == synchronized)] time tick when the stimulus beep-sound is played (counting from the global start time tick, in milliseconds)
    - [For (type == self_paced)] "v" / "m" = key_correct
- key_response:
    - [For (type == synchronized)] key pressed during given trial (could be None)
    - [For (type == self_paced)] "v"
- response_tick_ms:
    - [For (type == synchronized && synchronized_key_response is not None)] time tick when key is pressed (counting from the global start time tick, in milliseconds)
    - [For (type == synchronized && synchronized_key_response is None)] = synchronized_sound_ticks
    - [For (type == self_paced)] time tick when key is pressed (counting from the global start time tick, in milliseconds)
- interval_ms: time difference between two key presses (in milliseconds)
- trial_type: "Successful" (if all interval_ms of self-paced tappings in given trials is in [MIN_SELF_PACED_INTERVAL, MAX_SELF_PACED_INTERVAL]) / "Unsuccessful" (otherwise)
- key_correct: "v" / "m"
- group: i.e. YC / CD [first two text of participant_id]
'''

def single_trail(screen, block, start_tick, target_key, results, participant_id, trial = None, csv_file = None):
    screen.fill(GRAY_RGB)
    pygame.display.flip()
    start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # block = "practice1" # block
    pace_ms = SYNCHRONIZED_INTERVAL # pace_ms
    key_correct = key_to_str(target_key)

    # Run trial
    (synchronized_sound_ticks, 
     synchronized_key_responses, 
     self_paced_key_responses) = run_trial(screen,
                                           start_tick, 
                                           target_key,
                                           NUM_SYNCHRONIZED, 
                                           NUM_SELF_PACE, 
                                           STIMULUS_PATH_1000)
    
    # Write trial results
    assert len(synchronized_sound_ticks) == len(synchronized_key_responses)
    
    # type
    type = (["synchronized" for i in range(len(synchronized_key_responses))] + 
            ["self_paced" for i in range(len(self_paced_key_responses))])
    
    # synchrnoized_sound_tick_ms
    synchronized_sound_ticks += [None for i in range(len(self_paced_key_responses))]
    
    # key_response
    key_responses = ([response[0] for response in synchronized_key_responses] + 
                        [response[0] for response in self_paced_key_responses])
    
    # response_tick_ms
    response_ticks = ([response[1] for response in synchronized_key_responses] + 
                        [response[1] for response in self_paced_key_responses])
    
    assert len(synchronized_sound_ticks) == len(response_ticks)
    assert len(key_responses) == len(response_ticks)

    # interval_ms
    intervals = [None]
    for i in range(1, len(response_ticks)):
        if response_ticks[i] is not None and response_ticks[i-1] is not None:
            # Check if this is the first self-paced tap (transition from synchronized to self-paced)
            # The first self-paced tap starts at index len(synchronized_key_responses)
            if i == len(synchronized_key_responses):
                # This is the transition from synchronized to self-paced - don't calculate interval
                intervals.append(None)
            else:
                intervals.append(response_ticks[i] - response_ticks[i-1])
        else:
            intervals.append(None)

    # trial_type - only evaluate self-paced intervals, excluding the first self-paced tap
    trial_type = "Successful"
    print()
    # Get self-paced intervals, excluding the first one (which is None)
    self_paced_intervals = intervals[-NUM_SELF_PACE:]
    # Remove the first interval (transition) from evaluation
    evaluation_intervals = [interval for interval in self_paced_intervals[1:] if interval is not None]
    print("Self-paced intervals for evaluation:", evaluation_intervals)
    for interval in evaluation_intervals:
        if interval < MIN_SELF_PACED_INTERVAL or interval > MAX_SELF_PACED_INTERVAL:
            trial_type = "Unsuccessful"
            print(f"Interval {interval}ms is outside valid range [{MIN_SELF_PACED_INTERVAL}-{MAX_SELF_PACED_INTERVAL}]")
            break

    end_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for i in range(len(response_ticks)):
        # Extract the actual key pressed (or empty string if none)
        actual_key_pressed = key_responses[i] if key_responses[i] is not None else ""
        
        single_trail_result = [participant_id, participant_id[0:2], block, trial, len(results) + 1, type[i], pace_ms, type[i], pace_ms, os.path.abspath(STIMULUS_PATH_1000),
                               synchronized_sound_ticks[i], response_ticks[i], intervals[i], trial_type, actual_key_pressed, key_correct, start_time, end_time]
        results.append(single_trail_result)
        if csv_file is not None:
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(single_trail_result)