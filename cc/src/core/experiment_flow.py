from datetime import datetime

import pygame

import core.framework as framework
from core.contextual import Contextual
from core.motor import Motor
from core.sensorimotor import Sensorimotor
from ui.pygame_render import record_hands
import utils.config as cfg
from utils.save_results import InitResultCSV


def run() -> None:
    pygame.init()

    # Set up screen in fullscreen mode
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    framework.screen = screen

    # Update meta_parameters with actual screen dimensions
    cfg.SCREEN_W = screen_width
    cfg.SCREEN_H = screen_height

    pygame.mixer.init()

    # Legacy variables (no longer used for data saving - trials save individually)
    all_results = []
    all_acc = []

    # Record global task start time (yyyy-mm-dd-hh-mm-ss)
    cfg.START_TIME = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Run experiment (in backward order, because Python requires functions to be defined before they are called to use)
    def end_and_save():
        cfg._end_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # No backup save needed - all results already saved trial-by-trial
        pygame.time.wait(1000)
        pygame.quit()
        quit()

    def run_contextual():
        contextual = Contextual(screen, all_results, all_acc, version=cfg.VERSION)
        contextual.run_c_segment1(lambda: contextual.run_c_segment3(lambda: end_and_save()))

    def run_sensorimotor():
        sensorimotor = Sensorimotor(screen, all_results, all_acc, version=cfg.VERSION)
        sensorimotor.run_sm_segment1(lambda: sensorimotor.run_sm_segment3(lambda: run_contextual()))

    def run_motor():
        motor = Motor(screen, all_results, all_acc, version=cfg.VERSION)
        motor.run_m_segment1(
            lambda: motor.run_m_segment3(
                lambda: motor.run_m_segment5(lambda: run_sensorimotor())
            )
        )

    # Get participant ID
    participant_id = framework.get_participant_id(screen)
    cfg.PID = participant_id
    print("set Global participateID=", framework.GetParticipantId())

    # Determine VERSION / Set INSTRUCTIONS
    try:
        version = int(participant_id[-1])
        if version % 2 == 1:
            version = 1
        else:
            version = 2
    except Exception:
        version = 1
    cfg.VERSION = version

    # Record dominant hand / hand used
    record_hands(screen)

    InitResultCSV("results.csv", participant_id)
    run_motor()


if __name__ == "__main__":
    run()
