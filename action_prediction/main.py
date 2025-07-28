import pygame
import sys
import os
import csv
import time
import random
import pygame.event
import cv2

from Instruction import Instruction
from FeedbackIcon import FeedbackIcon

# Initialize pygame
pygame.init()

# Time settings
ACTUAL_READ_TIME = 10000
TEST_READ_TIME = 100
ACTUAL_MAX_RESPOND_TIME = 5000
TEST_MAX_RESPOND_TIME = 2000
ACTUAL_FEEDBACK_TIME = 2000
TEST_FEEDBACK_TIME = 500
FIXATION_CROSS = 500

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 11
DEMO_PAGE = 6
TEST1_PAGE = 8
TEST2_PAGE = 10

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

def load_instructions():
    instruction_objects = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.png")
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

            screen.fill((0, 0, 0))
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
            screen.fill((0, 0, 0))

            # Render V/M options
            label_font = pygame.font.SysFont(None, 48)
            if VERSION == 1:
                text_v = label_font.render("V (Left)", True, (255, 255, 255))
                text_m = label_font.render("M (Right)", True, (255, 255, 255))
            else:
                text_v = label_font.render("V (Right)", True, (255, 255, 255))
                text_m = label_font.render("M (Left)", True, (255, 255, 255))
            screen.blit(text_v, (SCREEN_WIDTH // 4 - text_v.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_m, (3 * SCREEN_WIDTH // 4 - text_m.get_width() // 2, SCREEN_HEIGHT // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        key_response = "v"
                        responded = True
                        correct = (cond["key_correct"] == "v")
                    elif event.key == pygame.K_m:
                        key_response = "m"
                        responded = True
                        correct = (cond["key_correct"] == "m")
            pygame.time.delay(10)

        reaction_time = pygame.time.get_ticks() - respond_start

        # -------- Phase 3: Show feedback --------
        if phase == "demo":
            screen.fill((0, 0, 0))
            if not responded:
                feedback_img = feedback_icons.timeout_icon
            else:
                feedback_img = feedback_icons.correct_icon if correct else feedback_icons.incorrect_icon
            feedback_rect = feedback_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(feedback_img, feedback_rect)
            pygame.display.flip()
            pygame.time.delay(feedback_time)

        elif phase in ["test1", "test2"]:
            screen.fill((0, 0, 0))
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

# Participant input
global_start_time = time.time()

id_recieved = False
mode_selected = False
version_selected = False
participant_info = ""
VERSION = 0

def input_id():
    global participant_info, id_recieved
    participant_info = ""
    input_active = True

    # Record the start time of the experiment
    global global_start_time
    global_start_time = time.time()

    while input_active:
        for event in pygame.event.get():
            # Handle window close event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle keyboard inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Exit input loop when space is pressed
                    print(f"Participant info: {participant_info}")
                    input_active = False
                    id_recieved = True  # Mark ID as received
                elif event.key == pygame.K_BACKSPACE:
                    # Remove the last character when backspace is pressed
                    participant_info = participant_info[:-1]
                else:
                    # Append any other character to the participant ID
                    participant_info += event.unicode

        # Clear the screen
        screen.fill((255, 255, 255))

        # Render instruction text
        text_surface1 = font_large.render("[For Operator] Type participant group & ID (e.g., YC_001)", True, (0, 0, 0))
        text_surface2 = font_medium.render("Press [space] when you complete.", True, (0, 0, 0))
        input_surface = font_medium.render(participant_info, True, (0, 0, 255))

        # Center the text on the screen
        screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))
        screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2, 300))
        screen.blit(input_surface, (SCREEN_WIDTH // 2 - input_surface.get_width() // 2, 500))

        # Update the display
        pygame.display.flip()

    pygame.event.clear()  # Clear event queue to prevent key leak
    print("✅ Participant ID entered successfully.")

def input_mode():
    global MODE, mode_selected
    input_active = True

    while input_active and not mode_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    MODE = "actual"
                    print("Mode selected: ACTUAL")
                    mode_selected = True
                    input_active = False
                elif event.key == pygame.K_2:
                    MODE = "test"
                    print("Mode selected: TEST")
                    mode_selected = True
                    input_active = False

        # Clear the screen
        screen.fill((255, 255, 255))

        # Render instruction text
        text_surface1 = font_large.render("[For Operator] Select MODE", True, (0, 0, 0))
        text_surface2 = font_medium.render("1 - actual task / 2 - test", True, (0, 0, 0))

        # Center the text on the screen
        screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))
        screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2, 300))
        
        # Update the display
        pygame.display.flip()

    pygame.event.clear()  # Clear event queue to prevent key leak
    print("✅ Task mode entered successfully.")


def input_version():
    global VERSION, version_selected
    input_active = True

    while input_active and not version_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    VERSION = 1
                    print("Version selected: 1")
                    version_selected = True
                    input_active = False
                elif event.key == pygame.K_2:
                    VERSION = 2
                    print("Version selected: 2")
                    version_selected = True
                    input_active = False

        # Clear the screen
        screen.fill((255, 255, 255))

        # Render instruction text
        text_surface1 = font_large.render("[For Operator] Select VERSION", True, (0, 0, 0))
        text_surface2 = font_medium.render("1 - normal / 2 - flipped", True, (0, 0, 0))

        # Center the text on the screen
        screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))
        screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2, 300))
        
        # Update the display
        pygame.display.flip()

    pygame.event.clear()  # Clear event queue to prevent key leak
    print("✅ Test version entered successfully.")

# Get participant ID
input_id()

# Get test mode
if id_recieved:
    input_mode()

# Get test version
if mode_selected:
    input_version()

# Load instructions if version is received
if version_selected:
    # Set file paths according to version
    if VERSION == 1:
        INSTRUCTION_DIR = "./stimuli/instructions/"
    elif VERSION == 2:
        INSTRUCTION_DIR = "./stimuli/instructions_reversed/"
    RESULT_DIR = "./results/"
    CONDITION_DIR = "./stimuli/conditions/"

    load_instructions()

global_end_time = time.time()
print("Task completed!")
