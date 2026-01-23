# ./src/core/test.py
"""
Test block execution logic using pygame.

This module presents randomized stimulus blocks, collects keyboard responses with timeout handling, and optionally displays feedback during practice trials.
"""


from __future__ import annotations
from pathlib import Path
import pygame
import random

import utils.config as cfg
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import (
    toggle_full_screen,
    place_image,
)
from core.saves import update_save


logger = get_logger("./src/core/practice")

def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def run_test(
    screen: pygame.Surface,
    block: str,
    stimuli: list[Path],
    event_handler: EventHandler,
) -> pygame.Surface:
    """
    Run a stimulus block once (each stimulus exactly once, randomized order).

    During each stimulus:
    - Wait for 'd' / 'k' response within cfg.MAX_REACTION_TIME ms
    - If timeout: outcome = "timeout"
    - If response: outcome = "correct"/"incorrect" based on mapping rule
    - Practice: show_feedback for cfg.FB_DURATION ms
    - Test: no feedback

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param block: Name of the block
    :type block: str

    :param stimuli: List of stimulus image paths
    :type stimuli: list[pathlib.Path]

    :param event_handler: Centralized event handler instance
    :type event_handler: EventHandler

    :return: Active display surface after the block (may be updated by fullscreen toggle)
    :rtype: pygame.Surface
    """
    shuffled = random.sample(stimuli, k=len(stimuli))

    for stim_path in shuffled:
        stim_id = int(stim_path.stem)  # 1..5
        correct_response = 1 if (stim_id % 2 == 1) else 2

        place_image(screen, stim_path, None, (400,300))
        pygame.display.flip()
        _flush_input()

        t0 = pygame.time.get_ticks()
        option_selected: int | None = None
        reaction_time = cfg.MAX_REACTION_TIME
        outcome = "timeout"

        while True:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                place_image(screen, stim_path)
                pygame.display.flip()
                _flush_input()

            elapsed = pygame.time.get_ticks() - t0

            if state.option_1:
                option_selected = 1
                outcome = "correct" if correct_response == 1 else "incorrect"
                reaction_time = elapsed
                break

            if state.option_2:
                option_selected = 2
                outcome = "correct" if correct_response == 2 else "incorrect"
                reaction_time = elapsed
                break

            if elapsed >= cfg.MAX_REACTION_TIME:
                break

            pygame.time.delay(1)

        # Lock input immediately after a decision/timeout (prevents double-response leakage)
        _flush_input()

        # Log result
        logger.info(
            "TRIAL_RESULT | block=%s | stim=%s | option=%s | status=%s | reaction_time_ms=%d",
            block,
            stim_path.name,
            option_selected if option_selected is not None else "None",
            outcome,
            reaction_time,
        )

        # Update save
        update_save("practice", None, None, outcome, reaction_time, stim_path.name)

    return screen