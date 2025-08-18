import pygame
import framework
from meta_parameters import *
from stimuli import *
from framework import *
from motor import *
from sensorimotor import *
from contextual import *
from save_results import *
from instructions_try import instruction, reversed_instruction
from datetime import datetime

# Initialize Pygame
pygame.init()

# Set up screen in fullscreen mode
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
framework.screen = screen

# Update meta_parameters with actual screen dimensions
import meta_parameters
meta_parameters.SCREEN_WIDTH = SCREEN_WIDTH
meta_parameters.SCREEN_HEIGHT = SCREEN_HEIGHT

pygame.mixer.init()

# Toggle fullscreen function
def toggle_fullscreen():
    """Toggle between fullscreen and windowed mode"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT
    screen_info = pygame.display.Info()

    if screen.get_flags() & pygame.FULLSCREEN:
        # Switch to windowed mode
        window_width = int(screen_info.current_w * 0.8)
        window_height = int(screen_info.current_h * 0.8)
        SCREEN_WIDTH = max(1024, min(window_width, screen_info.current_w - 100))
        SCREEN_HEIGHT = max(768, min(window_height, screen_info.current_h - 100))
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        framework.screen = screen
        
        # Update meta_parameters with new screen dimensions
        import meta_parameters
        meta_parameters.SCREEN_WIDTH = SCREEN_WIDTH
        meta_parameters.SCREEN_HEIGHT = SCREEN_HEIGHT
        
        print(f"Switched to windowed mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        # Switch to fullscreen mode
        SCREEN_WIDTH = screen_info.current_w
        SCREEN_HEIGHT = screen_info.current_h
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        framework.screen = screen
        
        # Update meta_parameters with new screen dimensions
        import meta_parameters
        meta_parameters.SCREEN_WIDTH = SCREEN_WIDTH
        meta_parameters.SCREEN_HEIGHT = SCREEN_HEIGHT
        
        print(f"Switched to fullscreen mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Legacy variables (no longer used for data saving - trials save individually)
all_results = []
all_acc = []

# Record start time globally
global_start_time = datetime.now().strftime("%y/%m/%d %H:%M:%S")

# Run experiment (in backward order, because Python requires functions to be defined before they are called to use)
def end_and_save():
    global_end_time = datetime.now().strftime("%y/%m/%d %H:%M:%S")
    # No backup save needed - all results already saved trial-by-trial
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

# Determine VERSION / Set INSTRUCTIONS
try:
    VERSION = int(participant_id[-1])
    if VERSION % 2 == 1:
        VERSION = 1
        instruction()
    else:
        VERSION = 2
        reversed_instruction()
except:
    VERSION = 1
    instruction()

InitResultCSV("results.csv", participant_id)
run_motor()
