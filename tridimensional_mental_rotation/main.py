import pygame
import sys
import os
import csv
import time
import random
import pygame.event

from Instruction import Instruction
from FeedbackIcon import FeedbackIcon


# Meta-parameters
#MODE = "test"
MODE = "actual"

# Colors (RGB)
RED_RGB = (255, 72, 72) # FF4848
BLUE_RGB = (72, 197, 255) # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0, 0, 0) # 000000
GRAY_RGB = (128, 128, 128) # 808080
YELLOW_RGB = (255, 255, 0)

# Time settings
ACTUAL_READ_TIME = 1000
TEST_READ_TIME = 100
ACTUAL_MAX_RESPOND_TIME = 7500  # Maximum time to respond to stimulus (7.5 seconds)
TEST_MAX_RESPOND_TIME = 7500    # Same for test mode
ACTUAL_FEEDBACK_TIME = 500      # Blank screen between trials (0.5 seconds)
TEST_FEEDBACK_TIME = 500        # Same for test mode
FIXATION_TIME = 250             # Fixation cross duration (0.25 seconds)
ISI_TIME = 500                  # Inter-stimulus interval (blank screen between trials) (0.5 seconds)
FEEDBACK_DURATION = 1000        # Additional time to show feedback with stimulus (1 second)

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 20
DEMO_PAGE = 12
TEST1_PAGE = 15
TEST2_PAGE = 19

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

