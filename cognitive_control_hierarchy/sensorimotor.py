import pygame
import random
import os
import csv
import sys

# ==== Meta Parameters ====
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000

REAL_PRACTICE_RED = 9
REAL_PRACTICE_BLUE = 9
REAL_PRACTICE_CATCH = 2
REAL_ACTUAL_RED = 18
REAL_ACTUAL_BLUE = 18
REAL_ACTUAL_CATCH = 4
REAL_FEEDBACK_TIME = 2000

TEST_PRACTICE_RED = 9
TEST_PRACTICE_BLUE = 9
TEST_PRACTICE_CATCH = 2
TEST_ACTUAL_RED = 9
TEST_ACTUAL_BLUE = 9
TEST_ACTUAL_CATCH = 2
TEST_FEEDBACK_TIME = 500

RED_DURATION = 2000
FIXATION_MIN = 800
FIXATION_MAX = 1200
ISI_DURATION = 500

TOTAL_INSTRUCTION_PAGES = 8
PRACTICE_START_PAGE = 5
ACTUAL_START_PAGE = 7

INSTRUCTION_DIR = "./instructions/sensorimotor/"
RESULT_DIR = "./results/"

COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gray": (200, 200, 200),
    "red": (255, 0, 0),
    "blue": (0, 0, 255)
}

ACCURACY = 80
MAX_PRACTICE_REPEATS = 3

# ==== Initialize Pygame ====
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sensorimotor Task")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

