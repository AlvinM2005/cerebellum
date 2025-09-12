import pygame
from meta_parameters import *
from stimuli import *
from framework import *
from motor import Motor
from save_results import *
from datetime import datetime

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Motor Task")

# Global result storage
all_results = []
all_acc = []

# Record start time globally
global_start_time = datetime.now().strftime("%y/%m/%d %H:%M:%S")

# End and save
def end_and_save():
    global_end_time = datetime.now().strftime("%y/%m/%d %H:%M:%S")
    # No backup save needed - all results already saved trial-by-trial
    pygame.time.wait(1000)
    pygame.quit()
    quit()

# Main runner
def run_motor():
    motor = Motor(screen, all_results, all_acc, version=VERSION)
    motor.run_m_segment1(lambda:
        motor.run_m_segment3(lambda:
                motor.run_m_segment5(lambda: end_and_save())))

# Get participant ID
participant_id = get_participant_id(screen)
print("set Global participateID=", GetParticipantId())

# Determine VERSION / Set INSTRUCTIONS
try:
    VERSION = int(participant_id[-1])
    if VERSION % 2 == 1:
        VERSION = 1
    else:
        VERSION = 2
except:
    VERSION = 1

InitResultCSV("results.csv", participant_id)
run_motor()