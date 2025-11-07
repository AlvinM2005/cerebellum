# ./src/ui/main_window.py
from __future__ import annotations
from typing import Tuple
import pygame
import datetime

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import init_display, get_participant_id, _compute_version_from_pid
from core.test_flow import run_practice, run_single_stimulus_phase, run_side_by_side_multiple_stimulus_phase, run_overlapped_multiple_stimulus_phase_targeting_shape, run_overlapped_multiple_stimulus_phase_targeting_line
from core.saves import create_save
from core.show_instructions import show_instructions


logger = get_logger("./src/ui/main_window") # create logger


def run() -> None:
    """
    Main entry point (called by main.py)
    """
    pygame.init()
    pygame.font.init()
    cfg.START_TIME = datetime.datetime.now().isoformat()

    screen = init_display()
    cfg.PID = get_participant_id(screen)
    create_save()

    # Compute VERSION based on the last digit of ID and write it
    cfg.VERSION = _compute_version_from_pid(cfg.PID)
    logger.info(f"Participant ID = {cfg.PID} | VERSION = {cfg.VERSION}")

    show_instructions(screen)

    pygame.quit()
