# ./src/ui/main_window.py
"""
Experiment flow runner.

This module orchestrates the full experimental session, including:
    - Initializing the pygame environment and display.
    - Collecting participant metadata (Participant ID, MAPPING).
    - Loading instruction pages and stimulus resources.
    - Sequentially presenting instruction screens.
    - Executing the complete experiment flow, inserting task blocks at the appropriate stages.
"""


from __future__ import annotations
from pathlib import Path
import pygame
import datetime

import utils.config as cfg
from utils.logger import get_logger
from utils.paths import load_instructions
from utils.event_handler import EventHandler
from ui.pygame_render import (
    init_display,
    toggle_full_screen,
    get_participant_id,
    record_hands,
    place_image,
)
from core.construct_trials import (
    construct_single_task_trial_series,
    construct_multi_task_trial_series,
)
from core.singla_tasks import run_single_task_phase
from core.multi_tasks import run_multi_task_phase
from utils.saves import create_save, finalize_save

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
    Run full instruction + task flow.

    Steps:
    1) get_participant_id
    2) record_hands (admin pages)
    3) build all trial series
    4) play instructions and insert tasks at configured checkpoints

    :return: None
    """
    pygame.init()
    pygame.font.init()
    cfg.START_TIME = datetime.datetime.now().isoformat()
    cfg.GLOBAL_END_TIME = None
    cfg._start_time = cfg.START_TIME

    try:
        screen = init_display()

        # 1) PID + MAPPING (computed from PID suffix in admin flow)
        screen = get_participant_id(screen)

        # 2) Hands (admin flow)
        screen = record_hands(screen)
        logger.info(
            f"Participant ID = {cfg.PID} | Mapping = {cfg.MAPPING} | "
            f"Dominant Hand = {cfg.DH} | Hand Used = {cfg.UH}"
        )
        create_save()

        # Build trial series
        single_task_series = construct_single_task_trial_series()
        multi_task_series = construct_multi_task_trial_series()
        all_task_series: dict[str, list] = {
            **single_task_series,
            **multi_task_series,
        }

        # Load assets
        event_handler = EventHandler()
        instruction_pages = load_instructions()
        task_order = cfg.INSTRUCTION_TASK_ORDER
        checkpoints = cfg.INSTRUCTION_TASK_AFTER_PNG_BY_MAPPING[cfg.MAPPING]

        for img_path in instruction_pages:
            screen = _show_instruction_page(screen, img_path, event_handler)

            if not img_path.stem.isdigit():
                continue
            page_no = int(img_path.stem)

            if page_no not in checkpoints:
                continue

            task_idx = checkpoints.index(page_no)
            task_phase = task_order[task_idx]
            trial_series = all_task_series[task_phase]

            logger.info(
                "TASK_START | phase=%s | after_instruction_page=%d | trials=%d",
                task_phase,
                page_no,
                len(trial_series),
            )

            if task_phase.startswith("multi_task"):
                screen = run_multi_task_phase(screen, task_phase, trial_series, event_handler)
            else:
                screen = run_single_task_phase(screen, task_phase, trial_series, event_handler)

        logger.info("Task completed successfully!")
    finally:
        cfg.GLOBAL_END_TIME = datetime.datetime.now().isoformat()
        finalize_save()

        if cfg.START_TIME is not None:
            try:
                start_dt = datetime.datetime.fromisoformat(cfg.START_TIME)
                elapsed_s = (datetime.datetime.now() - start_dt).total_seconds()
                logger.info(f"Total task duration: {elapsed_s / 60:.2f} minutes ({int(elapsed_s)} seconds)")
            except ValueError:
                pass

        pygame.quit()
