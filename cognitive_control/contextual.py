import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from motor import key_logging

# Run Trials
def run_c_trials(trials, response_time, isi_time, condition, screen):
    total_trials = 0
    correct_count = 0
    for trial in trials:
        stimulus_image, key_correct, type, phase, fixation_time = trial

        # Fixation
        screen.blit(CONTEXTUAL_FIXATION, (0, 0))
        fixation_key_response, fixation_reaction_time = key_logging(fixation_time)

        # Stimulus
        screen.blit(stimulus_image, (0, 0))
        stimulus_key_response, stimulus_reaction_time = key_logging(response_time)

        # ISI
        screen.fill(GRAY_RGB)
        isi_key_response, isi_reaction_time = key_logging(isi_time)

        # Feedback
        if type == "no_go":
            correct = (
                fixation_key_response is None
                and stimulus_key_response is None
                and isi_key_response is None
            )
            timeout = False
        else:
            correct = (
                stimulus_key_response is not None
                and stimulus_key_response == key_correct
                and fixation_key_response is None
                and isi_key_response is None
            )
            timeout = (
                fixation_key_response is None
                and stimulus_key_response is None
                and isi_key_response is None
            )
        if phase.startswith("practice"):
            show_feedback(screen, correct, timeout)
        
        # Error check
        error_type = []
        if fixation_key_response is not None:
                error_type.append("premature_error")
        if type == "no_go":
            if stimulus_key_response is not None:
                error_type.append("no_go_error")
            if isi_key_response is not None:
                error_type.append("no_go_delay_error")
        else:
            if stimulus_key_response != key_correct:
                error_type.append("incorrect_response")
            if isi_key_response is not None:
                error_type.append("delay_error")

        # Store results
        results = []
        results.append({
            "block": phase,
            "type": type,
            "fixation_time": fixation_time,
            "condition": condition,
            "difficulty": fixation_time,
            "key_correct": key_correct,
            "fixation_key_response": fixation_key_response,
            "fixation_reaction_time_ms": fixation_reaction_time,
            "stimulus_key_response": stimulus_key_response,
            "stimulus_reaction_time_ms": stimulus_reaction_time,
            "isi_key_response": isi_key_response,
            "isi_reaction_time_ms": isi_reaction_time,
            "correct": correct,
            "error_type": ";".join(error_type) if error_type else None
        })

        # Calculate accuracy
        total_trials += 1
        if correct:
            correct_count += 1

    accuracy = correct_count / total_trials
    return results, accuracy

def practice4_1(screen):
    return run_c_trials(practice4_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "contextual", screen)

def practice4_2(screen):
    return run_c_trials(practice4_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "contextual", screen)

def block4(screen):
    return run_c_trials(block4_trials, M_RESPONSE_TIME, M_ISI_TIME, "contextual", screen)

# Segment 1 practice 4-1 + practice 4-2
def run_c_segment1(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(0, PRACTICE3_2_PAGE):            
        if i == PRACTICE4_1_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], practice4_1))
        elif i == PRACTICE4_2_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], practice4_2))
        else:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], None))

    def after_c_segment1():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < 0.8:
            run_c_segment2(screen, all_results, all_acc, next_segment_func)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_c_segment1)

# Segment 2: repeat practice 4-1 + practice 4-2 (if not pass accuracy requirements)
def run_c_segment2(screen, all_results, all_acc, next_segment_func, repeat_count=1):
    instruction_flow = [(SM_INSTRUCTION_p3, None)]
    for i in range(PRACTICE4_1_PAGE - 1, PRACTICE4_2_PAGE):
        if i == PRACTICE4_1_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], practice4_1))
        elif i == PRACTICE4_2_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], practice4_2))
        else:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], None))

    def after_c_segment2():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < ACCURACY and repeat_count < MAX_REPEAT:
            run_c_segment2(screen, all_results, all_acc, next_segment_func, repeat_count + 1)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_c_segment2)

# Segment 3: block 3
def run_c_segment3(screen, all_results, all_acc, next_segment_func=None):
    instruction_flow = []
    for i in range(PRACTICE4_2_PAGE, len(C_ALL_INSTRUCTIONS)):
        if i == BLOCK4_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], block4))
        else:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], None))

    def after_c_segment3():
        if next_segment_func:
            next_segment_func()
        else:
            pygame.quit()
            quit()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_c_segment3)