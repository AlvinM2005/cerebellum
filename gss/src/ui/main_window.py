# ./src/ui/main_window.py
from __future__ import annotations
from typing import Tuple
import pygame
import datetime

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import init_display, get_participant_id, _compute_version_from_pid
from core.saves import create_save
from core.show_instructions import show_instructions
from core.pygame_setup import show_instruction_page

# For testing purposes
# from core.mapping_practice import run_mapping, mapping_interval
# from core.stroop_practice import run_stroop
# from core.gss_practice import run_gss_practice
# from core.gss_main import run_gss_main


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

    # For testing purposes
    # mp_interval(screen)
    # run_mp(screen)
    # run_stroop(screen)
    # run_gss_practice(screen)
    # run_gss_main(screen)

    show_instructions(screen)

    pygame.quit()
