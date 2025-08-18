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
##MODE = "test"
MODE = "actual"

# Colors (RGB)
RED_RGB = (255, 72, 72) # FF4848
BLUE_RGB = (72, 197, 255) # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0, 0, 0) # 000000
GRAY_RGB = (128, 128, 128) # 808080
YELLOW_RGB = (255, 255, 0)

# Time settings
ACTUAL_READ_TIME = 1000  # Reduced from 10000ms to 1000ms (1 second)
TEST_READ_TIME = 100
ACTUAL_MAX_RESPOND_TIME = 5000
TEST_MAX_RESPOND_TIME = 2000
ACTUAL_FEEDBACK_TIME = 1000  # Changed to 1000ms (1 second)
TEST_FEEDBACK_TIME = 1000    # Changed to 1000ms (1 second)
FIXATION_CROSS = 500

# Instruction and task settings
TOTAL_INSTRUCTION_PAGES = 19  # Extended for 4 blocks
DEMO_PAGE = 7
TEST1_PAGE = 10
BREAK1_PAGE = 13
TEST2_PAGE = 14
BREAK2_PAGE = 16
TEST3_PAGE = 17
BREAK3_PAGE = 18
TEST4_PAGE = 19

# Participant info
participant_info = ""
input_active = True
instruction_active = False

global_start_time = None
# Global variable to track unique filename across all trials
unique_filename = None
global_end_time = None
break_start_time = None
break_end_time = None
break_duration_ms = 0

