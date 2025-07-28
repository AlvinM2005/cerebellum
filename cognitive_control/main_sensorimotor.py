import pygame
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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Motor Task")

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

def run_sensorimotor():
    run_sm_segment1(screen, all_results, all_acc, lambda:
        run_sm_segment3(screen, all_results, all_acc, lambda: end_and_save())
    )

participant_id = get_participant_id(screen)

run_sensorimotor()
