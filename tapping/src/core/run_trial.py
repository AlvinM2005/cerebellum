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
        key_was_pressed = False  # Track if key was pressed using key state
        
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

            if state.pressed: # Tapped (space)
                response_tick = pygame.time.get_ticks() - start_tick
                current_response = [state.pressed, response_tick]
                responded = True
                key_was_pressed = True
                valid_key_pressed_num += 1
                print(f"  -> {state.pressed} pressed at {response_tick} ms ({valid_key_pressed_num}/{max_key_press})")
            else:
                key_was_pressed = False
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

    # trial_type - only evaluate self-paced intervals, excluding the first self-paced tap
    trial_type = 1
    print()
    # Get self-paced intervals, excluding the first one (which is None)
    self_paced_intervals = intervals[-cfg.NUM_SELF_PACE:]
    # Remove the first interval (transition) from evaluation
    evaluation_intervals = [interval for interval in self_paced_intervals[1:] if interval is not None]
    logger.info("Self-paced intervals for evaluation:", evaluation_intervals)
    for interval in evaluation_intervals:
        if interval < MIN_SELF_PACED_INTERVAL or interval > MAX_SELF_PACED_INTERVAL:
            trial_type = 0
            logger.info(f"Interval {interval}ms is outside valid range [{MIN_SELF_PACED_INTERVAL}-{MAX_SELF_PACED_INTERVAL}]")
            break

    end_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Write one row per tap
    for i in range(len(response_ticks)):
        actual_key = key_responses[i] if key_responses[i] is not None else "FALSE"
        update_save(
            block=block,
            type=typeblock,
            starttime=start_time,
            endtime=end_time,
            correct=trial_type,
            key_corr=pygame.key.name(target_key),
            key_resp=actual_key,
            pace_ms=pace_ms,
            synch_sound_ticks=synchronized_sound_ticks[i] if synchronized_sound_ticks[i] is not None else "NA",
            response_ticks=response_ticks[i] if response_ticks[i] is not None else "NA",
            intervals=intervals[i] if intervals[i] is not None else "NA",
            trial=trial,
            tap_num=i + 1,
            tap_type=tap_types[i],
        )
    # Log result
    logger.info(
        "TRIAL_RESULT | block=%s | trial=%s | pace=%d | "
        "synchronized_sound_ticks=%.2f | response_ticks=%s | target_word=%s | response=%s | status=%s | reaction_time_ms=%d",
        block,
        trial,
        pace_ms,
        synchronized_sound_ticks[-1],
        response_ticks[-1],
        intervals[-1],
        trial_type,
        key_responses[-1],
        key_correct
    )

    # Restaurar feedback visual de Timeout en amarillo si no hubo respuesta
    # if option_selected is None:
    #     show_feedback(screen, "timeout")
    # else:
    #     show_feedback(screen, correct)
    pygame.display.flip()
    pygame.time.delay(cfg.FB_DURATION)
    _flush_input()

    return screen, trial_type
