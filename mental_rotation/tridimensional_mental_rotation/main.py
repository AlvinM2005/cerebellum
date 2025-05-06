import pygame
import sys
import os
import csv
import time
import random
import pygame.event

from Instruction import Instruction
from FeedbackIcon import FeedbackIcon

# Initialize pygame
pygame.init()

# Meta parameters
# MODE = "actual" # Use when running the real experiment
MODE = "test"  # Use when testing
VERSION = 1 # Use for normal test (v-normal / m-mirrored)
# VERSION = 2 # Use for reversed test (v-mirrored / m-normal)

# Time settings
ACTUAL_READ_TIME = 10000
TEST_READ_TIME = 100
ACTUAL_MAX_RESPOND_TIME = 5000
TEST_MAX_RESPOND_TIME = 2000
ACTUAL_FEEDBACK_TIME = 2000
TEST_FEEDBACK_TIME = 500

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 15
DEMO_PAGE = 10
TEST1_PAGE = 12
TEST2_PAGE = 14

# Paths
if VERSION == "normal":
    INSTRUCTION_DIR = "./stimuli/instructions/"
elif VERSION == 2:
    INSTRUCTION_DIR = "./stimuli/instructions_reversed/"
RESULT_DIR = "./results/"
CONDITION_DIR = "./stimuli/conditions/"

# Set up screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mental Rotation Test")

# Fonts
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)

# Participant info
participant_info = ""
input_active = True
instruction_active = False

global_start_time = None
global_end_time = None
break_start_time = None
break_end_time = None
break_duration_ms = 0

# Phase data
phase_data = {
    "demo": [],
    "test1": [],
    "test2": []
}

def load_instructions(mode):
    instruction_objects = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.png")
        instruction_objects.append(Instruction(img_path))

    instruction_index = 0
    instruction_locked = True
    unlock_timer = pygame.time.get_ticks()
    READ_TIME = ACTUAL_READ_TIME if mode == "actual" else TEST_READ_TIME

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not instruction_locked:
                    instruction_index += 1
                    instruction_locked = True
                    unlock_timer = pygame.time.get_ticks()

                    if instruction_index == DEMO_PAGE:
                        result = run_trials("demo")
                        show_results("demo", result)
                    elif instruction_index == TEST1_PAGE:
                        result = run_trials("test1")
                        show_results("test1", result)
                    elif instruction_index == TEST2_PAGE - 1:
                        global break_start_time
                        break_start_time = time.time()
                    elif instruction_index == TEST2_PAGE:
                        global break_end_time, break_duration_ms
                        break_end_time = time.time()
                        break_duration_ms = int((break_end_time - break_start_time) * 1000)
                        result = run_trials("test2")
                        show_results("test2", result)
                        save_all_results()

        if current_time - unlock_timer >= READ_TIME:
            instruction_locked = False

        screen.fill((0, 0, 0))
        if instruction_index < TOTAL_INSTRUCTION_PAGES:
            img = instruction_objects[instruction_index].image
            if img:
                img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(img, img_rect)
                pygame.display.flip()
            else:
                break

