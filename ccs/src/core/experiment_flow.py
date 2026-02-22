from datetime import datetime

import pygame

from core.motor import Motor
from core.sensorimotor import Sensorimotor
from ui.pygame_render import get_participant_id, record_hands
import utils.config as cfg
from utils.logger import get_logger
from utils.saves import InitResultCSV


logger = get_logger("./src/core/experiment_flow")


def run() -> None:
    run_started_at = datetime.now()
    pygame.init()

    try:
        # Set up screen in fullscreen mode
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

        # Update meta_parameters with actual screen dimensions
        cfg.SCREEN_W = screen_width
        cfg.SCREEN_H = screen_height

        pygame.mixer.init()

        # Legacy variables (no longer used for data saving - trials save individually)
        all_results = []
        all_acc = []

        # Record global task start time (yyyy-mm-dd-hh-mm-ss)
        cfg.START_TIME = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        def end_and_save():
            cfg._end_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            pygame.time.wait(1000)
            pygame.quit()
            quit()

        def run_sensorimotor():
            logger.info("Transition: entering sensorimotor task")
            sensorimotor = Sensorimotor(screen, all_results, all_acc, version=cfg.MAPPING)
            sensorimotor.run_sm_segment1(lambda: sensorimotor.run_sm_segment3(lambda: end_and_save()))

        def run_motor():
            logger.info("Transition: entering motor task")
            motor = Motor(screen, all_results, all_acc, version=cfg.MAPPING)
            motor.run_m_segment1(
                lambda: motor.run_m_segment3(
                    lambda: motor.run_m_segment5(lambda: run_sensorimotor())
                )
            )

        # Get participant ID
        screen = get_participant_id(screen)
        participant_id = cfg.PID or ""

        # Record dominant hand / hand used
        screen = record_hands(screen)

        InitResultCSV("results.csv", participant_id)
        run_motor()
    finally:
        elapsed_seconds = int((datetime.now() - run_started_at).total_seconds())
        elapsed_minutes = elapsed_seconds / 60
        logger.info(
            f"Total task duration: {elapsed_minutes:.2f} minutes ({elapsed_seconds} seconds)"
        )


if __name__ == "__main__":
    run()
