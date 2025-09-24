from datetime import datetime
from tabnanny import process_tokens
import os
import csv

import pygame

from instructions import *
from run_trial import *
from framework import *
from meta_parameters import *

# Global variables for screen
screen = None
SCREEN_WIDTH = None 
SCREEN_HEIGHT = None

# Global variable to store the CSV filename for the entire session
CSV_FILENAME = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

COUNTDOWN = 10
TEST_COUNDTOWN = 2

def generate_unique_filename(participant_id):
    """
    Generate unique filename with automatic versioning.
    Returns a filename in format: [participantID]_TAP_results.csv
    If file exists, adds incremental suffix: [participantID]_TAP_results_2.csv, etc.
    """
    base_filename = f'{participant_id}_TAP_results.csv'
    csv_file = os.path.join(SCRIPT_DIR, 'results', base_filename)
    
    # Check if file exists and increment version
    if os.path.exists(csv_file):
        version = 2
        while True:
            versioned_filename = f'{participant_id}_TAP_results_{version}.csv'
            csv_file = os.path.join(SCRIPT_DIR, 'results', versioned_filename)
            if not os.path.exists(csv_file):
                break
            version += 1
    
    print(f"Generated unique filename: {os.path.basename(csv_file)}")
    return csv_file

def show_gray_screen(screen, countdown=TEST_COUNDTOWN):
    pygame.font.init()
    font = pygame.font.SysFont(None, 60)  # Font and size, adjustable
    clock = pygame.time.Clock()

    for i in range(countdown, 0, -1):
        screen.fill(GRAY_RGB)

        # Generate text
        plural = "s" if i > 1 else ""
        text_surface = font.render(f"The next trial will start in: {i} second{plural}", True, BLACK_RGB)
        text_rect = text_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))

        # Draw text
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

        # Wait 1 second
        pygame.time.delay(1000)
        clock.tick(60)

def process_func(i, csv_file, trail_count, participant_id):
    if VERSION == 1:
        if i == PRACTICE_1:
            for j in range(2):
                single_trail(screen, "practice1", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_1:
            for j in range(3):
                single_trail(screen, "block1", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == BLOCK_2:
            for j in range(3):
                single_trail(screen, "block2", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == PRACTICE_2:
            for j in range(2):
                single_trail(screen, "practice2", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_3:
            for j in range(3):
                single_trail(screen, "block3", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == BLOCK_4:
            for j in range(3):
                single_trail(screen, "block4", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
    else:
        if i == PRACTICE_1:
            for j in range(2):
                single_trail(screen, "practice1", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_1:
            for j in range(3):
                single_trail(screen, "block1", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == BLOCK_2:
            for j in range(3):
                single_trail(screen, "block2", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == PRACTICE_2:
            for j in range(2):
                single_trail(screen, "practice2", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_3:
            for j in range(3):
                single_trail(screen, "block3", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == BLOCK_4:
            for j in range(3):
                single_trail(screen, "block4", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
    return trail_count

if __name__ == '__main__':
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()

    pygame.time.delay(10)

    # Set up screen in fullscreen mode
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Tapping Task")

    # Get participant ID
    participant_id = get_participant_id(screen)

    try:
        VERSION = int(participant_id[-1])
        if VERSION % 2 == 1:
            VERSION = 1
            INSTRUCTIONS = get_instructions(INSTRUCTION_PATH)
        else:
            VERSION = 2
            INSTRUCTIONS = get_instructions(REVERSED_INSTRUCTION_PATH)
    except:
        VERSION = 1
        INSTRUCTIONS = get_instructions(INSTRUCTION_PATH)

    # Generate unique filename with automatic versioning
    CSV_FILENAME = generate_unique_filename(participant_id)

    # Ensure results directory exists
    os.makedirs(os.path.dirname(CSV_FILENAME), exist_ok=True)

    # Create CSV file with headers
    with open(CSV_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["participant_id", "group", "block", "trial", "tap_num", "type", "ISI_ms", "condition", "difficulty", "stimuli_path", "synchronized_sound_tick_ms", "key_response_tick_ms",
                         "interval_ms", "trial_type", "key_response", "key_correct", "start_time", "end_time"])


    global_start = pygame.time.get_ticks()
    results = []
    trail_count = 1
    for i in range(1, TOTAL_INSTRUCTIONS_PAGE + 1):
        instruction_path = os.path.join(SCRIPT_DIR, "instructions", "{}.jpg".format(i))
        show_next_page(screen, instruction_path)
        trail_count = process_func(i, CSV_FILENAME, trail_count, participant_id)

    for result in results:
        print()
        print(result)
