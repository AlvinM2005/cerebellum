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
from core.one_back import run_1back
from core.two_back import run_2back
from core.three_back import run_3back
from utils.saves import create_save

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
    1) run_1back

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

    # 3) run_1back
    # Practice 1
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[0], event_handler)
    screen = run_1back(screen, "1back_practice1", "practice", True, event_handler)
    # Block 1
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[0], event_handler)
    screen = run_1back(screen, "1back_block1", "test", False, event_handler)
    
    if cfg.MODE == "actual":
        # Block 2
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[0], event_handler)
        screen = run_1back(screen, "1back_block2", "test", False, event_handler)
        # Blcok 3
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[0], event_handler)
        screen = run_1back(screen, "1back_block3", "test", False, event_handler)
    
    # 4) run_2back
    # Practice 2
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[1], event_handler)
    screen = run_2back(screen, "2back_practice2", "practice", True, event_handler)
    # Block 4
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[1], event_handler)
    screen = run_2back(screen, "1back_block4", "test", False, event_handler)
    
    if cfg.MODE == "actual":
        # Block 5
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[1], event_handler)
        screen = run_2back(screen, "1back_block5", "test", False, event_handler)
        # Blcok 6
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[1], event_handler)
        screen = run_2back(screen, "1back_block6", "test", False, event_handler)

   # 5) run_3back
   # Practice 3
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[2], event_handler)
    screen = run_3back(screen, "3back_practice3", "practice", True, event_handler)
    # Block 7
    screen = _show_instruction_page(screen, paths.INSTRUCTIONS[2], event_handler)
    screen = run_3back(screen, "1back_block7", "test", False, event_handler)
    
    if cfg.MODE == "actual":
        # Block 8
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[2], event_handler)
        screen = run_3back(screen, "1back_block8", "test", False, event_handler)
        # Blcok 9
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[2], event_handler)
        screen = run_3back(screen, "1back_block9", "test", False, event_handler)

    # 10) end
    pygame.quit()
