from datetime import datetime
from tabnanny import process_tokens

import pygame

from instructions import *
from run_trial import *
from framework import *
from meta_parameters import *

COUNTDOWN = 10
TEST_COUNDTOWN = 2

def show_gray_screen(screen, countdown=TEST_COUNDTOWN):
    pygame.font.init()
    font = pygame.font.SysFont(None, 60)  # 字体和大小，可以调
    clock = pygame.time.Clock()

    for i in range(countdown, 0, -1):
        screen.fill(GRAY_RGB)

        # 生成文字
        text_surface = font.render(f"Next trial will start in: {i} second{'s' if i>1 else ''}", True, BLACK_RGB)
        text_rect = text_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))

        # 绘制文字
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

        # 等 1 秒
        pygame.time.delay(1000)
        clock.tick(60)

def process_func(i, csv_file, trail_count, participant_id):
    if VERSION == 1:
        if i == PRACTICE_1:
            for j in range(2):
                single_trail("practice1", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_1:
            for j in range(3):
                single_trail("block1", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                show_gray_screen(screen)
        elif i == BLOCK_2:
            for j in range(3):
                single_trail("block2", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == PRACTICE_2:
            for j in range(2):
                single_trail("practice2", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_3:
            for j in range(3):
                single_trail("block3", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                show_gray_screen(screen)
                trail_count += 1
        elif i == BLOCK_4:
            for j in range(3):
                single_trail("block4", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
    else:
        if i == PRACTICE_1:
            for j in range(2):
                single_trail("practice1", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_1:
            for j in range(3):
                single_trail("block1", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                show_gray_screen(screen)
                trail_count += 1
        elif i == BLOCK_2:
            for j in range(3):
                single_trail("block2", global_start, pygame.K_k, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 2:
                    show_gray_screen(screen)
        elif i == PRACTICE_2:
            for j in range(2):
                single_trail("practice2", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                trail_count += 1
                if j < 1:
                    show_gray_screen(screen)
        elif i == BLOCK_3:
            for j in range(3):
                single_trail("block3", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
                show_gray_screen(screen)
                trail_count += 1
        elif i == BLOCK_4:
            for j in range(3):
                single_trail("block4", global_start, pygame.K_d, results, participant_id, trail_count, csv_file)
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

    csv_file = f'./results/{participant_id}_result.csv'

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
