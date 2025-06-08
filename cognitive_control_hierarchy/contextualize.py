import os
import pygame
import random
import csv

# ==== Meta Parameters ====
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
RESPONSE_DURATION = 2000
FIXATION_DURATION = 500

# ==== Color Definitions ====
COLORS = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0)
}

# ==== Input Functions ====
def input_number(screen, font, prompt_text):
    input_str = ""
    while True:
        screen.fill(COLORS["black"])
        prompt1 = font.render(prompt_text, True, COLORS["white"])
        prompt2 = font.render("[Press SPACE to continue]", True, COLORS["white"])
        input_surface = font.render(input_str, True, COLORS["white"])
        screen.blit(prompt1, (100, 200))
        screen.blit(input_surface, (100, 300))
        screen.blit(prompt2, (100, 400))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif event.key == pygame.K_SPACE and input_str:
                    return input_str if not input_str.isdigit() else int(input_str)
                elif event.unicode.isalnum() or event.unicode in "_-":
                    input_str += event.unicode

# ==== Trial Generator ====
def generate_trials(trial_num):
    actual_trials = []
    letters = ["A", "a", "B", "b"]
    color_counts = trial_num // 2
    each_count = color_counts // 4
    for color in ["red", "blue"]:
        for letter in letters:
            for _ in range(each_count):
                actual_trials.append(["actual", random.randint(800, 1200), color, letter])
    catch_trials = [["catch", random.randint(800, 1200), None, None] for _ in range(trial_num // 10)]
    all_trials = actual_trials + catch_trials
    random.shuffle(all_trials)
    return all_trials

# ==== Drawing Functions ====
def draw_text_center(screen, text, font, color, y_offset=0):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
    screen.blit(text_surface, rect)

def draw_stimulus(screen, color, letter=None, show_cross=False, font=None):
    screen.fill(COLORS["black"])
    if show_cross:
        draw_text_center(screen, "+", font, COLORS["white"], y_offset=0)
    elif letter:
        draw_text_center(screen, letter, font, COLORS[color], y_offset=0)
    draw_text_center(screen, "V (capital / vowel)", font, COLORS["white"], y_offset=100)
    draw_text_center(screen, "M (lowercase / consonant)", font, COLORS["white"], y_offset=160)
    pygame.display.flip()

def draw_fixation(screen):
    screen.fill(COLORS["black"])
    pygame.display.flip()

# ==== Save Function ====
def save_results_csv(participant_id, results):
    os.makedirs("results", exist_ok=True)
    filename = f"{participant_id}_contextual_result.csv"
    path = os.path.join("results", filename)
    with open(path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id", "valid", "item_number", "type", "delay_time", "color",
            "test_type", "capital", "vowel",
            "condition", "difficulty", "letter", "reaction_time_ms",
            "key_correct", "key_response", "correct", "error_type"
        ])
        writer.writeheader()
        writer.writerows(results)

# ==== Main ====
def run_contextual_task():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Contextual Task")
    font = pygame.font.SysFont(None, 64)
    prompt_font = pygame.font.SysFont(None, 48)

    TRIAL_NUM = input_number(screen, prompt_font, "Enter number of actual trials (recommended: divisible by 40):")
    participant_id = input_number(screen, prompt_font, "Enter participant ID:")
    trials = generate_trials(TRIAL_NUM)
    results = []
    any_invalid = False

    for trial_index, (trial_type, delay_time, color, letter) in enumerate(trials):
        pygame.event.clear()
        responded = False
        key_response = None
        key_correct = None
        reaction_time_ms = None
        error_type = None
        correct = None

        test_type = None
        capital_type = None
        vowel_type = None

        if trial_type == "actual":
            if color == "red":
                test_type = "capital"
                key_correct = "v" if letter.isupper() else "m"
                capital_type = "capital" if letter.isupper() else "lowercase"
                vowel_type = None
            elif color == "blue":
                test_type = "vowel"
                key_correct = "v" if letter.lower() == "a" else "m"
                capital_type = None
                vowel_type = "vowel" if letter.lower() == "a" else "consonant"

        # === white cross ===
        draw_stimulus(screen, color, letter=None, show_cross=True, font=font)
        white_start = pygame.time.get_ticks()
        premature = False
        while pygame.time.get_ticks() - white_start < delay_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if not responded and event.type == pygame.KEYDOWN and event.key in [pygame.K_v, pygame.K_m]:
                    key_response = "v" if event.key == pygame.K_v else "m"
                    responded = True
                    premature = True
                    error_type = "premature_error" if trial_type == "actual" else "catch_error"
                    break
            if premature:
                break

        # === red/blue letter + response phase ===
        if not premature:
            if trial_type == "actual":
                draw_stimulus(screen, color, letter=letter, show_cross=False, font=font)
            elif trial_type == "catch":
                draw_stimulus(screen, "white", letter=None, show_cross=True, font=font)

            response_start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - response_start < RESPONSE_DURATION:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); exit()
                    if not responded and event.type == pygame.KEYDOWN and event.key in [pygame.K_v, pygame.K_m]:
                        key_response = "v" if event.key == pygame.K_v else "m"
                        reaction_time_ms = pygame.time.get_ticks() - response_start
                        responded = True
                        if trial_type == "catch":
                            error_type = "catch_error"
                        elif trial_type == "actual":
                            correct = int(key_response == key_correct)
                        break
                if responded:
                    break

        # === Fixation and late press detection ===
        draw_fixation(screen)
        fixation_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - fixation_start < FIXATION_DURATION:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if not responded and event.type == pygame.KEYDOWN and event.key in [pygame.K_v, pygame.K_m]:
                    responded = True
                    key_response = "v" if event.key == pygame.K_v else "m"
                    reaction_time_ms = None
                    if trial_type == "catch":
                        error_type = "catch_delay_error"
                    elif trial_type == "actual":
                        error_type = "delay_error"

        if trial_type == "actual":
            if not responded:
                error_type = "miss_error"
            elif error_type is None:
                correct = int(key_response == key_correct)

        if error_type in ["catch_error", "catch_delay_error"]:
            any_invalid = True
        if error_type is not None:
            reaction_time_ms = None
            correct = 0

        results.append({
            "participant_id": participant_id,
            "valid": None,
            "item_number": trial_index + 1,
            "type": trial_type,
            "delay_time": delay_time,
            "color": color,
            "test_type": test_type,
            "capital": capital_type,
            "vowel": vowel_type,
            "condition": "contextual",
            "difficulty": delay_time,
            "letter": letter,
            "reaction_time_ms": reaction_time_ms,
            "key_correct": key_correct,
            "key_response": key_response,
            "correct": correct,
            "error_type": error_type
        })

    for r in results:
        r["valid"] = not any_invalid

    save_results_csv(participant_id, results)
    pygame.quit()

run_contextual_task()
