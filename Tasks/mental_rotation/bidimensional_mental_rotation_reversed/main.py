import pygame
import sys
import os
import csv
import time
from Instruction import Instruction
from TrialConditions import TrialConditions
from FeedbackIcon import FeedbackIcon

# Initialize pygame
pygame.init()

# Meta parameters
# MODE = "actual" # Use when running the real experiment
MODE = "test"  # Use when testing

# Time settings
ACTUAL_READ_TIME = 10000
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

# Paths
INSTRUCTION_DIR = "./stimuli/instructions/"
RESULT_DIR = "./results/"
CONDITION_DIR = "./stimuli/conditions/"

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

# Welcome messages
welcome_text1 = "[For Operator] Type participant group & ID (e.g., YC_001)"
welcome_text2 = "Press the semicolon (';') when you complete."

# Flags to control phases
input_active = True
instruction_active = False

# Global timing
global_start_time = None
global_end_time = None
break_start_time = None
break_end_time = None
break_duration_s = 0

# Load instruction images
def load_instructions(mode):
    instruction_objects = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.png")
        ins = Instruction(img_path)
        instruction_objects.append(ins)

    instruction_index = 0
    instruction_locked = True
    unlock_timer = pygame.time.get_ticks()

    if mode == "actual":
        READ_TIME = ACTUAL_READ_TIME
    else:
        READ_TIME = TEST_READ_TIME

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
                        global break_end_time, break_duration_s
                        break_end_time = time.time()
                        break_duration_s = int((break_end_time - break_start_time))
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

# Storage for all phases
phase_data = {
    "demo": [],
    "test1": [],
    "test2": []
}

def show_results(phase, result):
    waiting = True

    screen.fill((255, 255, 255))

    correct_count = 0
    for respond in result:
        correct_count += 1 if respond else 0
    accuracy = round(100 * correct_count / len(result), 2)

    text_surface1 = font_large.render(f'You are correct on {accuracy}% of the test.', True, (0, 0, 0))
    screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))

    if phase == "demo" or phase == "test1":
        if accuracy >= 90:
            suggestion = "Try to go faster!"
        elif accuracy >= 80:
            suggestion = "Maintain speed and accuracy!"
        else:
            suggestion = "Focus on being more accurate!"
        text_surface2 = font_medium.render(suggestion, True, (0, 0, 0))
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
        image_dir = f"./stimuli/images/{phase}_images/"
        answer_path = f"./stimuli/answers/{phase}_answer.txt"
        condition_path = f"{CONDITION_DIR}{phase}_conditions.csv"
    else:
        max_respond_time = TEST_MAX_RESPOND_TIME
        feedback_time = TEST_FEEDBACK_TIME
        image_dir = f"./stimuli/images/{phase}_images_short/"
        answer_path = f"./stimuli/answers/{phase}_answer_short.txt"
        condition_path = f"{CONDITION_DIR}{phase}_conditions_short.csv"

    feedback_icons = FeedbackIcon()

    try:
        with open(answer_path, "r") as f:
            answers = [line.strip() for line in f.readlines() if line.strip()]
    except:
        print(f"Failed to read answers for {phase}")
        return

    trial_conditions = []
    for i in range(1, len(answers)+1):
        img_path = os.path.join(image_dir, f"{i}.png")
        if os.path.exists(img_path):
            mirrored = True if answers[i-1] == "1" else False
            cond = TrialConditions(img_path, mirrored)
            trial_conditions.append(cond)

    condition_info = []
    try:
        with open(condition_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                condition_info.append(row)
    except:
        print(f"Failed to read condition info for {phase}")

    record = []

    for idx, cond in enumerate(trial_conditions):
        screen.fill((0, 0, 0))
        img_rect = cond.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(cond.image, img_rect)
        pygame.display.flip()

        trial_start = pygame.time.get_ticks()
        responded = False
        correct = False

        while pygame.time.get_ticks() - trial_start < max_respond_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        responded = True
                        correct = cond.mirrored
                    elif event.key == pygame.K_m:
                        responded = True
                        correct = not cond.mirrored

            if responded:
                break

        reaction_time = pygame.time.get_ticks() - trial_start

        if idx < len(condition_info):
            info = condition_info[idx]
            phase_data[phase].append({
                "item_number": info["item_number"],
                "letter_name": info["letter_name"],
                "rotation_angle": info["rotation_angle"],
                "mirrored": info["mirrored"],
                "block": info["block"],
                "reaction_time": reaction_time,
                "correct": int(correct)
            })

        record.append(correct)

        screen.fill((0, 0, 0))
        if phase == "demo":
            if correct:
                feedback_img = feedback_icons.correct_icon
            else:
                feedback_img = feedback_icons.incorrect_icon
            feedback_rect = feedback_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(feedback_img, feedback_rect)

        pygame.display.flip()
        pygame.time.delay(feedback_time)

    return record

def save_all_results():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    save_result_csv("demo")
    save_result_csv("test1")
    save_result_csv("test2")

    print("All results saved!")

def save_result_csv(phase):
    filename = os.path.join(RESULT_DIR, f"{participant_info}_{phase}_result.csv")
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["participant_id","item_number","letter_name","rotation_angle","mirrored","block","reaction_time_ms","correct","start_time","end_time","break_duration_s"])
        for trial in phase_data[phase]:
            writer.writerow([
                participant_info,
                trial["item_number"],
                trial["letter_name"],
                trial["rotation_angle"],
                trial["mirrored"],
                trial["block"],
                trial["reaction_time"],
                trial["correct"],
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_start_time)),
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_end_time)),
                break_duration_s
            ])

# Main loop for participant input
global_start_time = time.time()
while input_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SEMICOLON:
                print(f"Participant info: {participant_info}")
                input_active = False
                instruction_active = True
            elif event.key == pygame.K_BACKSPACE:
                participant_info = participant_info[:-1]
            else:
                participant_info += event.unicode

    screen.fill((255, 255, 255))

    text_surface1 = font_large.render(welcome_text1, True, (0, 0, 0))
    text_surface2 = font_medium.render(welcome_text2, True, (0, 0, 0))
    input_surface = font_medium.render(participant_info, True, (0, 0, 255))

    screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2, 200))
    screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2, 300))
    screen.blit(input_surface, (SCREEN_WIDTH // 2 - input_surface.get_width() // 2, 500))

    pygame.display.flip()

if instruction_active:
    load_instructions(MODE)

global_end_time = time.time()
print("Task completed!")
