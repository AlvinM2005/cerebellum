from datetime import datetime
from tabnanny import process_tokens

import pygame

from instructions import *
from run_trial import *
from framework import *

def process_func(i, csv_file, trail_count, participant_id):
    if VERSION == 1:
        if i == PRACTICE_1:
            for j in range(2):
                single_trail("practice1", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_1:
            for j in range(3):
                single_trail("block1", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_2:
            for j in range(3):
                single_trail("block2", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == PRACTICE_2:
            for j in range(2):
                single_trail("practice2", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_3:
            for j in range(3):
                single_trail("block3", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_4:
            for j in range(3):
                single_trail("block4", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
    else:
        if i == PRACTICE_1:
            for j in range(2):
                single_trail("practice1", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_1:
            for j in range(3):
                single_trail("block1", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_2:
            for j in range(3):
                single_trail("block2", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == PRACTICE_2:
            for j in range(2):
                single_trail("practice2", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_3:
            for j in range(3):
                single_trail("block3", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
        elif i == BLOCK_4:
            for j in range(3):
                single_trail("block4", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
    return trail_count

if __name__ == '__main__':
    # Initialize pygame
    pygame.init()

    # Set up screen in fullscreen mode
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

    pygame.mixer.init()

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

    # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    csv_file = f'results/{participant_id}_result.csv'

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["participant_id", "group", "block", "trial", "tap_num", "type", "ISI_ms", "condition", "difficulty", "stimuli_path", "synchronized_sound_tick_ms", "key_response_tick_ms",
                         "interval_ms", "trial_type", "key_correct", "start_time", "end_time"])


    global_start = pygame.time.get_ticks()
    results = []
    trail_count = 1
    for i in range(1, TOTAL_PAGE + 1):
        show_next_page(screen, "instructions/{}.jpg".format(i))
        trail_count = process_func(i, csv_file, trail_count, participant_id)

    for result in results:
        print()
        print(result)
