import pygame
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
import csv
import time
import random
import pygame.event
import cv2

from Instruction import Instruction
from FeedbackIcon import FeedbackIcon

# Meta-parameters
MODE = "test"
# MODE = "actual"

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
FIXATION_CROSS = 500

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 15
DEMO_PAGE = 7
TEST1_PAGE = 10
TEST2_PAGE = 14

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

# Initialize pygame
pygame.init()

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

def load_instructions():
    instruction_objects = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.jpg")
        instruction_objects.append(Instruction(img_path))

    instruction_index = 0
    instruction_locked = True
    unlock_timer = pygame.time.get_ticks()
    READ_TIME = ACTUAL_READ_TIME if MODE == "actual" else TEST_READ_TIME

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_fullscreen()
                elif event.key == pygame.K_SPACE and not instruction_locked:
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

        screen.fill(GRAY_RGB)
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
        elif phase in ["test1", "test2"]:
            suffix = "_short" if VERSION == 1 else "_short_flipped"

    condition_path = os.path.join(CONDITION_DIR, f"{phase}{suffix}.csv")
    feedback_icons = FeedbackIcon()

    trial_conditions = []
    try:
        with open(condition_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trial_conditions.append({
                    "player_name": row["player_name"],
                    "miss_goal": row["miss_goal"],
                    "left_right": row["left_right"],
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
        video_path = cond["stimuli_path"]
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            continue

        # -------- Phase 1: Play full video --------
        cap = cv2.VideoCapture(video_path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (850, 475))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            screen.fill(GRAY_RGB)
            img_rect = frame_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(frame_surface, img_rect)
            pygame.display.flip()
            pygame.time.delay(30)
        cap.release()

        # -------- Fixation delay before response page --------
        pygame.time.delay(FIXATION_CROSS)

        # -------- Phase 2: Show response page --------
        pygame.event.clear()  # clear cache to avoid key leak
        responded = False
        correct = False
        key_response = None
        respond_start = pygame.time.get_ticks()

        while not responded and (pygame.time.get_ticks() - respond_start < max_respond_time):
            screen.fill(GRAY_RGB)

            # Render V/M options
            label_font = pygame.font.SysFont(None, 48)
            if VERSION == 1:
                text_d = label_font.render("D (Left)", True, BLACK_RGB)
                text_k = label_font.render("K (Right)", True, BLACK_RGB)
            else:
                text_d = label_font.render("D (Right)", True, BLACK_RGB)
                text_k = label_font.render("K (Left)", True, BLACK_RGB)
            screen.blit(text_d, (SCREEN_WIDTH // 4 - text_d.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_k, (3 * SCREEN_WIDTH // 4 - text_k.get_width() // 2, SCREEN_HEIGHT // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        toggle_fullscreen()
                    elif event.key == pygame.K_d:
                        key_response = "d"
                        responded = True
                        correct = (cond["key_correct"] == "d")
                    elif event.key == pygame.K_k:
                        key_response = "k"
                        responded = True
                        correct = (cond["key_correct"] == "k")
            pygame.time.delay(10)

        reaction_time = pygame.time.get_ticks() - respond_start

        # -------- Phase 3: Show feedback --------
        if phase == "demo":
            screen.fill(GRAY_RGB)
            if not responded:
                feedback_img = feedback_icons.timeout_icon
            else:
                feedback_img = feedback_icons.correct_icon if correct else feedback_icons.incorrect_icon
            feedback_rect = feedback_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(feedback_img, feedback_rect)
            pygame.display.flip()
            pygame.time.delay(feedback_time)

        elif phase in ["test1", "test2"]:
            screen.fill(GRAY_RGB)
            pygame.display.flip()
            pygame.time.delay(feedback_time)

        # -------- Record result --------
        phase_data[phase].append({
            "item_number": idx + 1,
            "player_name": cond["player_name"],
            "miss_goal": cond["miss_goal"],
            "left_right": cond["left_right"],
            "condition": cond["condition"],
            "difficulty": "easy" if cond["difficulty"] == 0 else 1,
            "stimuli_path": cond["stimuli_path"],
            "key_correct": cond["key_correct"],
            "key_response": key_response,
            "correct": int(correct),
            "reaction_time": reaction_time,
        })

        record.append(correct)

    return record

def show_results(phase, result):
    correct_count = sum(1 for r in result if r)
    accuracy = round(100 * correct_count / len(result), 2)

    screen.fill(GRAY_RGB)
    text_surface1 = font_large.render(f'You are correct on {accuracy}% of the test.', True, BLACK_RGB)
    screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))

    if phase in ["demo", "test1"]:
        if accuracy >= 90:
            suggestion = "Try to go faster!"
        elif accuracy >= 80:
            suggestion = "Maintain speed and accuracy!"
        else:
            suggestion = "Focus on being more accurate!"
        text_surface2 = font_medium.render(suggestion, True, BLACK_RGB)
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
            "participant_id", "version", "item_number", "block", "player_name", "miss_goal", "left_right",
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

            for trial in phase_data[phase]:
                writer.writerow([
                    participant_info,
                    VERSION,
                    trial["item_number"] + cumulative_id,
                    block,
                    trial["player_name"],
                    trial["miss_goal"],
                    trial["left_right"],
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

# Get participant ID
participant_id = get_participant_id(screen)

try:
    VERSION = int(participant_id[-1])
    if VERSION % 2 == 1:
        VERSION = 1
        INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions")
    else:
        VERSION = 2
        INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions_reversed")
except:
    VERSION = 1
    INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions")

RESULT_DIR = os.path.join(SCRIPT_DIR, "results")
CONDITION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "conditions")

load_instructions()

# Participant input
global_start_time = time.time()
global_end_time = time.time()
print("Task completed!")
