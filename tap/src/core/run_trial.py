import csv
import os.path
import datetime

import pygame
import time
import utils.config as cfg
import utils.paths as path
from utils.config import *
from ui.pygame_render import *
from utils.event_handler import EventHandler
from ui.pygame_render import (
    toggle_full_screen,
    show_feedback,
)
from core.saves import update_save

def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()

# Run synchronized sequence
def run_synchronized(screen, start_tick, target_key, max_key_press, stimulus_path, event_handler:EventHandler):
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
        
        # Listen to keyboard input for exactly 600ms with improved event handling
        
        while pygame.time.get_ticks() - current_sound_tick < SYNCHRONIZED_INTERVAL:

            state = event_handler.poll()
            
            if state.quit:
                pygame.quit()
                raise SystemExit
            
            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _flush_input()

            # Count at most one tap per tone window to avoid accidental double-count
            # (e.g., key-repeat/duplicate KEYDOWN events in the same 550 ms window).
            if state.pressed and not responded: # Tapped (space)
                response_tick = pygame.time.get_ticks() - start_tick
                current_response = [state.pressed, response_tick]
                responded = True
                valid_key_pressed_num += 1
                print(f"  -> {state.pressed} pressed at {response_tick} ms ({valid_key_pressed_num}/{max_key_press})")
            pygame.time.wait(1)
        
        # Always add exactly one response per sound
        key_responses.append(current_response)
        if not responded:
            print(f"  -> No response detected for sound {sound_index}")

    pygame.time.delay(10) # Prevent CPU overuse

    return sound_ticks, key_responses

# Run self-paced sequence
def run_self_paced(screen, start_tick, target_key, max_key_press, event_handler:EventHandler):
    last_tick = start_tick
    key_responses = []
    self_paced_start_tick = pygame.time.get_ticks()  # Record start of self-paced phase

    while len(key_responses) < max_key_press:
        # Check timeout only in ACTUAL mode
        if MODE == "ACTUAL":
            elapsed_time = pygame.time.get_ticks() - self_paced_start_tick
            if elapsed_time >= SELF_PACED_TIMEOUT:
                print(f"Self-paced phase timed out after {elapsed_time}ms (limit: {SELF_PACED_TIMEOUT}ms)")
                print(f"Completed {len(key_responses)}/{max_key_press} taps before timeout")
                break

        state = event_handler.poll()
        response_tick = pygame.time.get_ticks() - start_tick
            
        if state.quit:
            pygame.quit()
            raise SystemExit
        
        if state.toggle_full_screen:
            pygame.event.clear()
            screen = toggle_full_screen(screen)
            pygame.event.clear()
            _flush_input()

        if state.pressed and response_tick - last_tick > TREMOR_INTERVAL: # Tapped (space)
            last_tick = response_tick
            key_responses.append([state.pressed, response_tick])
            print(f"{state.pressed} pressed at {response_tick} ms ({len(key_responses)}/{max_key_press})")
        
    pygame.time.delay(10) # Prevent CPU overuse

    return key_responses

# Run trial (synchronized + self-paced)
def run_trial(screen, start_tick, target_key, max_synchronized_key_press, max_self_paced_key_press, stimulus_path, event_handler:EventHandler):
    synchronized_sound_ticks, synchronized_key_responses = run_synchronized(screen, start_tick, target_key, max_synchronized_key_press, stimulus_path,event_handler=event_handler,)
    self_paced_key_responses = run_self_paced(screen, start_tick, target_key, max_self_paced_key_press, event_handler=event_handler)
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

def single_trial(
        screen:pygame.Surface,
        block: str,
        start_tick: int,
        typeblock: str,
        target_key: pygame.key,
        trial,
        event_handler: EventHandler,
    ) -> pygame.Surface:
    screen.fill(BLACK_RGB)
    pygame.display.flip()
    start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pace_ms = SYNCHRONIZED_INTERVAL # pace_ms
    key_correct = target_key

    # Run trial
    (synchronized_sound_ticks, 
     synchronized_key_responses, 
     self_paced_key_responses) = run_trial(screen,
                                           start_tick, 
                                           target_key,
                                           cfg.NUM_SYNCHRONIZED, 
                                           cfg.NUM_SELF_PACE, 
                                           paths.STIMULUS_PATH_1000,
                                           event_handler)
    
    # Write trial results
    assert len(synchronized_sound_ticks) == len(synchronized_key_responses)
    
    # type
    tap_types = (["synchronized"] * len(synchronized_key_responses) +
                 ["self_paced"] * len(self_paced_key_responses))

    # synchrnoized_sound_tick_ms
    synchronized_sound_ticks += [None] * len(self_paced_key_responses)
    
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

    # Compute trial_outcome based on self-paced unguided IRIs (275-825 ms inclusive)
    # A trial is "valid" if every self-paced IRI (excluding the first transition) falls in [275, 825]
    self_paced_start_idx = len(synchronized_key_responses)
    self_paced_intervals = intervals[self_paced_start_idx:]
    # Skip the first self-paced interval (transition) and filter out None values
    unguided_iris = [iri for iri in self_paced_intervals[1:] if iri is not None]
    
    trial_outcome_value = "valid"
    trial_type = 1  # 1 = successful, 0 = unsuccessful
    for iri in unguided_iris:
        if iri < 275 or iri > 825:
            trial_outcome_value = "invalid"
            trial_type = 0
            break

    end_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Compute tap_num per block: only count actual responses, restart numbering per block
    # We'll track a per-block counter externally, but for now we use a simple approach:
    # tap_num is sequential within each trial, starting from 1, but NA when response is None
    tap_counter = 0
    
    # Write one row per tap
    for i in range(len(response_ticks)):
        actual_key = key_responses[i] if key_responses[i] is not None else "FALSE"
        
        # Compute tap_num: only increment for actual responses
        if key_responses[i] is not None:
            tap_counter += 1
            tap_num_value = tap_counter
        else:
            tap_num_value = "NA"
        
        # Compute row-level trial_outcome: applies to entire trial, not individual taps
        # But we include it in every row for the trial
        update_save(
            block=block,
            type=typeblock,
            starttime=start_time,
            endtime=end_time,
            correct=trial_type,
            key_corr=pygame.key.name(target_key),
            key_resp=actual_key,
            pace_ms=pace_ms,
            synch_sound_ticks=synchronized_sound_ticks[i],
            response_ticks=response_ticks[i],
            intervals=intervals[i],
            trial=trial,
            tap_num=tap_num_value,
            tap_type=tap_types[i],
            trial_outcome=trial_outcome_value,
        )
    # Log result
    logger.info(
        "TRIAL_RESULT | block=%s | trial=%s | trial_type=%s | trial_outcome=%s | num_taps=%d",
        block,
        trial,
        trial_type,
        trial_outcome_value,
        len([r for r in key_responses if r is not None])
    )

    pygame.display.flip()
    pygame.time.delay(cfg.FB_DURATION)
    _flush_input()

    return screen, trial_type
