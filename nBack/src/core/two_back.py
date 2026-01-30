# ./src/core/test.py
"""
Practice block execution logic using pygame.

This module presents randomized stimulus blocks, collects keyboard responses with timeout handling, and optionally displays feedback during practice trials.
"""


from __future__ import annotations
from pathlib import Path
import pygame
import random
import math

import utils.config as cfg
from utils.paths import STIM_BG, STIMULI
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import (
    toggle_full_screen,
    place_image,
    show_feedback,
    _play_beep
)
from utils.saves import update_save


logger = get_logger("./src/core/two_back")


def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _construct_stimuli_seuqnece() -> list[Path]:
    """
    Construct a stimulus sequence for 1back
    
    :return: A list of stimuli representing the full stimulus sequence
    :rtype: list[pathlib.Path]
    """
    valid = False
    limit = cfg.run_limit
    run = 0

    while not valid and run < limit:
        consecutive_same_stim_count = 0
        
        match_count = math.floor(cfg.STIM_COUNT * 0.3)
        match_pos = random.sample(range(cfg.STIM_COUNT), match_count)
        match_map = [(i in match_pos) for i in range(cfg.STIM_COUNT)]

        dummy_count = 2
        stim_seq = random.sample(STIMULI, dummy_count)

        for match in match_map:
            if match:
                stim_seq.append(stim_seq[-dummy_count])
            else:
                non_match_stim = [stim for stim in STIMULI if stim != stim_seq[-dummy_count]]
                stim_seq.append(random.choice(non_match_stim))
        
        for i in range(1, len(stim_seq)):
            if stim_seq[i] == stim_seq[i-1]:
                consecutive_same_stim_count += 1
                if consecutive_same_stim_count > 2: #at most 3 consecutive strimuli can be the same
                    break
            else:
                consecutive_same_stim_count = 0
        
        if consecutive_same_stim_count <= 2:
            valid = True
        else:
            run += 1
    
    if run == limit:
        logger.warning(f"Not an optimal stimuli sequence")
    
    return match_map, stim_seq


_match_map, _stim_seq = _construct_stimuli_seuqnece()

logger.info(f"Match map: {_match_map}")
logger.info(f"Stimuli Sequence: {_stim_seq}")


def run_2back(
    screen: pygame.Surface,
    phase: str,
    condition: str,
    _is_practice: bool,
    event_handler: EventHandler,
) -> pygame.Surface:
    """
    Run a stimulus block once (each stimulus exactly once, randomized order).

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param phase: Name of the phase
    :type phase: str

    :param condition: Name of the condition
    :type condition: str

    :param _is_practice: True = Practice / False = Test
    :type _is_practice: bool

    :param event_handler: Centralized event handler instance
    :type event_handler: EventHandler

    :return: Active display surface after the block (may be updated by fullscreen toggle)
    :rtype: pygame.Surface
    """

    for i in range(len(_stim_seq)):
        stim_path = _stim_seq[i]
        stim_id = str(stim_path.stem)
        if i == 0 or i == 1:
            match = None
        else:
            match = _match_map[i-2]

        # Stimulus
        place_image(screen, STIM_BG)
        place_image(screen, stim_path, None, (cfg.STIM_W, cfg.STIM_H))
        pygame.display.flip()
        _flush_input()

        total_window = cfg.STIM_DISPLAY_TIME + cfg.ISI
        phase_state = "stim"  # "stim" or "isi"

        t0 = pygame.time.get_ticks()
        reaction_time = total_window
        option_selected: int | None = None
        result = "timeout"

        while True:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            elapsed = pygame.time.get_ticks() - t0

            # Clear screen when stimulus display ends
            if phase_state == "stim" and elapsed >= cfg.STIM_DISPLAY_TIME:
                screen.fill(cfg.GRAY_RGB)
                pygame.display.flip()
                _flush_input()
                phase_state = "isi"
            
            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()

                if phase_state == "stim":
                    place_image(screen, STIM_BG)
                    place_image(screen, stim_path, None, (cfg.STIM_W, cfg.STIM_H))
                else:
                    screen.fill(cfg.GRAY_RGB)

                pygame.display.flip()
                _flush_input()

            if state.option_1:
                _play_beep()
                option_selected = 1
                if i == 0:
                    result = "incorrect"
                else:
                    result = "correct" if match else "incorrect"
                reaction_time = elapsed
                break

            if state.option_2:
                _play_beep()
                option_selected = 2
                if i == 0:
                    result = "incorrect"
                else:
                    result = "correct" if not match else "incorrect"
                reaction_time = elapsed
                break

            if elapsed >= total_window:
                break

            pygame.time.delay(1)

        # Lock input immediately after a decision/timeout (prevents double-response leakage)
        _flush_input()
        
        if option_selected is None:
            response = None
        else:
            if option_selected == 1:
                response = "match"
            elif option_selected == 2:
                response = "non_match"

        if match is None:
            correct_response = None
        else:
            if match:
                correct_response = "match"
            else:
                correct_response = "non_match"

        # Log result
        logger.info(
            "TRIAL_RESULT | stim=%s | response=%s | result=%s | reaction_time_ms=%d",
            stim_path.name,
            response,
            result,
            reaction_time,
        )

        # Dummy stimuli (first 2)
        if i == 0 or i == 1:
            if result == "timeout":
                update_save(phase, condition, "2back", None, None, "correct", None, stim_id)

            else:
                update_save(phase, condition, "2back", response, None, "incorrect", reaction_time, stim_id)

                if _is_practice:
                    show_feedback(screen, "incorrect")
                    
        # Actual stimuli          
        else:
            update_save(phase, condition, "2back", response, correct_response, result, reaction_time, stim_id)

            if _is_practice:
                show_feedback(screen, result)

        pygame.display.flip()
        pygame.time.delay(cfg.FB_DURATION)
        _flush_input()

    return screen
