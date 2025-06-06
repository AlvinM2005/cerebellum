import pygame
import random
import os
import csv

# ==== Meta Parameters ====
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
CIRCLE_DURATION = 2000
FIXATION_DURATION = 500

# ==== Color Definitions ====
COLORS = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0)
}

# ==== Input Trial Number ====
def input_trial_number(screen, font):
    input_str = ""
    active = True
    while active:
        screen.fill(COLORS["black"])
        prompt1 = font.render("Enter number of trials (recommended: divisible by 20):", True, COLORS["white"])
        prompt2 = font.render("[Press SPACE to continue]", True, COLORS["white"])
        input_surface = font.render(input_str, True, COLORS["white"])
        screen.blit(prompt1, (100, 200))
        screen.blit(input_surface, (100, 300))
        screen.blit(prompt2, (100, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif event.key == pygame.K_SPACE:
                    if input_str.isdigit() and int(input_str) > 0:
                        return int(input_str)
                elif event.unicode.isdigit():
                    input_str += event.unicode

# ==== Input Participant ID ====
def input_participant_id(screen, font):
    input_str = ""
    active = True
    while active:
        screen.fill(COLORS["black"])
        prompt1 = font.render("Enter participant ID:", True, COLORS["white"])
        prompt2 = font.render("[Press SPACE to continue]", True, COLORS["white"])
        input_surface = font.render(input_str, True, COLORS["white"])
        screen.blit(prompt1, (100, 200))
        screen.blit(input_surface, (100, 300))
        screen.blit(prompt2, (100, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif event.key == pygame.K_SPACE and input_str:
                    return input_str
                elif event.unicode.isalnum() or event.unicode in "_-":
                    input_str += event.unicode

# ==== Trial Generator ====
def generate_trials(trial_num):
    trials = []
    catch_num = trial_num // 10
    red_num = trial_num // 2
    blue_num = trial_num - red_num

    for _ in range(red_num):
        trials.append(["actual", random.randint(800, 1200), "red"])
    for _ in range(blue_num):
        trials.append(["actual", random.randint(800, 1200), "blue"])
    for _ in range(catch_num):
        trials.append(["catch", random.randint(800, 1200), None])
    random.shuffle(trials)
    return trials

# ==== Draw Circle ====
def draw_circle(screen, color, font):
    screen.fill(COLORS["black"])
    pygame.draw.circle(screen, COLORS[color], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 100)

    # Show instruction text below the circle
    v_text = font.render("V (red)", True, COLORS["white"])
    m_text = font.render("M (blue)", True, COLORS["white"])
    screen.blit(v_text, (SCREEN_WIDTH // 2 - v_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))
    screen.blit(m_text, (SCREEN_WIDTH // 2 - m_text.get_width() // 2, SCREEN_HEIGHT // 2 + 210))

    pygame.display.flip()

# ==== Draw Fixation ====
def draw_fixation(screen):
    screen.fill(COLORS["black"])
    pygame.display.flip()

# ==== Save Results ====
def save_results_csv(participant_id, results):
    os.makedirs("results", exist_ok=True)
    filename = f"{participant_id}_sensorimotor_result.csv"
    path = os.path.join("results", filename)
    with open(path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id", "valid", "item_number", "type", "delay_time", "color",
            "condition", "difficulty", "reaction_time_ms", "key_correct", "key_response",
            "correct", "error_type"
        ])
        writer.writeheader()
        writer.writerows(results)

# ==== Main ====
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sensorimotor Task")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

TRIAL_NUM = input_trial_number(screen, font)
participant_id = input_participant_id(screen, font)
trials = generate_trials(TRIAL_NUM)
results = []
any_invalid = False

for trial_index, (trial_type, time_white, color) in enumerate(trials):
    pygame.event.clear()
    responded = False
    reaction_time_ms = None
    error_type = None
    key_response = None
    key_correct = None
    correct = None

    if color == "red":
        key_correct = "v"
    elif color == "blue":
        key_correct = "m"

    # === White circle ===
    draw_circle(screen, "white", font)
    white_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - white_start < time_white:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if not responded and event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_v, pygame.K_m]:
                    responded = True
                    key_response = "v" if event.key == pygame.K_v else "m"
                    if trial_type == "catch":
                        error_type = "catch_error"
                    elif trial_type == "actual":
                        error_type = "premature_error"
        if responded and error_type == "premature_error":
            break

    # === Red or Blue circle if actual and no premature error ===
    if trial_type == "actual" and error_type is None:
        draw_circle(screen, color, font)
        red_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - red_start < CIRCLE_DURATION:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if not responded and event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_v, pygame.K_m]:
                        reaction_time_ms = pygame.time.get_ticks() - red_start
                        responded = True
                        key_response = "v" if event.key == pygame.K_v else "m"
                        correct = int(key_response == key_correct)
                        error_type = None
                        break
            if responded:
                break
        if not responded:
            error_type = "miss_error"

    # === Fixation ===
    draw_fixation(screen)
    fixation_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - fixation_start < FIXATION_DURATION:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if not responded and event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_v, pygame.K_m]:
                    responded = True
                    key_response = "v" if event.key == pygame.K_v else "m"
                    if trial_type == "catch":
                        error_type = "catch_delay_error"
                    elif trial_type == "actual" and error_type is None:
                        error_type = "delay_error"

    if error_type in ["catch_error", "catch_delay_error"]:
        any_invalid = True

    if trial_type == "actual" and error_type is None and reaction_time_ms is None:
        error_type = "miss_error"

    if error_type is not None:
        reaction_time_ms = None
        correct = 0

    results.append({
        "participant_id": participant_id,
        "valid": None,
        "item_number": trial_index + 1,
        "type": trial_type,
        "delay_time": time_white,
        "color": color,
        "condition": "sensorimotor",
        "difficulty": time_white,
        "reaction_time_ms": reaction_time_ms,
        "key_correct": key_correct,
        "key_response": key_response,
        "correct": correct,
        "error_type": error_type
    })

# Fill valid column
for row in results:
    row["valid"] = not any_invalid

save_results_csv(participant_id, results)
pygame.quit()