# Trial counters for continuous saving
trial_counters = {
    "demo": 0,
    "test1": 0,
    "test2": 0
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

    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen/windowed mode
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
                        print("✅ All trials completed and saved!")

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
        suffix = f"_{VERSION}"
    else:
        max_respond_time = TEST_MAX_RESPOND_TIME
        if phase == "demo":
            suffix = f"_{VERSION}"
        elif phase == "test1" or phase == "test2":
            suffix = f"_short_{VERSION}"

    condition_path = os.path.join(CONDITION_DIR, f"{phase}{suffix}.csv")
    feedback_icons = FeedbackIcon()

    # Initialize the results file for this phase
    initialize_results_file(phase)

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
                    "object_id": row["object_id"],
                    "rotation_angle": row["rotation_angle"],
                    "different": row["different"],
                    "condition": row["condition"],
                    "difficulty": row["difficulty"],
                    "stimuli_path": stimuli_absolute_path,
                    "key_correct": row["key_correct"]
                })
    except Exception as e:
        print(f"Failed to read condition info for {phase}: {e}")
        return None

    random.shuffle(trial_conditions)
    record = []

    for idx, cond in enumerate(trial_conditions):
        try:
            img = pygame.image.load(cond["stimuli_path"])
            img = pygame.transform.scale(img, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        except Exception as e:
            print(f"Error loading image {cond['stimuli_path']}: {e}")
            continue

        # 1. Show fixation cross for 250ms (using same style as cognitive_control)
        screen.fill(GRAY_RGB)  # Black background instead of gray
        
        # Create a larger fixation cross with thicker lines 
        # Draw horizontal line (larger and thicker)
        pygame.draw.line(screen, BLACK_RGB,
             (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2),
             (SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT // 2), 6)
        # Draw vertical line (larger and thicker)
        pygame.draw.line(screen, BLACK_RGB,
             (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40),
             (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40), 6)
        
        pygame.display.flip()
        pygame.time.delay(FIXATION_TIME)

        # 2. Show stimulus until response (max 7500ms)
        screen.fill(GRAY_RGB)
        img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(img, img_rect)

        label_font = pygame.font.SysFont(None, 48)
        if VERSION == 1:
            # Left side - D key
            text_D = label_font.render("D", True, BLACK_RGB)
            text_D_label = label_font.render("Same", True, BLACK_RGB)
            # Right side - K key
            text_K = label_font.render("K", True, BLACK_RGB)
            text_K_label = label_font.render("Different", True, BLACK_RGB)
        else:
            # Left side - D key
            text_D = label_font.render("D", True, BLACK_RGB)
            text_D_label = label_font.render("Different", True, BLACK_RGB)
            # Right side - K key
            text_K = label_font.render("K", True, BLACK_RGB)
            text_K_label = label_font.render("Same", True, BLACK_RGB)
        
        # Position letters and labels
        # Left side (D) - moved down and slightly more separated
        screen.blit(text_D, (SCREEN_WIDTH // 3.5 - text_D.get_width() // 2, SCREEN_HEIGHT - 250))
        screen.blit(text_D_label, (SCREEN_WIDTH // 3.5 - text_D_label.get_width() // 2, SCREEN_HEIGHT - 210))
        # Right side (K) - moved down and slightly more separated
        screen.blit(text_K, (2.5 * SCREEN_WIDTH // 3.5 - text_K.get_width() // 2, SCREEN_HEIGHT - 250))
        screen.blit(text_K_label, (2.5 * SCREEN_WIDTH // 3.5 - text_K_label.get_width() // 2, SCREEN_HEIGHT - 210))
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Toggle fullscreen/windowed mode during trials
                        toggle_fullscreen()
                    elif not responded and not key_locked:
                        if event.key == pygame.K_d:
                            responded = True
                            key_response = "d"
                            correct = (cond["key_correct"] == "d")
                            key_locked = True
                        elif event.key == pygame.K_k:
                            responded = True
                            key_response = "k"
                            correct = (cond["key_correct"] == "k")
                            key_locked = True
            if responded:
                break

        reaction_time = pygame.time.get_ticks() - trial_start

        # Create trial data
        trial_data = {
            "item_number": idx + 1,
            "object_id": cond["object_id"],
            "rotation_angle": cond["rotation_angle"],
            "different": cond["different"],
            "condition": cond["condition"],
            "difficulty": cond["difficulty"],
            "stimuli_path": cond["stimuli_path"],
            "key_correct": cond["key_correct"],
            "key_response": key_response,
            "correct": int(correct),
            "reaction_time": reaction_time,
            "trial_end_time": time.time()  # Add end time for this trial
        }

        # Save trial immediately to CSV file
        save_trial_immediately(phase, trial_data)
        
        # Also keep in memory for compatibility with show_results function
        phase_data[phase].append(trial_data)
        record.append(correct)

        # 3. Show feedback below stimulus for 200ms additional time (only in demo phase)
        if phase == "demo":
            # Keep the stimulus on screen and add feedback below it
            # The screen already has the stimulus, just add feedback below
            feedback_y_position = img_rect.bottom + 50  # 50 pixels below the stimulus
            
            if not responded:
                # Show "Too Slow!" in yellow
                feedback_text = font_medium.render("Too Slow!", True, YELLOW_RGB)  # Yellow color
                feedback_rect = feedback_text.get_rect(center=(SCREEN_WIDTH // 2, feedback_y_position))
                screen.blit(feedback_text, feedback_rect)
            else:
                # Show correct/incorrect icon below stimulus
                feedback_img = feedback_icons.correct_icon if correct else feedback_icons.incorrect_icon
                feedback_rect = feedback_img.get_rect(center=(SCREEN_WIDTH // 2, feedback_y_position))
                screen.blit(feedback_img, feedback_rect)
            
            pygame.display.flip()
            pygame.time.delay(FEEDBACK_DURATION)  # 200ms additional feedback time
        
        # 4. ISI - Blank black screen between trials (500ms)
        screen.fill(GRAY_RGB)
        pygame.display.flip()
        pygame.time.delay(ISI_TIME)  # 500ms blank screen using new ISI_TIME

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen/windowed mode
                    toggle_fullscreen()
                elif event.key == pygame.K_SPACE:
                    waiting = False

def initialize_results_file(phase):
    """Initialize CSV file with headers at the start of each phase"""
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    
    # Automatic file versioning system
    global results_filename
    base_filename = f"{participant_id}_3D_results.csv"
    filepath = os.path.join(RESULT_DIR, base_filename)
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    if not os.path.exists(filepath):
        results_filename = base_filename
    else:
        name_part, ext = os.path.splitext(base_filename)
        version = 2
        while True:
            versioned_filename = f"{name_part}_{version}{ext}"
            versioned_filepath = os.path.join(RESULT_DIR, versioned_filename)
            if not os.path.exists(versioned_filepath):
                results_filename = versioned_filename
                break
            version += 1
    # Create the new file with headers only if it doesn't exist
    filepath = os.path.join(RESULT_DIR, results_filename)
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant_id", "version", "mode", "item_number", "block", "object_id", "rotation_angle", "different",
                "condition", "difficulty", "stimuli_path", "key_correct", "key_response",
                "correct", "reaction_time_ms", "start_time", "end_time", "break_duration_ms"
            ])
        print(f"✅ Initialized results file: {results_filename}")

def save_trial_immediately(phase, trial_data):
    """Save a single trial immediately to CSV file"""
    global results_filename
    # Set block names and cumulative IDs
    if phase == "demo":
        block = "practice"
        cumulative_id = trial_counters["demo"]
    elif phase == "test1":
        block = "block1"
        cumulative_id = trial_counters["demo"] + trial_counters["test1"]
    elif phase == "test2":
        block = "block2"
        cumulative_id = trial_counters["demo"] + trial_counters["test1"] + trial_counters["test2"]
    # Set mode value based on MODE variable
    mode_value = "full" if MODE == "actual" else "demo"
    filepath = os.path.join(RESULT_DIR, results_filename)
    # Append the trial data to the file
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            participant_id,
            VERSION,
            mode_value,
            trial_data["item_number"] + cumulative_id,
            block,
            trial_data["object_id"],
            trial_data["rotation_angle"],
            trial_data["different"],
            trial_data["condition"],
            trial_data["difficulty"],
            trial_data["stimuli_path"],
            trial_data["key_correct"],
            trial_data["key_response"],
            trial_data["correct"],
            trial_data["reaction_time"],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_start_time)),
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trial_data["trial_end_time"])),
            break_duration_ms if phase == "test2" else 0
        ])
    # Increment the trial counter for this phase
    trial_counters[phase] += 1
    print(f"✅ Saved trial {trial_counters[phase]} for phase {phase}")

# Get participant ID
participant_id = get_participant_id(screen)

# Set VERSION / INSTRUCTION_DIR
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions") # Other (not specifically defined) participant use VERSION 1 (normal)
try:
    VERSION = int(participant_id[-1])
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
