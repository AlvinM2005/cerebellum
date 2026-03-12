# ./src/ui/main_window.py
"""
Experiment flow runner.

This module runs the practice blocks with pygame, including:
  - Display init + participant metadata collection (PID, mapping).
  - Ordered practice blocks: color → stroop → interval → speed → accuracy → varying → test.
  - Start block is controlled by `start_from` (default: color_practice).
"""


from __future__ import annotations
from pathlib import Path
import pygame
import datetime
import random
import re

import utils.config as cfg
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import (
    init_display,
    toggle_full_screen,
    get_participant_id,
    record_hands,
    place_image,
)
from core.goal_practice import speed_practice, accuracy_practice, varying_practice
from core.test import run_test
from core.basic_practice import color_practice, stroop_practice, interval_practice
from utils.saves import create_save, finalize_global_end_time

logger = get_logger("./src/core/experiment_flow")


def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _wait_for_next_page(
    screen: pygame.Surface,
    event_handler: EventHandler,
    img_path: Path | None = None,
) -> pygame.Surface:
    """
    Wait until SPACE is pressed (next_page), with min reading time constraint.
    Also handles quit / fullscreen toggle.

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param event_handler: Centralized event handler
    :type event_handler: EventHandler

    :img_path: Image path of the current instruction page
    :type img_path: pathlib.Path

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

            if img_path is not None:
                place_image(screen, img_path)
                pygame.display.flip()
                _flush_input()

        elapsed = pygame.time.get_ticks() - start_ms
        if state.next_page and elapsed >= cfg.MIN_READING_TIME:
            return screen

        pygame.time.delay(10)


def _wait_for_end_page(
    screen: pygame.Surface,
    event_handler: EventHandler,
    img_path: Path | None = None,
    max_duration_ms: int = 10_000,
) -> pygame.Surface:
    """
    End screen behavior:
    - Press SPACE to exit immediately, OR
    - Auto-exit after max_duration_ms.

    Also handles quit / fullscreen toggle.

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param event_handler: Centralized event handler
    :type event_handler: EventHandler

    :param img_path: Image path of the end page (redraw after fullscreen toggle)
    :type img_path: pathlib.Path | None

    :param max_duration_ms: Auto-exit timeout in milliseconds
    :type max_duration_ms: int

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

            if img_path is not None:
                place_image(screen, img_path)
                pygame.display.flip()
                _flush_input()

        elapsed = pygame.time.get_ticks() - start_ms
        if state.next_page:
            return screen

        if elapsed >= max_duration_ms:
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
    :type img_path: pathlib.Path

    :param event_handler: Centralized event handler
    :type event_handler: EventHandler

    :return: Possibly updated display surface
    :rtype: pygame.Surface
    """
    place_image(screen, img_path)
    pygame.display.flip()
    _flush_input()
    return _wait_for_next_page(screen, event_handler, img_path=img_path)


def _show_end_page(
    screen: pygame.Surface,
    img_path: Path,
    event_handler: EventHandler,
    max_duration_ms: int = 10_000,
) -> pygame.Surface:
    """
    Show the final end screen and exit on SPACE or timeout.

    :param screen: Current display surface
    :type screen: pygame.Surface

    :param img_path: End screen image path
    :type img_path: pathlib.Path

    :param event_handler: Centralized event handler
    :type event_handler: EventHandler

    :param max_duration_ms: Auto-exit timeout in milliseconds
    :type max_duration_ms: int

    :return: Possibly updated display surface
    :rtype: pygame.Surface
    """
    place_image(screen, img_path)
    pygame.display.flip()
    _flush_input()
    return _wait_for_end_page(
        screen,
        event_handler,
        img_path=img_path,
        max_duration_ms=max_duration_ms,
    )


def run() -> None:
    """
    Run the full practice flow.

    Steps:
        1) init display
        2) get PID + mapping
        3) record hands
        4) create save
        5) run blocks by order from `start_from`: color → stroop → interval → speed → accuracy → varying
        6) finalize and quit

    :return: None
    """
    pygame.init()
    pygame.font.init()
    cfg.START_TIME = datetime.datetime.now().isoformat()
    cfg._start_time = cfg.START_TIME

    try:
        screen = init_display()
        cfg.global_start_time = datetime.datetime.now().isoformat()
        # 1) PID + MAPPING (computed from PID suffix in admin flow)
        screen = get_participant_id(screen)

        # 2) Hands (admin flow)
        screen = record_hands(screen)
        logger.info(f"Participant ID = {cfg.PID} | Dominant Hand = {cfg.DH} | Hand Used = {cfg.UH}")
                # Derive PID-based version (mod 16) from PID suffix split by '-' or '_' and store in cfg.version
        try:
            pid_str = cfg.PID or ""
            parts = [p for p in re.split(r"[-_]\s*", pid_str) if p]
            suffix = parts[-1] if parts else ""
            try:
                pid_suffix_num = int(suffix)
                cfg.version = pid_suffix_num % 16
                logger.info(f"Derived version={cfg.version} from PID suffix {pid_suffix_num}")
            except ValueError:
                cfg.version = None
                logger.info("PID suffix is not an integer; will use default task sequence index 0")
        except Exception as e:
            cfg.version = None
            logger.warning(f"Failed to derive version from PID: {e}")

        # Set task_sequence from version; if version is None, fallback to index 0
        try:
            if hasattr(cfg, "TASK_SEQUENCES") and cfg.TASK_SEQUENCES:
                _seq_idx = (cfg.version % len(cfg.TASK_SEQUENCES)) if (cfg.version is not None) else 0
                cfg.task_sequence = cfg.TASK_SEQUENCES[_seq_idx]
                logger.info(f"Task sequence index={_seq_idx} value={cfg.task_sequence}")
            else:
                cfg.task_sequence = None
                logger.info("Task sequence not set (sequences missing)")
        except Exception as e:
            cfg.task_sequence = None
            logger.warning(f"Failed to set task_sequence: {e}")# Event handling
        # Create save
        create_save()
        # Block sequencing control: set start_from to choose starting block
        start_from = 'color_practice'
        ordered_blocks = [
            ("color_practice", color_practice),
            ("stroop_practice", stroop_practice),
            ("interval_practice", interval_practice),
            ("speed_practice", speed_practice),
            ("accuracy_practice", accuracy_practice),
            ("varying_practice", varying_practice),
            ("test", run_test),
        ]
        index_map = {}
        for i, (n, fn) in enumerate(ordered_blocks):
            index_map[n] = i
            index_map[getattr(fn, "__name__", n)] = i
        start_idx = index_map.get(start_from, 0)
        for name, fn in ordered_blocks[start_idx:]:
            screen = fn(screen)

        # Create save
        logger.info("Task completed successfully!")
    finally:
        if cfg.START_TIME is not None:
            try:
                start_dt = datetime.datetime.fromisoformat(cfg.START_TIME)
                elapsed_s = (datetime.datetime.now() - start_dt).total_seconds()
                logger.info(f"Total task duration: {elapsed_s / 60:.2f} minutes ({int(elapsed_s)} seconds)")
            except ValueError:
                pass

        finalize_global_end_time()
        cfg.global_end_time = datetime.datetime.now().isoformat()






















