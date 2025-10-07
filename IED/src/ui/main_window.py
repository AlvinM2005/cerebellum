# ./src/ui/main_window.py
from __future__ import annotations
from typing import Tuple
import pygame
import datetime

import utils.config as cfg
from utils.logger import get_logger
from utils.pygame_setup import init_display, get_participant_id, _compute_version_from_pid
from core.test_flow import run_test_phase
from utils.saves import create_save


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

    for i in range(cfg.PHASE_COUNT):
        if cfg.force_quit:
            break
        else:
            run_test_phase(screen, i+1)
        logger.info(f"Running phase {i+1}")

    pygame.quit()
