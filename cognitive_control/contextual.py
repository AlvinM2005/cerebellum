import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from motor import key_logging, run_trials

class Contextual:
    def __init__(self, screen, all_results, all_acc, version):
        self.screen = screen
        self.all_results = all_results
        self.all_acc = all_acc

        # ⭐️ 初始化并生成路径/图片
        self.instructions = Instructions(version)
        self.instructions.generate_paths(version)

        # 为了少写长名字，做个简短引用
        self.C_ALL_INSTRUCTIONS = self.instructions.C_ALL_INSTRUCTIONS
        self.C_INSTRUCTION_p4 = self.instructions.C_INSTRUCTION_p4

        self.version = version

    # Read information from trials
    def read_contextual_trial(self, trial):
        print("CONTEXTUAL trial=", trial)
        if len(trial) == 5:
            stimulus_image, key_correct, type, phase, fixation_time = trial
            return fixation_time, stimulus_image, type, phase, key_correct
        if len(trial) == 7:
            stimulus_image, key_correct, type, phase, fixation_time, _, _ = trial
            return fixation_time, stimulus_image, type, phase, key_correct
        stimulus_image, key_correct, type, phase, fixation_time = trial
        return fixation_time, stimulus_image, type, phase, key_correct

    def practice4_1(self, screen):
        practice4_1_trials = create_contextual_trials(PRACTICE4_1_NUM_ACTUAL, PRACTICE4_1_NUM_NOGO, "practice4_1", self.version)
        for trial in practice4_1_trials:
            print(trial)
        return run_trials(practice4_1_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", self.read_contextual_trial, self.screen)

    def practice4_2(self, screen):
        practice4_2_trials = create_contextual_trials(PRACTICE4_2_NUM_ACTUAL, PRACTICE4_2_NUM_NOGO, "practice4_2", self.version)
        return run_trials(practice4_2_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", self.read_contextual_trial, self.screen)

    def block5(self, screen):
        block5_trials = create_contextual_trials(BLOCK5_NUM_ACTUAL, BLOCK5_NUM_NOGO, "block5", self.version)
        return run_trials(block5_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", self.read_contextual_trial, self.screen)

    def block6(self, screen):
        block6_trials = create_contextual_trials(BLOCK6_NUM_ACTUAL, BLOCK6_NUM_NOGO, "block5", self.version)
        return run_trials(block6_trials, C_RESPONSE_TIME, C_ISI_TIME, "contextual", self.read_contextual_trial, self.screen)

    # Segment 1 practice 4-1 + practice 4-2
    def run_c_segment1(self, next_segment_func):
        instruction_flow = []
        for i in range(0, PRACTICE4_2_PAGE):            
            if i == PRACTICE4_1_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.practice4_1))
            elif i == PRACTICE4_2_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.practice4_2))
            else:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], None))

        def after_c_segment1():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < 0.8:
                self.run_c_segment2(next_segment_func)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_c_segment1)

    # Segment 2: repeat practice 4-1 + practice 4-2 (if not pass accuracy requirements)
    def run_c_segment2(self, next_segment_func, repeat_count=1):
        instruction_flow = [(self.C_INSTRUCTION_p4, None)]
        for i in range(PRACTICE4_1_PAGE - 1, PRACTICE4_2_PAGE):
            if i == PRACTICE4_1_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.practice4_1))
            elif i == PRACTICE4_2_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.practice4_2))
            else:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], None))

        def after_c_segment2():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
                self.run_c_segment2(next_segment_func, repeat_count + 1)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_c_segment2)

    # Segment 3: block 5 + block 6
    def run_c_segment3(self, next_segment_func=None):
        instruction_flow = []
        for i in range(PRACTICE4_2_PAGE, len(self.C_ALL_INSTRUCTIONS)):
            if i == BLOCK5_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.block5))
            elif i == BLOCK6_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.block6))
            else:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], None))

        def after_c_segment3():
            if next_segment_func:
                next_segment_func()
            else:
                pygame.quit()
                quit()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_c_segment3)