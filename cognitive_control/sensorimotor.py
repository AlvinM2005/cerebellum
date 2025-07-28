import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from motor import key_logging, read_motor_trial, run_trials

def practice3_1(screen):
    return run_trials(practice3_1_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", read_motor_trial, screen)

def practice3_2(screen):
    return run_trials(practice3_2_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", read_motor_trial, screen)

def block3(screen):
    return run_trials(block3_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", read_motor_trial, screen)

def block4(screen):
    return run_trials(block4_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", read_motor_trial, screen)

# Segment 1 practice 3-1 + practice 3-2
def run_sm_segment1(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(0, PRACTICE3_2_PAGE):            
        if i == PRACTICE3_1_PAGE - 1:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], practice3_1))
        elif i == PRACTICE3_2_PAGE - 1:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], practice3_2))
        else:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], None))

    def after_sm_segment1():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < 0.8:
            run_sm_segment2(screen, all_results, all_acc, next_segment_func)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_sm_segment1)

# Segment 2: repeat practice 3-1 + practice 3-2 (if not pass accuracy requirements)
def run_sm_segment2(screen, all_results, all_acc, next_segment_func, repeat_count=1):
    instruction_flow = [(SM_INSTRUCTION_p3, None)]
    for i in range(PRACTICE3_1_PAGE - 1, PRACTICE3_2_PAGE):
        if i == PRACTICE3_1_PAGE - 1:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], practice3_1))
        elif i == PRACTICE3_2_PAGE - 1:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], practice3_2))
        else:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], None))

    def after_sm_segment2():
        acc_mean = sum(all_acc[-2:]) / 2
        if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
            run_sm_segment2(screen, all_results, all_acc, next_segment_func, repeat_count + 1)
        else:
            next_segment_func()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_sm_segment2)

# Segment 3: block 3 + block 4
def run_sm_segment3(screen, all_results, all_acc, next_segment_func=None):
    instruction_flow = []
    for i in range(PRACTICE3_2_PAGE, len(SM_ALL_INSTRUCTIONS)):
        if i == BLOCK3_PAGE - 1:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], block3))
        elif i == BLOCK4_PAGE - 1:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], block4))
        else:
            instruction_flow.append((SM_ALL_INSTRUCTIONS[i], None))

    def after_sm_segment3():
        if next_segment_func:
            next_segment_func()
        else:
            pygame.quit()
            quit()

    run_instruction_sequence(screen, instruction_flow, all_results, all_acc, after_sm_segment3)