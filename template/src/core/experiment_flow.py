# ./src/ui/main_window.py
"""
Experiment flow runner.

This module orchestrates the full experimental session, including:
    - Initializing the pygame environment and display.
    - Collecting participant metadata (Participant ID, VERSION).
    - Loading instruction pages and stimulus resources.
    - Sequentially presenting instruction screens.
    - Executing the complete experiment flow, inserting task blocks at the appropriate stages.
"""


from __future__ import annotations
from pathlib import Path
import pygame
import datetime
import random

import utils.config as cfg
from utils.logger import get_logger
import utils.paths as paths
from utils.event_handler import EventHandler
from ui.pygame_render import (
    init_display,
    toggle_full_screen,
    get_participant_id,
    record_hands,
    place_image,
)
from core.practice import run_practice
from core.test import run_test
from core.saves import create_save

logger = get_logger("./src/core/experiment_flow")


def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _wait_for_next_page(screen: pygame.Surface, event_handler: EventHandler) -> pygame.Surface:
    """
    Wait until SPACE is pressed (next_page), with min reading time constraint.
    Also handles quit / fullscreen toggle.

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param event_handler: Centralized event handler
    :type event_handler: EventHandler

    :return: Possibly updated display surface
    :rtype: pygame.Surface
    """
    start_ms = pygame.time.get_ticks()

    while True:
        state = event_handler.poll()

        if state.quit:
            pygame.quit()
            raise SystemExit

        if state.toggle_full_screen:
            pygame.event.clear()
            screen = toggle_full_screen(screen)
            pygame.event.clear()

        elapsed = pygame.time.get_ticks() - start_ms
        if state.next_page and elapsed >= cfg.MIN_READING_TIME:
            return screen

        pygame.time.delay(10)


def _show_instruction_page(
    screen: pygame.Surface,
    img_path: Path,
    event_handler: EventHandler,
) -> pygame.Surface:
    """
    Show a single instruction page and advance on SPACE.

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param img_path: Instruction image path
    :type img_path: Path

    :param event_handler: Centralized event handler
    :type event_handler: EventHandler

    :return: Possibly updated display surface
    :rtype: pygame.Surface
    """
    place_image(screen, img_path)
    pygame.display.flip()
    _flush_input()
    return _wait_for_next_page(screen, event_handler)


def run() -> None:
    """
    Deploy the full experiment flow (no result recording in this clean version).

    Steps:
    1) get_participant_id
    2) select_version
    3) instructions 1-3 (SPACE to advance)
    4) instruction practice
    5) practice block (randomized 5 stimuli, with feedback)
    6) instruction 4
    7) instruction test
    8) test block (randomized 5 stimuli, no feedback)
    9) instruction 5
    10) end task

    :return: None
    """
    pygame.init()
    pygame.font.init()
    cfg.START_TIME = datetime.datetime.now().isoformat()

    screen = init_display()

    # 1) PID
    get_participant_id(screen)

    # 2) VERSION
    record_hands(screen)
    logger.info(f"Participant ID = {cfg.PID} | Dominand Hand = {cfg.dominant_hand} | Less Affected Hand = {cfg.less_affected_hand}")

    # Load assets
    event_handler = EventHandler()

    # Create save
    create_save()

    # TODO: Modify test flow based on needs
    
    # 3) instructions 1-3
    for i in range(3):
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[i], event_handler)

    # 4) instruction practice
    screen = _show_instruction_page(screen, paths.PRACTICE_INSTRUCTIONS, event_handler)

    # 5) practice block (with feedback)
    screen = run_practice(screen, "practice", paths.STIMULI, event_handler)

    # 6) instruction 4
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[3], event_handler)

    # 7) instruction test
    screen = _show_instruction_page(screen, paths.TEST_INSTRUCTIONS, event_handler)

    # 8) test block (no feedback)
    screen = run_test(screen, "test", paths.STIMULI, event_handler)

    # 9) instruction 5
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[4], event_handler)

    # 10) end
    pygame.quit()
