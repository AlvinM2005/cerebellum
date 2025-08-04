import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from motor import key_logging, run_trials

# Read information from trials
def read_contextual_trial(trial):
    print("CONTEXTUAL trial=", trial)
    if len(trial) == 5:
        stimulus_image, key_correct, type, phase, fixation_time = trial
        return fixation_time, stimulus_image, type, phase, key_correct
    if len(trial) == 7:
        stimulus_image, key_correct, type, phase, fixation_time, _, _ = trial
        return fixation_time, stimulus_image, type, phase, key_correct
    stimulus_image, key_correct, type, phase, fixation_time = trial
    return fixation_time, stimulus_image, type, phase, key_correct

def practice4_1(screen):
    return run_trials(practice4_1_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", read_contextual_trial, screen)

def practice4_2(screen):
    return run_trials(practice4_2_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", read_contextual_trial, screen)

def block5(screen):
    return run_trials(block5_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", read_contextual_trial, screen)

def block6(screen):
    return run_trials(block6_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", read_contextual_trial, screen)

# Segment 1 practice 4-1 + practice 4-2
def run_c_segment1(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(0, PRACTICE4_2_PAGE):            
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
        if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
            run_c_segment2(screen, all_results, all_acc, next_segment_func, repeat_count + 1)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_c_segment2)

# Segment 3: block 5 + block 6
def run_c_segment3(screen, all_results, all_acc, next_segment_func=None):
    instruction_flow = []
    for i in range(PRACTICE4_2_PAGE, len(C_ALL_INSTRUCTIONS)):
        if i == BLOCK5_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], block5))
        elif i == BLOCK6_PAGE - 1:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], block6))
        else:
            instruction_flow.append((C_ALL_INSTRUCTIONS[i], None))

    def after_c_segment3():
        if next_segment_func:
            next_segment_func()
        else:
            pygame.quit()
            quit()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_c_segment3)