# Phase data
phase_data = {
    "demo": [],
    "test1": [],
    "test2": [],
    "test3": [],
    "test4": []
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
                    if instruction_index >= TEST4_PAGE:
                        # If we're at the final screens, ESC should exit immediately
                        running = False
                    else:
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
                    elif instruction_index == BREAK1_PAGE:
                        # Break before test2
                        global break_start_time
                        break_start_time = time.time()
                    elif instruction_index == TEST2_PAGE:
                        global break_end_time, break_duration_ms
                        break_end_time = time.time()
                        break_duration_ms = int((break_end_time - break_start_time) * 1000)
                        result = run_trials("test2")
                        show_results("test2", result)
                    elif instruction_index == BREAK2_PAGE:
                        # Break before test3
                        pass  # Just transition page
                    elif instruction_index == TEST3_PAGE:
                        result = run_trials("test3")
                        show_results("test3", result)
                    elif instruction_index == BREAK3_PAGE:
                        # Break before test4
                        pass  # Just transition page
                    elif instruction_index == TEST4_PAGE:
                        result = run_trials("test4")
                        show_results("test4", result)
                        save_all_results()
                    elif instruction_index >= TOTAL_INSTRUCTION_PAGES:
                        # Final completion screen
                        running = False  # Exit the experiment

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
        elif instruction_index > TOTAL_INSTRUCTION_PAGES:
            # Show final completion screen
            screen.fill(GRAY_RGB)
            completion_text = font_large.render("Task completed!", True, BLACK_RGB)
            thanks_text = font_medium.render("Thank you for participating!", True, BLACK_RGB)
            instruction_text = font_medium.render("Press SPACE to exit", True, BLACK_RGB)
            
            screen.blit(completion_text, (SCREEN_WIDTH // 2 - completion_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(thanks_text, (SCREEN_WIDTH // 2 - thanks_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
            pygame.display.flip()

def run_trials(phase):
    if MODE == "actual":
        max_respond_time = ACTUAL_MAX_RESPOND_TIME
        feedback_time = ACTUAL_FEEDBACK_TIME
        # For actual mode, use full test files for all 4 blocks
        if phase == "demo":
            suffix = "" if VERSION == 1 else "_flipped"
        elif phase in ["test1", "test2", "test3", "test4"]:
            suffix = "" if VERSION == 1 else "_flipped"
    else:
        max_respond_time = TEST_MAX_RESPOND_TIME
        feedback_time = TEST_FEEDBACK_TIME
        if phase == "demo":
            suffix = "" if VERSION == 1 else "_flipped"
        elif phase in ["test1", "test2"]:
            suffix = "_short" if VERSION == 1 else "_short_flipped"
        # For test mode, test3 and test4 don't exist, so return empty
        elif phase in ["test3", "test4"]:
            return []

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
        # Fix relative path to be absolute
        video_path = cond["stimuli_path"]
        if video_path.startswith("./"):
            video_path = os.path.join(SCRIPT_DIR, video_path[2:])  # Remove "./" and make absolute
        
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
        # Clear cache but preserve ESC events to avoid key leak
        escape_events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                escape_events.append(event)
        
        # Re-post any ESC events that were in the queue
        for event in escape_events:
            pygame.event.post(event)
            
        responded = False
        correct = False
        key_response = None
        respond_start = pygame.time.get_ticks()

        while not responded and (pygame.time.get_ticks() - respond_start < max_respond_time):
            screen.fill(GRAY_RGB)

            # Render D/K options
            label_font = pygame.font.SysFont(None, 72)  # Same font size for both letters and direction labels
            
            # Render letters
            text_d = label_font.render("D", True, BLACK_RGB)
            text_k = label_font.render("K", True, BLACK_RGB)
            
            # Render direction labels without parentheses and in lowercase
            text_left = label_font.render("left", True, BLACK_RGB)
            text_right = label_font.render("right", True, BLACK_RGB)
            
            # Position letters closer together and more centered
            spacing = 200  # Increased spacing between D and K
            center_x = SCREEN_WIDTH // 2
            d_x = center_x - spacing - text_d.get_width() // 2
            k_x = center_x + spacing - text_k.get_width() // 2
            letter_y = SCREEN_HEIGHT // 2 - 30
            
            # Position direction labels below letters
            left_x = center_x - spacing - text_left.get_width() // 2
            right_x = center_x + spacing - text_right.get_width() // 2
            direction_y = letter_y + 50
            
            # Draw everything
            screen.blit(text_d, (d_x, letter_y))
            screen.blit(text_k, (k_x, letter_y))
            screen.blit(text_left, (left_x, direction_y))
            screen.blit(text_right, (right_x, direction_y))

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
            # Show feedback on the same screen as D/K mapping
            screen.fill(GRAY_RGB)
            
            # Render D/K options (same as response phase)
            label_font = pygame.font.SysFont(None, 72)
            
            # Render letters
            text_d = label_font.render("D", True, BLACK_RGB)
            text_k = label_font.render("K", True, BLACK_RGB)
            
            # Render direction labels without parentheses and in lowercase
            text_left = label_font.render("left", True, BLACK_RGB)
            text_right = label_font.render("right", True, BLACK_RGB)
            
            # Position letters
            spacing = 200
            center_x = SCREEN_WIDTH // 2
            d_x = center_x - spacing - text_d.get_width() // 2
            k_x = center_x + spacing - text_k.get_width() // 2
            letter_y = SCREEN_HEIGHT // 2 - 30
            
            # Position direction labels below letters
            left_x = center_x - spacing - text_left.get_width() // 2
            right_x = center_x + spacing - text_right.get_width() // 2
            direction_y = letter_y + 50
            
            # Draw D/K mapping
            screen.blit(text_d, (d_x, letter_y))
            screen.blit(text_k, (k_x, letter_y))
            screen.blit(text_left, (left_x, direction_y))
            screen.blit(text_right, (right_x, direction_y))
            
            # Add feedback icon/text below the mapping
            if not responded:
                # Show "Too Slow" text in yellow like cognitive control
                feedback_font = pygame.font.SysFont(None, 48)
                feedback_text = feedback_font.render("Too Slow", True, YELLOW_RGB)
                feedback_y = direction_y + 80
                feedback_rect = feedback_text.get_rect(center=(center_x, feedback_y))
                screen.blit(feedback_text, feedback_rect)
            else:
                feedback_img = feedback_icons.correct_icon if correct else feedback_icons.incorrect_icon
                feedback_y = direction_y + 80  # Position feedback below the direction labels
                feedback_rect = feedback_img.get_rect(center=(center_x, feedback_y))
                screen.blit(feedback_img, feedback_rect)
            
            pygame.display.flip()
            pygame.time.delay(1000)  # Use same duration as cognitive control (1000ms)

        elif phase in ["test1", "test2"]:
            screen.fill(GRAY_RGB)
            pygame.display.flip()
            pygame.time.delay(feedback_time)

        # -------- Record result --------
        trial_data = {
            "item_number": idx + 1,
            "player_name": cond["player_name"],
            "miss_goal": cond["miss_goal"],
            "left_right": cond["left_right"],
            "condition": cond["condition"],
            "difficulty": cond["difficulty"],  # Use difficulty directly from CSV (easy/hard)
            "stimuli_path": cond["stimuli_path"],
            "key_correct": cond["key_correct"],
            "key_response": key_response,
            "correct": int(correct),
            "reaction_time": reaction_time,
        }
        
        # Add to phase data (for backward compatibility)
        phase_data[phase].append(trial_data)
        
        # Save immediately to CSV (like cognitive control)
        save_single_trial(trial_data, phase)
        
        record.append(correct)

    return record

def show_results(phase, result):
    if not result:  # Check if result list is empty
        print(f"No valid trials completed for {phase} phase")
        return
    
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
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    toggle_fullscreen()

def get_unique_filename(base_filename):
    """
    Automatic file versioning system:
    - Creates standard filename format [participantID]_SOC_results.csv
    - Checks if file already exists in results directory
    - If exists, appends _2, _3, _4, etc. until finding available filename
    - Returns the unique filename for global tracking
    """
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    
    # Start with base filename
    filepath = os.path.join(RESULT_DIR, base_filename)
    
    # If file doesn't exist, use the base filename
    if not os.path.exists(filepath):
        return base_filename
    
    # If file exists, find the next available version
    name_part, ext = os.path.splitext(base_filename)
    version = 2
    
    while True:
        versioned_filename = f"{name_part}_{version}{ext}"
        versioned_filepath = os.path.join(RESULT_DIR, versioned_filename)
        
        if not os.path.exists(versioned_filepath):
            return versioned_filename
        
        version += 1

def save_single_trial(trial_data, phase):
    """Save a single trial result immediately to CSV"""
    global unique_filename
    
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    
    # Initialize unique filename on first trial if not already set
    if unique_filename is None:
        base_filename = f"{participant_info}_SOC_results.csv"
        unique_filename = get_unique_filename(base_filename)
    
    # Use the globally tracked unique filename
    filepath = os.path.join(RESULT_DIR, unique_filename)
    
    # Determine block and type values following cognitive control pattern
    if phase == "demo":
        block = "practice"
        type_value = "practice"
    elif phase == "test1":
        block = "block1"
        type_value = "test"
    elif phase == "test2":
        block = "block2"
        type_value = "test"
    elif phase == "test3":
        block = "block3"
        type_value = "test"
    elif phase == "test4":
        block = "block4"
        type_value = "test"
    
    # Check if file exists to determine if we need to write header
    file_exists = os.path.exists(filepath)
    
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        
        # Write header if file doesn't exist
        if not file_exists:
            writer.writerow([
                "participant_id", "version", "item_number", "block", "type", "player_name", "miss_goal", "left_right",
                "condition", "difficulty", "stimuli_path", "key_correct", "key_response",
                "correct", "reaction_time_ms", "start_time", "end_time", "break_duration_ms"
            ])
        
        # Write trial data
        writer.writerow([
            participant_info,
            VERSION,
            trial_data["item_number"],
            block,
            type_value,
            trial_data["player_name"],
            trial_data["miss_goal"],
            trial_data["left_right"],
            trial_data["condition"],
            trial_data["difficulty"],
            trial_data["stimuli_path"],
            trial_data["key_correct"],
            trial_data["key_response"],
            trial_data["correct"],
            trial_data["reaction_time"],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_start_time)),
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_end_time)) if global_end_time else "",
            break_duration_ms
        ])

