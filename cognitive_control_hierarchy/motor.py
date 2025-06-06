import pygame
import random
import os
import csv

# ==== Meta Parameters ====
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
RED_DURATION = 1500
FIXATION_DURATION = 500

# ==== Color Definitions ====
COLORS = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "black": (0, 0, 0)
}

# ==== Input Trial Number ====
def input_trial_number(screen, font):
    input_str = ""
    active = True
    while active:
        screen.fill(COLORS["black"])
        prompt1 = font.render("Enter number of trials (recommended: divisible by 10):", True, COLORS["white"])
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
    for _ in range(trial_num):
        trials.append(["actual", random.randint(800, 1200)])
    for _ in range(catch_num):
        trials.append(["catch", random.randint(800, 1200)])
    random.shuffle(trials)
    return trials

# ==== Draw Circle ====
def draw_circle(screen, color, font):
    screen.fill(COLORS["black"])
    pygame.draw.circle(screen, COLORS[color], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 100)

    # Show instruction text below the circle
    space_text = font.render("SPACE (respond)", True, COLORS["white"])
    screen.blit(space_text, (SCREEN_WIDTH // 2 - space_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))

    pygame.display.flip()

# ==== Draw Fixation (black screen placeholder) ====
def draw_fixation(screen):
    screen.fill(COLORS["black"])
    pygame.display.flip()

# ==== Save to CSV ====
def save_results_csv(participant_id, results):
    os.makedirs("results", exist_ok=True)
    filename = f"{participant_id}_motor_result.csv"
    path = os.path.join("results", filename)

    with open(path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id", "valid", "item_number", "type", "delay_time", "condition",
            "difficulty", "reaction_time_ms", "error_type"
        ])
        writer.writeheader()
        writer.writerows(results)

# ==== Main ====
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Motor Task")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

TRIAL_NUM = input_trial_number(screen, font)
participant_id = input_participant_id(screen, font)
trials = generate_trials(TRIAL_NUM)

results = []
any_invalid = False

for trial_index, (trial_type, time_white) in enumerate(trials):
    pygame.event.clear()
    responded = False
    reaction_time_ms = None
    error_type = None

    # === White circle ===
    draw_circle(screen, "white", font)
    white_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - white_start < time_white:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if not responded and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                responded = True
                if trial_type == "catch":
                    error_type = "catch_error"
                elif trial_type == "actual":
                    error_type = "premature_error"
        if responded and error_type == "premature_error":
            break  # Exit white early if premature error

    # === Red circle if actual and not premature_error ===
    if trial_type == "actual" and error_type is None:
        draw_circle(screen, "red", font)
        red_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - red_start < RED_DURATION:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if not responded and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    reaction_time_ms = pygame.time.get_ticks() - red_start
                    responded = True
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
            if not responded and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                responded = True
                if trial_type == "catch":
                    error_type = "catch_delay_error"
                elif trial_type == "actual" and error_type is None:
                    error_type = "delay_error"

    if error_type in ["catch_error", "catch_delay_error"]:
        any_invalid = True
    if trial_type == "actual" and error_type is None and reaction_time_ms is None:
        error_type = "miss_error"

    results.append({
        "participant_id": participant_id,
        "valid": None,  # to be filled after all trials
        "item_number": trial_index + 1,
        "type": trial_type,
        "delay_time": time_white,
        "condition": "motor",
        "difficulty": time_white,
        "reaction_time_ms": reaction_time_ms if error_type is None else None,
        "error_type": error_type
    })

# Set global valid flag for all rows
for row in results:
    row["valid"] = not any_invalid

save_results_csv(participant_id, results)
pygame.quit()