# ==== Input ID ====
def input_participant_id():
    input_str = ""
    while True:
        screen.fill(COLORS["gray"])
        prompt1 = font.render("Enter participant ID:", True, COLORS["black"])
        prompt2 = font.render("Press [SPACE] to continue", True, COLORS["black"])
        input_surface = font.render(input_str, True, COLORS["black"])
        screen.blit(prompt1, (100, 200))
        screen.blit(input_surface, (100, 300))
        screen.blit(prompt2, (100, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif event.key == pygame.K_SPACE and input_str:
                    return input_str
                elif event.unicode.isalnum() or event.unicode in "_-":
                    input_str += event.unicode

# ==== Input Mode ====
def input_mode():
    while True:
        screen.fill(COLORS["gray"])
        prompt = font.render("Select mode: 1 for REAL / 2 for TEST", True, COLORS["black"])
        screen.blit(prompt, (100, 200))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: return "real"
                elif event.key == pygame.K_2: return "test"

# ==== Load Instructions ====
def load_instructions():
    pages = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.png")
        try:
            img = pygame.image.load(img_path)
            pages.append(img)
        except:
            pages.append(None)
    return pages

# ==== Trial Generator ====
def generate_trials(num_red, num_blue, num_catch):
    actual_trials = [("actual", random.randint(FIXATION_MIN, FIXATION_MAX), "red") for _ in range(num_red)]
    actual_trials += [("actual", random.randint(FIXATION_MIN, FIXATION_MAX), "blue") for _ in range(num_blue)]
    catch_trials = [("catch", random.randint(FIXATION_MIN, FIXATION_MAX), None) for _ in range(num_catch)]
    combined = actual_trials + catch_trials
    grouped = [combined[i:i+20] for i in range(0, len(combined), 20)]
    for group in grouped:
        random.shuffle(group)
    return [trial for group in grouped for trial in group]

# ==== Draw Circle and ISI ====
def draw_circle(color):
    screen.fill(COLORS["gray"])
    pygame.draw.circle(screen, COLORS[color], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 100)
    pygame.display.flip()

def draw_isi():
    screen.fill(COLORS["gray"])
    pygame.display.flip()

# ==== Show Text Feedback ====
def show_text_feedback(trial_data, feedback_time):
    messages = []
    if trial_data["fixation_cross_key_response"]:
        messages.append("Too early: wait until the circle turns black.")
    if trial_data["ISI_key_response"] or (
        trial_data["type"] == "actual" and not trial_data["response_key_response"]
    ):
        messages.append("Too late: response before the black circle vanishes.")
    if (
        not trial_data["fixation_cross_key_response"]
        and not trial_data["ISI_key_response"]
        and trial_data["response_key_response"]
    ):
        if trial_data["correct"] is True:
            messages.append("Correct.")
        elif trial_data["correct"] is False:
            messages.append("Wrong response: press [v] for red circle and [m] for blue circle.")

    screen.fill(COLORS["gray"])
    for idx, msg in enumerate(messages):
        rendered = font.render(msg, True, COLORS["black"])
        screen.blit(rendered, (SCREEN_WIDTH // 2 - rendered.get_width() // 2, SCREEN_HEIGHT // 2 + idx * 40))
    pygame.display.flip()
    pygame.time.delay(feedback_time)

    screen.fill(COLORS["gray"])
    pygame.display.flip()
    pygame.time.delay(10)

# ==== Calculate Accuracy ====
def calculate_accuracy(results):
    total = len(results)
    correct = sum(1 for r in results if r["error_type"] is None)
    return correct / total if total > 0 else 0

# ==== Run Trials ====
def run_trials(trials, block, participant_id, show_feedback=False, feedback_time=2000):
    results = []
    any_invalid = False
    for trial_type, delay_time, color in trials:
        key_correct = None
        if trial_type == "actual":
            key_correct = "v" if color == "red" else "m"

        trial_data = {
            "participant_id": participant_id,
            "valid": None,
            "block": block,
            "item_number": item_counter,
            "type": trial_type,
            "delay_time": delay_time,
            "condition": "sensorimotor",
            "difficulty": delay_time,
            "color": color,
            "key_correct": key_correct,
            "fixation_cross_key_response": None,
            "fixation_cross_reaction_time_ms": None,
            "response_key_response": None,
            "response_reaction_time_ms": None,
            "ISI_key_response": None,
            "ISI_reaction_time_ms": None,
            "correct": None,
            "error_type": None,
            "reaction_time_ms": None
        }

        # Fixation
        pygame.event.clear()
        pygame.draw.circle(screen, COLORS["white"], (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 100)
        pygame.display.flip()
        fixation_start = pygame.time.get_ticks()
        responded = False
        while pygame.time.get_ticks() - fixation_start < delay_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if not responded and event.type == pygame.KEYDOWN and event.key in [pygame.K_v, pygame.K_m]:
                    trial_data["fixation_cross_key_response"] = "v"
                    trial_data["fixation_cross_reaction_time_ms"] = pygame.time.get_ticks() - fixation_start
                    responded = True
                    break
            if responded: break

        # Response
        pygame.event.clear()
        if trial_type == "actual":
            pygame.draw.circle(screen, COLORS[color], (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 100)
            pygame.display.flip()
            response_start = pygame.time.get_ticks()
            responded = False
            while pygame.time.get_ticks() - response_start < RED_DURATION:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if not responded and event.type == pygame.KEYDOWN and event.key in [pygame.K_v, pygame.K_m]:
                        key = pygame.key.name(event.key)
                        trial_data["response_key_response"] = key
                        trial_data["response_reaction_time_ms"] = pygame.time.get_ticks() - response_start
                        trial_data["reaction_time_ms"] = pygame.time.get_ticks() - response_start
                        trial_data["correct"] = (key == key_correct)
                        responded = True
                        break
                if responded: break

        # ISI
        pygame.event.clear()
        screen.fill(COLORS["gray"])
        pygame.display.flip()
        isi_start = pygame.time.get_ticks()
        responded = False
        while pygame.time.get_ticks() - isi_start < ISI_DURATION:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if not responded and event.type == pygame.KEYDOWN and event.key in [pygame.K_v, pygame.K_m]:
                    trial_data["ISI_key_response"] = pygame.key.name(event.key)
                    trial_data["ISI_reaction_time_ms"] = pygame.time.get_ticks() - isi_start
                    responded = True
                    break
            if responded: break

        # Error logic
        if trial_type == "catch":
            if trial_data["fixation_cross_key_response"]:
                trial_data["error_type"] = "catch_error"
            elif trial_data["ISI_key_response"]:
                trial_data["error_type"] = "catch_delay_error"
        elif trial_type == "actual":
            if trial_data["fixation_cross_key_response"]:
                trial_data["error_type"] = "premature_error"
            elif trial_data["ISI_key_response"]:
                trial_data["error_type"] = "delay_error"
            elif not trial_data["response_key_response"]:
                trial_data["error_type"] = "miss_error"

        if trial_data["error_type"] in ["miss_error", "delay_error", "catch_error", "catch_delay_error"]:
            any_invalid = True

        if show_feedback:
            show_text_feedback(trial_data, feedback_time)

        results.append(trial_data)

    for row in results:
        row["valid"] = not any_invalid
    return results

# ==== Save Results ====
def save_results_csv(participant_id, block_name, results):
    os.makedirs(RESULT_DIR, exist_ok=True)
    filename = f"{participant_id}_motor_{block_name}_result.csv"
    path = os.path.join(RESULT_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

# ==== Load Instruction Pages ====
def load_instructions():
    pages = []
    for i in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        img_path = os.path.join(INSTRUCTION_DIR, f"{i}.png")
        try:
            img = pygame.image.load(img_path)
            pages.append(img)
        except:
            pages.append(None)
    return pages

# ==== Main ====
participant_id = input_participant_id()
mode = input_mode()
instructions = load_instructions()
page_idx = 0
instruction_locked = True
unlock_timer = pygame.time.get_ticks()
read_time = 10000 if mode == "real" else 100

running = True
while running:
    screen.fill(COLORS["gray"])
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not instruction_locked:
            page_idx += 1
            instruction_locked = True
            unlock_timer = pygame.time.get_ticks()

            if page_idx == PRACTICE_START_PAGE:
                max_repeat = 0
                passed = False
                all_practice_results = []
                item_counter = 1

                while max_repeat < MAX_PRACTICE_REPEATS and not passed:
                    if mode == "real":
                        trials = generate_trials(REAL_PRACTICE_RED, REAL_PRACTICE_BLUE, REAL_PRACTICE_CATCH)
                        results = run_trials(trials, "practice", participant_id, show_feedback=True, feedback_time=REAL_FEEDBACK_TIME)
                    else:
                        trials = generate_trials(TEST_PRACTICE_RED, TEST_PRACTICE_BLUE, TEST_PRACTICE_CATCH)
                        results = run_trials(trials, "practice", participant_id, show_feedback=True, feedback_time=TEST_FEEDBACK_TIME)

                    for r in results:
                        r["block"] = f"practice{max_repeat + 1}"
                        r["item_number"] = item_counter
                        item_counter += 1
                    all_practice_results.extend(results)

                    acc = calculate_accuracy(all_practice_results)
                    no_catch_error = all(r["error_type"] not in ["catch_error", "catch_delay_error"] for r in results)

                    if acc >= ACCURACY / 100 and no_catch_error:
                        passed = True
                    else:
                        max_repeat += 1
                        if max_repeat < MAX_PRACTICE_REPEATS:
                            for img_name in ["4_2.png", "5_2.png"]:
                                img_path = os.path.join(INSTRUCTION_DIR, img_name)
                                try:
                                    img = pygame.image.load(img_path)
                                except:
                                    continue
                                unlock_timer = pygame.time.get_ticks()
                                instruction_locked = True
                                waiting = True
                                while waiting:
                                    screen.fill(COLORS["gray"])
                                    current_time = pygame.time.get_ticks()
                                    if current_time - unlock_timer >= read_time:
                                        instruction_locked = False
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit(); sys.exit()
                                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not instruction_locked:
                                            waiting = False
                                    screen.blit(pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
                                    pygame.display.flip()

                save_results_csv(participant_id, "practice", all_practice_results)

            elif page_idx == ACTUAL_START_PAGE:
                if mode == "real":
                    trials = generate_trials(REAL_ACTUAL_RED, REAL_ACTUAL_BLUE, REAL_ACTUAL_CATCH)
                    results = run_trials(trials, "actual", participant_id, show_feedback=False)
                else:
                    trials = generate_trials(TEST_ACTUAL_RED, TEST_ACTUAL_BLUE, TEST_ACTUAL_CATCH)
                    results = run_trials(trials, "actual", participant_id, show_feedback=False)
                save_results_csv(participant_id, "actual", results)

    if current_time - unlock_timer >= read_time:
        instruction_locked = False

    if page_idx < len(instructions) and instructions[page_idx]:
        img = pygame.transform.scale(instructions[page_idx], (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(img, (0, 0))
    pygame.display.flip()

pygame.quit()