def save_all_results():
    """Save all results to single file (backward compatibility function)"""
    global unique_filename
    
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    # Use the same unique filename that was established during trials
    if unique_filename is None:
        base_filename = f"{participant_info}_SOC_results.csv"
        unique_filename = get_unique_filename(base_filename)

    # Save all phases including the 4 test blocks for actual mode
    if MODE == "actual":
        save_result_csv(["demo", "test1", "test2", "test3", "test4"], unique_filename)
    else:
        save_result_csv(["demo", "test1", "test2"], unique_filename)

def save_result_csv(phases, filename):
    cumulative_id = 0
    filepath = os.path.join(RESULT_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "participant_id", "version", "item_number", "block", "type", "player_name", "miss_goal", "left_right",
            "condition", "difficulty", "stimuli_path", "key_correct", "key_response",
            "correct", "reaction_time_ms", "start_time", "end_time", "break_duration_ms"
        ])

        for phase in phases:
            # Determine block and type values following cognitive control pattern
            if phase == "demo":
                block = "practice"
                type_value = "practice"
            elif phase == "test1":
                block = "block1"
                type_value = "test"
            elif phase == "test2":
                block = "block2"
                type_value = "test"
            elif phase == "test3":
                block = "block3"
                type_value = "test"
            elif phase == "test4":
                block = "block4"
                type_value = "test"

            for trial in phase_data[phase]:
                writer.writerow([
                    participant_info,
                    VERSION,
                    trial["item_number"] + cumulative_id,
                    block,
                    type_value,
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

# Initialize default values first
VERSION = 1
INSTRUCTION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "instructions")
RESULT_DIR = os.path.join(SCRIPT_DIR, "results")
CONDITION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "conditions")

# Get participant ID
participant_id = get_participant_id(screen)
participant_info = participant_id  # Set participant_info

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

load_instructions()

# Set end time
global_end_time = time.time()
print("Task completed!")
