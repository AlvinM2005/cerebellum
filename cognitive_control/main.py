import pygame
import framework
from meta_parameters import *
from stimuli import *
from framework import *
from motor import *
from sensorimotor import *
from contextual import *
from save_results import *
from datetime import datetime

# Initialize Pygame
pygame.init()

# Set up screen in fullscreen mode
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
framework.screen = screen

pygame.mixer.init()

# Global result storage
all_results = []
all_acc = []

# Record start time globally
global_start_time = datetime.now().strftime("%y/%m/%d %H:%M:%S")

# Run experiment (in backward order, because Python requires functions to be defined before they are called to use)
def end_and_save():
    global_end_time = datetime.now().strftime("%y/%m/%d %H:%M:%S")
    save_results_to_csv("results.csv", participant_id, all_results, global_start_time, global_end_time)
    pygame.time.wait(1000)
    pygame.quit()
    quit()

def run_contextual():
    run_c_segment1(screen, all_results, all_acc, lambda:
        run_c_segment3(screen, all_results, all_acc, lambda: end_and_save())
    )

def run_sensorimotor():
    run_sm_segment1(screen, all_results, all_acc, lambda:
        run_sm_segment3(screen, all_results, all_acc, lambda: run_contextual())
    )

def run_motor():
    run_m_segment1(screen, all_results, all_acc, lambda:
        run_m_segment3(screen, all_results, all_acc, lambda:
            run_m_segment5(screen, all_results, all_acc, lambda: run_sensorimotor())
        )
    )

# Get participant ID
participant_id = get_participant_id(screen)
print("set Global participateID=", GetParticipantId())

'''
How to deal with the VERSION???
'''

# # Determine VERSION / Set INSTRUCTIONS
# try:
#     VERSION = int(participant_id[-1])
#     if VERSION % 2 == 1:
#         VERSION = 1
#         instruction()
#     else:
#         VERSION = 2
#         reversed_instruction()
# except:
#     VERSION = 1
#     instruction()

InitResultCSV("results.csv", participant_id)
run_motor()
