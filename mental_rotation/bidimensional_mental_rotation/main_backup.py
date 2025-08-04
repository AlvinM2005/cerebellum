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

# Colors (RGB)
RED_RGB = (255, 72, 72) # FF4848
BLUE_RGB = (72, 197, 255) # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0, 0, 0) # 000000
GRAY_RGB = (128, 128, 128) # 808080
YELLOW_RGB = (255, 255, 0)

# Time settings
ACTUAL_READ_TIME = 10000
TEST_READ_TIME = 100
ACTUAL_MAX_RESPOND_TIME = 5000
TEST_MAX_RESPOND_TIME = 2000
ACTUAL_FEEDBACK_TIME = 2000
TEST_FEEDBACK_TIME = 500

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 15
DEMO_PAGE = 8
TEST1_PAGE = 11
TEST2_PAGE = 14

# Flags to control phases
input_active = True
instruction_active = False

# Global timing
global_start_time = None
global_end_time = None
break_start_time = None
break_end_time = None
break_duration_ms = 0

# Toggle fullscreen function
def toggle_fullscreen():
    """Toggle between fullscreen and windowed mode"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT
    screen_info = pygame.display.Info()

    if screen.get_flags() & pygame.FULLSCREEN:
        # Switch to windowed mode
        # Use 80% of screen size for windowed mode to ensure it fits
        window_width = int(screen_info.current_w * 0.8)
        window_height = int(screen_info.current_h * 0.8)

        # Ensure minimum size but not larger than screen
        SCREEN_WIDTH = max(1024, min(window_width, screen_info.current_w - 100))
        SCREEN_HEIGHT = max(768, min(window_height, screen_info.current_h - 100))

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Switched to windowed mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        # Switch to fullscreen mode
        SCREEN_WIDTH = screen_info.current_w
        SCREEN_HEIGHT = screen_info.current_h
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print(f"Switched to fullscreen mode: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Set up screen in fullscreen mode
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Mental Rotation Test")

# Fonts
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)

def get_participant_id(screen):
    global global_start_time
    global_start_time = time.time()
    input_text = ""
    active = True

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_fullscreen()
                elif event.key == pygame.K_RETURN and input_text != "":
                    active = False
                    print(f"Participant info: {input_text}")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.fill(GRAY_RGB)
        prompt = font_medium.render("Enter Participant ID (press enter when completed):", True, BLACK_RGB)
        text_surface = font_medium.render(input_text, True, BLACK_RGB)
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

    pygame.event.clear()
    return input_text

# Load instruction images
def load_instructions():
    instruction_objects = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.png")
        ins = Instruction(img_path)
        instruction_objects.append(ins)

    instruction_index = 0
    instruction_locked = True
    unlock_timer = pygame.time.get_ticks()

    if MODE == "actual":
        read_time = ACTUAL_READ_TIME
    elif MODE == "test":
        read_time = TEST_READ_TIME

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

        if current_time - unlock_timer >= read_time:
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

# Storage for all phases
phase_data = {
    "demo": [],
    "test1": [],
    "test2": []
}

def show_results(phase, result):
    waiting = True

    screen.fill((0, 0, 0))

    correct_count = 0
    for respond in result:
        correct_count += 1 if respond else 0
    accuracy = round(100 * correct_count / len(result), 2)

    text_surface1 = font_large.render(f'You are correct on {accuracy}% of the test.', True, (255, 255, 255))
    screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))

    if phase == "demo" or phase == "test1":
        if accuracy >= 90:
            suggestion = "Try to go faster!"
        elif accuracy >= 80:
            suggestion = "Maintain speed and accuracy!"
        else:
            suggestion = "Focus on being more accurate!"
        text_surface2 = font_medium.render(suggestion, True, (255, 255, 255))
        screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2, 300))

    pygame.display.flip()

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def run_trials(phase):
    if MODE == "actual":
        max_respond_time = ACTUAL_MAX_RESPOND_TIME
        feedback_time = ACTUAL_FEEDBACK_TIME
        if phase == "demo":
            if VERSION == 1:
                condition_path = f"{CONDITION_DIR}demo.csv"
            elif VERSION == 2:
                condition_path = f"{CONDITION_DIR}demo_flipped.csv"
        elif phase == "test1" or phase == "test2":
            if VERSION == 1:
                condition_path = f"{CONDITION_DIR}test.csv"
            elif VERSION == 2:
                condition_path = f"{CONDITION_DIR}test_flipped.csv"
    elif MODE == "test":
        max_respond_time = TEST_MAX_RESPOND_TIME
        feedback_time = TEST_FEEDBACK_TIME
        if phase == "demo":
            if VERSION == 1:
                condition_path = f"{CONDITION_DIR}demo.csv"
            elif VERSION == 2:
                condition_path = f"{CONDITION_DIR}demo_flipped.csv"
        elif phase == "test1" or phase == "test2":
            if VERSION == 1:
                condition_path = f"{CONDITION_DIR}test_short.csv"
            elif VERSION == 2:
                condition_path = f"{CONDITION_DIR}test_short_flipped.csv"

    feedback_icons = FeedbackIcon()

    # Read conditions from CSV files
    trial_conditions = []
    try:
        with open(condition_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trial_conditions.append({
                    "letter_name": row["letter_name"],
                    "rotation_angle": row["rotation_angle"],
                    "mirrored": row["mirrored"],
                    "condition": row["condition"],
                    "difficulty": row["difficulty"],
                    "stimuli_path": row["stimuli_path"],
                    "key_correct": row["key_correct"]
                })
    except Exception as e:
        print(f"Failed to read condition info for {phase}: {e}")
        return

    # Randomize trials
    random.shuffle(trial_conditions)

    record = []

    for idx, cond in enumerate(trial_conditions):
        try:
            img = pygame.image.load(cond["stimuli_path"])
            img = pygame.transform.scale(img, (200, 200))
        except Exception as e:
            print(f"Error loading image {cond['stimuli_path']}: {e}")
            continue

        # screen.fill((0, 0, 0))
        # img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        # screen.blit(img, img_rect)
        # pygame.display.flip()

        screen.fill((0, 0, 0))
        img = pygame.transform.scale(img, (200, 200))  # 缩放图像为 200x200
        img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(img, img_rect)

        label_font = pygame.font.SysFont(None, 48)
        if VERSION == 1:
            text_v = label_font.render("V (Normal)", True, (255, 255, 255))
            text_m = label_font.render("M (Mirrored)", True, (255, 255, 255))
        elif VERSION == 2:
            text_v = label_font.render("V (Mirrored)", True, (255, 255, 255))
            text_m = label_font.render("M (Normal)", True, (255, 255, 255))
        screen.blit(text_v, (SCREEN_WIDTH // 4 - text_v.get_width() // 2, SCREEN_HEIGHT - 400))
        screen.blit(text_m, (3 * SCREEN_WIDTH // 4 - text_m.get_width() // 2, SCREEN_HEIGHT - 400))

        pygame.display.flip()

        pygame.event.clear()
        trial_start = pygame.time.get_ticks()
        responded = False
        correct = False
        key_response = None
        key_locked = False

        trial_start = pygame.time.get_ticks()

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

        # Save result
        phase_data[phase].append({
            "item_number": idx + 1,
            "letter_name": cond["letter_name"],
            "rotation_angle": cond["rotation_angle"],
            "mirrored": cond["mirrored"],
            "condition": cond["condition"],
            "difficulty": cond["difficulty"],
            "stimuli_path": cond["stimuli_path"],
            "key_correct": cond["key_correct"],
            "key_response": key_response,
            "correct": int(correct),
            "reaction_time": reaction_time,
        })

        record.append(correct)

        # Show Feedback
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

def save_all_results():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    save_result_csv(["demo"], f"{participant_id}_demo_result.csv")
    save_result_csv(["test1", "test2"], f"{participant_id}_test_result.csv")

    print("All results saved!")

def save_result_csv(phases, filename):
    cumulative_id = 0
    filename = os.path.join(RESULT_DIR, filename)
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "participant_id", "version", "item_number", "block", "letter_name", "rotation_angle", "mirrored",
            "condition", "difficulty", "stimuli_path", "key_correct", "key_response",
            "correct", "reaction_time_ms", "start_time", "end_time", "break_duration_ms"
        ])

        for phase in phases:
            if phase == "demo":
                block = 0
            elif phase == "test1":
                block = 1
            elif phase == "test2":
                block = 2

            if phase_data[phase]:
                for trial in phase_data[phase]:
                    writer.writerow([
                        participant_id,
                        VERSION,
                        trial["item_number"] + cumulative_id,
                        block,
                        trial["letter_name"],
                        trial["rotation_angle"],
                        trial["mirrored"],
                        trial["condition"],
                        trial["difficulty"],
                        trial["stimuli_path"],
                        trial["key_correct"],
                        trial["key_response"],
                        trial["correct"],
                        trial["reaction_time"],
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_start_time)),
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_end_time)),
                        break_duration_ms
                    ])
                cumulative_id += len(phase_data[phase])
            else:
                print(f"No data to save for phase: {phase}")

# Main loop for participant input
global_start_time = time.time()

# Get participant ID
participant_id = get_participant_id(screen)

# Set VERSION / INSTRUCTION_DIR
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions") # Other (not specifically defined) participant use VERSION 1 (normal)
try:
    VERSION = int(participant_id[:-1])
    if VERSION % 2 == 1:
        VERSION = 1
        INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions") # Odd participant use VERSION 1 (normal)
    else:
        VERSION = 2
        INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions_reversed") # Even participant use VERSION 2 (reversed)
except:
    VERSION = 1
RESULT_DIR = os.path.join(SCRIPT_DIR, "results")
CONDITION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "conditions")

load_instructions()

global_end_time = time.time()

print("Task completed!")