def run_trials(phase):
    if MODE == "actual":
        max_respond_time = ACTUAL_MAX_RESPOND_TIME
        feedback_time = ACTUAL_FEEDBACK_TIME
        suffix = "" if VERSION == 1 else "_flipped"
    else:
        max_respond_time = TEST_MAX_RESPOND_TIME
        feedback_time = TEST_FEEDBACK_TIME
        if phase == "demo":
            suffix = "" if VERSION == 1 else "_flipped"
        elif phase == "test1" or phase == "test2":
            suffix = "_short" if VERSION == 1 else "_short_flipped"

    condition_path = os.path.join(CONDITION_DIR, f"{phase}{suffix}.csv")
    feedback_icons = FeedbackIcon()

    trial_conditions = []
    try:
        with open(condition_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trial_conditions.append({
                    "object_id": row["object_id"],
                    "rotation_angle": row["rotation_angle"],
                    "reversed": row["reversed"],
                    "condition": row["condition"],
                    "difficulty": row["difficulty"],
                    "stimuli_path": row["stimuli_path"],
                    "key_correct": row["key_correct"]
                })
    except Exception as e:
        print(f"Failed to read condition info for {phase}: {e}")
        return

    random.shuffle(trial_conditions)
    record = []

    for idx, cond in enumerate(trial_conditions):
        try:
            img = pygame.image.load(cond["stimuli_path"])
            img = pygame.transform.scale(img, (800, 427))
        except Exception as e:
            print(f"Error loading image {cond['stimuli_path']}: {e}")
            continue

        screen.fill((0, 0, 0))
        img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(img, img_rect)

        label_font = pygame.font.SysFont(None, 48)
        if VERSION == 1:
            text_v = label_font.render("V (Normal)", True, (255, 255, 255))
            text_m = label_font.render("M (Reversed)", True, (255, 255, 255))
        else:
            text_v = label_font.render("V (Reversed)", True, (255, 255, 255))
            text_m = label_font.render("M (Normal)", True, (255, 255, 255))
        screen.blit(text_v, (SCREEN_WIDTH // 4 - text_v.get_width() // 2, SCREEN_HEIGHT - 200))
        screen.blit(text_m, (3 * SCREEN_WIDTH // 4 - text_m.get_width() // 2, SCREEN_HEIGHT - 200))
        pygame.display.flip()

        pygame.event.clear()
        trial_start = pygame.time.get_ticks()
        responded = False
        correct = False
        key_response = None
        key_locked = False

        while pygame.time.get_ticks() - trial_start < max_respond_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and not responded and not key_locked:
                    if event.key == pygame.K_v:
                        responded = True
                        key_response = "v"
                        correct = (cond["key_correct"] == "v")
                        key_locked = True
                    elif event.key == pygame.K_m:
                        responded = True
                        key_response = "m"
                        correct = (cond["key_correct"] == "m")
                        key_locked = True
            if responded:
                break

        reaction_time = pygame.time.get_ticks() - trial_start

        phase_data[phase].append({
            "item_number": idx + 1,
            "object_id": cond["object_id"],
            "rotation_angle": cond["rotation_angle"],
            "reversed": cond["reversed"],
            "condition": cond["condition"],
            "difficulty": cond["difficulty"],
            "stimuli_path": cond["stimuli_path"],
            "key_correct": cond["key_correct"],
            "key_response": key_response,
            "correct": int(correct),
            "reaction_time": reaction_time,
            "block": phase
        })

        record.append(correct)

        screen.fill((0, 0, 0))
        if phase == "demo":
            if not responded:
                feedback_img = feedback_icons.timeout_icon
            else:
                feedback_img = feedback_icons.correct_icon if correct else feedback_icons.incorrect_icon
            feedback_rect = feedback_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(feedback_img, feedback_rect)
        pygame.display.flip()
        pygame.time.delay(feedback_time)

    return record

def show_results(phase, result):
    correct_count = sum(1 for r in result if r)
    accuracy = round(100 * correct_count / len(result), 2)

    screen.fill((0, 0, 0))
    text_surface1 = font_large.render(f'You are correct on {accuracy}% of the test.', True, (255, 255, 255))
    screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))

    if phase in ["demo", "test1"]:
        if accuracy >= 90:
            suggestion = "Try to go faster!"
        elif accuracy >= 80:
            suggestion = "Maintain speed and accuracy!"
        else:
            suggestion = "Focus on being more accurate!"
        text_surface2 = font_medium.render(suggestion, True, (255, 255, 255))
        screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2, 300))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def save_all_results():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    save_result_csv(["demo"], f"{participant_info}_demo_result.csv")
    save_result_csv(["test1", "test2"], f"{participant_info}_test_result.csv")

def save_result_csv(phases, filename):
    cumulative_id = 0
    filepath = os.path.join(RESULT_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "participant_id", "version", "phase", "item_number", "object_id", "rotation_angle", "reversed",
            "condition", "difficulty", "stimuli_path", "key_correct", "key_response",
            "correct", "reaction_time_ms", "block", "start_time", "end_time", "break_duration_ms"
        ])

        for phase in phases:
            for trial in phase_data[phase]:
                writer.writerow([
                    participant_info,
                    VERSION,
                    phase,
                    trial["item_number"] + cumulative_id,
                    trial["object_id"],
                    trial["rotation_angle"],
                    trial["reversed"],
                    trial["condition"],
                    trial["difficulty"],
                    trial["stimuli_path"],
                    trial["key_correct"],
                    trial["key_response"],
                    trial["correct"],
                    trial["reaction_time"],
                    trial["block"],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_start_time)),
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_end_time)),
                    break_duration_ms
                ])
            cumulative_id += len(phase_data[phase])

# Participant input
global_start_time = time.time()
while input_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                input_active = False
                instruction_active = True
            elif event.key == pygame.K_BACKSPACE:
                participant_info = participant_info[:-1]
            else:
                participant_info += event.unicode

    screen.fill((255, 255, 255))
    t1 = font_large.render("[For Operator] Type participant group & ID (e.g., YC_001)", True, (0, 0, 0))
    t2 = font_medium.render("Press [space] when you complete.", True, (0, 0, 0))
    input_text = font_medium.render(participant_info, True, (0, 0, 255))
    screen.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, 200))
    screen.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, 300))
    screen.blit(input_text, (SCREEN_WIDTH // 2 - input_text.get_width() // 2, 500))
    pygame.display.flip()

if instruction_active:
    load_instructions(MODE)

global_end_time = time.time()
print("Task completed!")
