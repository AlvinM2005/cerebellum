import pygame
import sys
import os
import csv
import time
import random  # Importar el módulo random para mezclar las condiciones
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
TOTAL_INSTRUCTION_PAGES = 15
DEMO_PAGE = 7
TEST1_PAGE = 11
TEST2_PAGE = 14

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
        condition_path = f"{CONDITION_DIR}{phase}_conditions.csv"
    else:
        max_respond_time = TEST_MAX_RESPOND_TIME
        feedback_time = TEST_FEEDBACK_TIME
        condition_path = f"{CONDITION_DIR}{phase}_conditions_short.csv"

    feedback_icons = FeedbackIcon()

    # Leer las condiciones desde el archivo CSV
    trial_conditions = []
    try:
        with open(condition_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trial_conditions.append({
                    "stimuli_path": row["stimuli_path"],
                    "key_correct": row["key_correct"],  # Actualizado para reflejar el cambio de nombre
                    "file_name": row["file_name"],  # Nueva columna
                    "letter_name": row["letter_name"],
                    "rotation_angle": row["rotation_angle"],
                    "mirrored": row["mirrored"]
                })
    except Exception as e:
        print(f"Failed to read condition info for {phase}: {e}")
        return

    # Mezclar las condiciones de forma aleatoria
    random.shuffle(trial_conditions)

    record = []

    for idx, cond in enumerate(trial_conditions):
        # Cargar la imagen desde la ruta especificada
        try:
            img = pygame.image.load(cond["stimuli_path"])
            img = pygame.transform.scale(img, (400, 400))
        except Exception as e:
            print(f"Error loading image {cond['stimuli_path']}: {e}")
            continue

        screen.fill((0, 0, 0))
        img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(img, img_rect)
        pygame.display.flip()

        trial_start = pygame.time.get_ticks()
        responded = False
        correct = False
        key_response = None  # Inicializar la tecla presionada

        while pygame.time.get_ticks() - trial_start < max_respond_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        responded = True
                        key_response = "v"
                        correct = cond["key_correct"] == "v"
                    elif event.key == pygame.K_m:
                        responded = True
                        key_response = "m"
                        correct = cond["key_correct"] == "m"

            if responded:
                break

        reaction_time = pygame.time.get_ticks() - trial_start

        # Registrar los resultados
        phase_data[phase].append({
            "item_number": idx + 1,  # Número del ítem
            "letter_name": cond["letter_name"],  # Extraer la letra del CSV
            "rotation_angle": cond["rotation_angle"],  # Extraer el ángulo del CSV
            "mirrored": cond["mirrored"],  # Extraer si está espejado del CSV
            "stimuli_path": cond["stimuli_path"],  # Ruta de la imagen
            "file_name": cond["file_name"],  # Nombre del archivo
            "correct_response": cond["key_correct"],  # Guardar como correct_response
            "key_response": key_response,  # Tecla presionada
            "block": phase,
            "reaction_time": reaction_time,
            "correct": int(correct)
        })

        record.append(correct)

        # Mostrar retroalimentación
        screen.fill((0, 0, 0))
        if phase == "demo":
            feedback_img = feedback_icons.correct_icon if correct else feedback_icons.incorrect_icon
            feedback_rect = feedback_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
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
    if phase_data[phase]:  # Verificar que haya datos para guardar
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "participant_id", "item_number", "letter_name", "rotation_angle", "mirrored",
                "stimuli_path", "file_name", "correct_response", "key_response", "block",
                "reaction_time_ms", "correct", "start_time", "end_time", "break_duration_s"
            ])
            for trial in phase_data[phase]:
                writer.writerow([
                    participant_info,
                    trial["item_number"],
                    trial["letter_name"],
                    trial["rotation_angle"],
                    trial["mirrored"],
                    trial["stimuli_path"],
                    trial["file_name"],
                    trial["correct_response"],
                    trial["key_response"],
                    trial["block"],
                    trial["reaction_time"],
                    trial["correct"],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_start_time)),
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_end_time)),
                    break_duration_s
                ])
    else:
        print(f"No data to save for phase: {phase}")

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
