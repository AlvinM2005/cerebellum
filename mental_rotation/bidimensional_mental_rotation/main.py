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

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Meta parameters
# MODE = "actual" # Use when running the real experiment
MODE = "test"  # Use when testing

# Time settings
ACTUAL_READ_TIME = 100
TEST_READ_TIME = 100
ACTUAL_MAX_RESPOND_TIME = 5000
TEST_MAX_RESPOND_TIME = 2000
ACTUAL_FEEDBACK_TIME = 2000
TEST_FEEDBACK_TIME = 500

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 12
DEMO_PAGE = 7
TEST1_PAGE = 9
TEST2_PAGE = 11

# Set up the screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mental Rotation Test")

# Set up fonts
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)

# Participant info
participant_info = ""

# Flags to control phases
input_active = True
instruction_active = False

# Global timing
global_start_time = None
global_end_time = None
break_start_time = None
break_end_time = None
break_duration_ms = 0

# Load instruction images
def load_instructions():
    instruction_objects = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, str(i) + ".png")
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

    # Handle empty results
    if not result or len(result) == 0:
        accuracy = 0
        text_surface1 = font_large.render(f'No valid trials completed.', True, (255, 255, 255))
    else:
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
                condition_path = os.path.join(CONDITION_DIR, "demo.csv")
            elif VERSION == 2:
                condition_path = os.path.join(CONDITION_DIR, "demo_flipped.csv")
        elif phase == "test1" or phase == "test2":
            if VERSION == 1:
                condition_path = os.path.join(CONDITION_DIR, "test_corrected.csv")
            elif VERSION == 2:
                condition_path = os.path.join(CONDITION_DIR, "test_corrected_flipped.csv")
    elif MODE == "test":
        max_respond_time = TEST_MAX_RESPOND_TIME
        feedback_time = TEST_FEEDBACK_TIME
        if phase == "demo":
            if VERSION == 1:
                condition_path = os.path.join(CONDITION_DIR, "demo.csv")
            elif VERSION == 2:
                condition_path = os.path.join(CONDITION_DIR, "demo_flipped.csv")
        elif phase == "test1" or phase == "test2":
            if VERSION == 1:
                condition_path = os.path.join(CONDITION_DIR, "test_short.csv")
            elif VERSION == 2:
                condition_path = os.path.join(CONDITION_DIR, "test_short_flipped.csv")

    feedback_icons = FeedbackIcon()

    # Read conditions from CSV files
    trial_conditions = []
    try:
        with open(condition_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert relative path to absolute path
                stimuli_relative_path = row["stimuli_path"]
                if stimuli_relative_path.startswith("./"):
                    # Remove "./" and join with script directory
                    stimuli_relative_path = stimuli_relative_path[2:]  # Remove "./"
                    stimuli_absolute_path = os.path.join(SCRIPT_DIR, stimuli_relative_path)
                else:
                    stimuli_absolute_path = os.path.join(SCRIPT_DIR, stimuli_relative_path)
                
                trial_conditions.append({
                    "letter_name": row["letter_name"],
                    "rotation_angle": row["rotation_angle"],
                    "mirrored": row["mirrored"],
                    "condition": row["condition"],
                    "difficulty": row["difficulty"],
                    "stimuli_path": stimuli_absolute_path,
                    "key_correct": row["key_correct"]
                })
    except Exception as e:
        print(f"Failed to read condition info for {phase}: {e}")
        return []

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

    save_result_csv(["demo"],f"{participant_info}_demo_result.csv")
    save_result_csv(["test1", "test2"],f"{participant_info}_test_result.csv")

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
                        participant_info,
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

id_recieved = False
version_recieved = False
participant_info = ""
version = ""

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

    print("✅ Participant ID entered successfully.")

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
    # Set file paths according to version using absolute paths
    if VERSION == 1:
        INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions")
    elif VERSION == 2:
        INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions_reversed")
    RESULT_DIR = os.path.join(SCRIPT_DIR, "results")
    CONDITION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "conditions")

    load_instructions()

global_end_time = time.time()
print("Task completed!")
