import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *

# Key logging (listen to key press)
def key_logging(duration_ms):
    pygame.display.flip()
    pygame.event.clear()
    start_time = pygame.time.get_ticks()
    key_response = None
    reaction_time = None

    while pygame.time.get_ticks() - start_time < duration_ms:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and key_response is None:
                key_response = event.key
                reaction_time = pygame.time.get_ticks() - start_time

    pygame.event.clear()
    return key_response, reaction_time

# Read information from trials
def read_motor_trial(trial):
    fixation_time, stimulus_image, phase = trial
    if stimulus_image == BLUE:
        key_correct = pygame.K_v
        type = "actual"
    elif stimulus_image == RED:
        key_correct = pygame.K_m
        type = "actual"
    elif stimulus_image == NOGO:
        key_correct = None
        type = "no_go"
    return fixation_time, stimulus_image, type, phase, key_correct

# Run trials
def run_trials(trials, response_time, isi_time, condition, read_trial, screen):
    total_trials = 0
    correct_count = 0
    results = []

    for trial in trials:
        fixation_time, stimulus_image, type, phase, key_correct = read_trial(trial)

        # Fixation
        if (condition == "motor"
            or condition == "sensorimotor"):
            screen.blit(FIXATION, (0, 0))
        else:
            screen.blit(CONTEXTUAL_FIXATION, (0, 0))
        fixation_key_response, fixation_reaction_time = key_logging(fixation_time)

        # Stimulus
        screen.blit(stimulus_image, (0, 0))
        stimulus_key_response, stimulus_reaction_time = key_logging(response_time)

        if phase.startswith("practice"):
            if type == "no_go":
                correct = (fixation_key_response is None and stimulus_key_response is None)
                timeout = False
            else:
                correct = (stimulus_key_response == key_correct)
                timeout = (fixation_key_response is None and stimulus_key_response is None)
            show_feedback(screen, correct, timeout, stimulus_image)

        # ISI
        screen.fill(GRAY_RGB)
        isi_key_response, isi_reaction_time = key_logging(isi_time)

        # Error check
        if fixation_key_response is not None:
            error_type = "premature_error"
        else:
            if type == "no_go":
                if stimulus_key_response is not None:
                    error_type = "no_go_error"
                elif isi_key_response is not None:
                    error_type = "no_go_delay_error"
                else:
                    error_type = None
            elif type == "actual":
                if stimulus_key_response == key_correct:
                    error_type = None
                elif stimulus_key_response is not None:
                    error_type = "incorrect_response"
                elif isi_key_response is not None:
                    error_type = "delay_error"
                else:
                    error_type = "no_response"

        avg_fixation_time = (
            M_AVG_FIXATION_TIME if condition == "motor"
            else C_AVG_FIXATION_TIME if condition == "contextual"
            else SM_AVG_FIXATION_TIME  # fallback
        )
        correct = (error_type is None)

        results.append({
            "block": phase,
            "type": type,
            "fixation_time": fixation_time,
            "condition": condition,
            "difficulty": abs(fixation_time - avg_fixation_time),
            "key_correct": key_correct,
            "fixation_key_response": fixation_key_response,
            "fixation_reaction_time_ms": fixation_reaction_time,
            "stimulus_key_response": stimulus_key_response,
            "stimulus_reaction_time_ms": stimulus_reaction_time,
            "isi_key_response": isi_key_response,
            "isi_reaction_time_ms": isi_reaction_time,
            "correct": correct,
            "error_type": error_type
        })

        total_trials += 1
        if correct:
            correct_count += 1

    accuracy = correct_count / total_trials
    return results, accuracy

def practice1_1(screen):
    return run_trials(practice1_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def practice1_2(screen):
    return run_trials(practice1_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def block1(screen):
    return run_trials(block1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def practice2_1(screen):
    return run_trials(practice2_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def practice2_2(screen):
    return run_trials(practice2_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def block2(screen):
    return run_trials(block2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

# Segment 1: practice 1-1 + practice 1-2
def run_m_segment1(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(0, PRACTICE1_2_PAGE):            
        if i == PRACTICE1_1_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice1_1))
        elif i == PRACTICE1_2_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice1_2))
        else:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], None))

    def after_m_segment1():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < 0.8:
            run_m_segment2(screen, all_results, all_acc, next_segment_func)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_m_segment1)

# Segment 2: repeat practice 1-1 + practice 1-2 (if not pass accuracy requirements)
def run_m_segment2(screen, all_results, all_acc, next_segment_func, repeat_count=1):
    instruction_flow = [(M_INSTRUCTION_p1, None)]
    for i in range(PRACTICE1_1_PAGE - 1, PRACTICE1_2_PAGE):
        if i == PRACTICE1_1_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice1_1))
        elif i == PRACTICE1_2_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice1_2))
        else:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], None))

    def after_m_segment2():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
            run_m_segment2(screen, all_results, all_acc, next_segment_func, repeat_count + 1)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_m_segment2)

# Segment 3: block 3 + practice 2-1 + practice 2-2
def run_m_segment3(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(PRACTICE1_2_PAGE, PRACTICE2_2_PAGE):
        if i == BLOCK1_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], block1))
        elif i == PRACTICE2_1_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice2_1))
        elif i == PRACTICE2_2_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice2_2))
        else:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], None))

    def after_m_segment3():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < ACCURACY:
            run_m_segment4(screen, all_results, all_acc, next_segment_func)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_m_segment3)

# Segment 4: repeat practice 2-1 + practice 2-2 (if not pass accuracy requirements)
def run_m_segment4(screen, all_results, all_acc, next_segment_func, repeat_count=1):
    instruction_flow = [(M_INSTRUCTION_p2, None)]
    for i in range(PRACTICE2_1_PAGE - 1, PRACTICE2_2_PAGE):
        if i == PRACTICE2_1_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice2_1))
        elif i == PRACTICE2_2_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], practice2_2))
        else:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], None))

    def after_m_segment4():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
            run_m_segment4(screen, all_results, all_acc, next_segment_func, repeat_count + 1)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_m_segment4)

# Segment 5: block 2
def run_m_segment5(screen, all_results, all_acc, next_segment_func=None):
    instruction_flow = []
    for i in range(PRACTICE2_2_PAGE, len(M_ALL_INSTRUCTIONS)):
        if i == BLOCK2_PAGE - 1:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], block2))
        else:
            instruction_flow.append((M_ALL_INSTRUCTIONS[i], None))

    def after_m_segment5():
        if next_segment_func:
            next_segment_func()
        else:
            pygame.quit()
            quit()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_m_segment5)
