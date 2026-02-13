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
    _compute_version_from_pid,
    _compute_mode_from_pid,
)
from core.practice import run_practice
from core.test import run_test
from core.saves import create_save
from utils.stimulus import load_sentences_from_csv, randomShuffle, EXAMPLE_SENTENCE

logger = get_logger("./src/core/main_window")


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
    
def _wait_for_next_page_or_timeout(
    screen: pygame.Surface, 
    event_handler: EventHandler,
    timeout_ms: int = 10000
) -> pygame.Surface:
    """
    Wait until SPACE is pressed (next_page) OR timeout expires.
    Also handles quit / fullscreen toggle.

    :param screen: Current display surface
    :param event_handler: Centralized event handler
    :param timeout_ms: Timeout in milliseconds (default 10000 = 10 seconds)
    :return: Possibly updated display surface
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
        
        # Exit if timeout reached
        if elapsed >= timeout_ms:
            logger.info(f"Timeout, end task")
            return screen
        
        # Exit if next_page pressed (and min reading time met)
        if state.next_page and elapsed >= cfg.MIN_READING_TIME:
            logger.info(f"Timeout, end task")
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
    pygame.joystick.init()
    cfg.START_TIME = datetime.datetime.now().isoformat()

    screen = init_display()

    # 1) PID, VERSION, MODE
    get_participant_id(screen)
    cfg.VERSION = _compute_version_from_pid(cfg.PID)
    cfg.MODE = _compute_mode_from_pid(cfg.PID)
    cfg.initialize_mode_settings()

    # 2) VERSION
    record_hands(screen)
    logger.info(f"Participant ID = {cfg.PID} | Version = {cfg.VERSION} | Mode = {cfg.MODE} | Dominant Hand = {cfg.dominant_hand} | Used Hand = {cfg.used_hand}")

    # Load assets
    event_handler = EventHandler()

    # Create save
    create_save()

    
    # INSTRUCTIONS PRACTICE 
    for i in range(cfg.BLOCK1_PG-1):
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[i], event_handler)

    # Parsing sentences from csv into stimuli
    try:
        sentences_prac = load_sentences_from_csv(paths.SENTENCES_CSV_PRAC) 
        sentences_test = load_sentences_from_csv(paths.SENTENCES_CSV_TEST)
        
        logger.info(f"Loaded {len(sentences_prac)+len(sentences_test)} sentences")
    except FileNotFoundError:
        sentences_prac = EXAMPLE_SENTENCE
        sentences_test = EXAMPLE_SENTENCE

    mid_index = len(sentences_test)//2
    sentences_experblock1 = sentences_test[:mid_index]
    entences_experblock2 = sentences_test[mid_index:]

    # PRACTICE BLOCK START
    screen = run_practice(screen, "p1", sentences_prac, event_handler)

    # INSTRUCTIONS BLOCK 1
    for i in range (cfg.BLOCK1_PG-1, cfg.BLOCK2_PG-1):
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[i], event_handler)
    # BLOCK 1 START
    screen = run_test(screen, "b1", sentences_experblock1, event_handler)

    # INSTRUCTIONS BLOCK 2
    for i in range(cfg.BLOCK2_PG-1, cfg.LAST_PG-1):
        screen = _show_instruction_page(screen, paths.INSTRUCTIONS[i], event_handler)
    # BLOCK 2 START
    screen = run_test(screen, "b2", entences_experblock2, event_handler)

    # END
    #screen = _show_instruction_page(screen, paths.INSTRUCTIONS[cfg.LAST_PG-1], event_handler)
    place_image(screen, paths.INSTRUCTIONS[cfg.LAST_PG-1])
    pygame.display.flip()
    _flush_input()
    screen = _wait_for_next_page_or_timeout(screen, event_handler, timeout_ms=10000)

    # Calculate and display total task duration
    end_time = datetime.datetime.now()
    start_time_obj = datetime.datetime.fromisoformat(cfg.START_TIME)
    total_duration = end_time - start_time_obj
    total_minutes = total_duration.total_seconds() / 60

    logger.info(f"Task completed successfully!")
    logger.info(f"Total task duration: {total_minutes:.2f} minutes ({int(total_duration.total_seconds())} seconds)")

    pygame.quit()
