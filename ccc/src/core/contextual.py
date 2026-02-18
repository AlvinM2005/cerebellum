import pygame

from core.feedback import *
from core.framework import *
from core.generate_trials import *
from core.stimuli import *
from core.trial_runner import run_trials, is_practice_passed
from utils.config import *

class Contextual:
    def __init__(self, screen, all_results, all_acc, version):
        self.screen = screen
        self.all_results = all_results
        self.all_acc = all_acc

        # Initialize and generate instruction paths/images
        self.instructions = Instructions(version)
        self.instructions.generate_paths(version)

        # Short aliases for instruction references
        self.C_ALL_INSTRUCTIONS = self.instructions.C_ALL_INSTRUCTIONS
        self.C_INSTRUCTION_p4 = self.instructions.C_INSTRUCTION_p4

        self.version = version

        self.practice4_1_trials = create_contextual_practice_trials("p1", self.version, color="yellow")
        self.practice4_2_trials = create_contextual_practice_trials("p2", self.version, color="pink")
        self.block5_trials = create_contextual_block1_trials(self.version)
        self.block6_trials = create_contextual_block2_trials(self.version)
        self._practice4_1_pass = False
        self._practice4_2_pass = False

    # Read information from trials
    def read_contextual_trial(self, trial):
        if len(trial) >= 6:
            stimulus_image, key_correct, trial_type, phase, fixation_time, trial_meta = trial
        else:
            stimulus_image, key_correct, trial_type, phase, fixation_time = trial
            trial_meta = {}
        return fixation_time, stimulus_image, trial_type, phase, key_correct, trial_meta

    def practice4_1(self, screen):
        results, acc = run_trials(self.practice4_1_trials, C_RESPONSE_TIME, C_ISI_TIME, self.read_contextual_trial, self.screen)
        self._practice4_1_pass = is_practice_passed(results)
        return results, acc

    def practice4_2(self, screen):
        results, acc = run_trials(self.practice4_2_trials, C_RESPONSE_TIME, C_ISI_TIME, self.read_contextual_trial, self.screen)
        self._practice4_2_pass = is_practice_passed(results)
        return results, acc

    def block5(self, screen):
        return run_trials(self.block5_trials, C_RESPONSE_TIME, C_ISI_TIME, self.read_contextual_trial, self.screen)

    def block6(self, screen):
        return run_trials(self.block6_trials, C_RESPONSE_TIME, C_ISI_TIME, self.read_contextual_trial, self.screen)

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
            if self._practice4_1_pass and self._practice4_2_pass:
                next_segment_func()
            else:
                self.run_c_segment2(next_segment_func, repeat_count=0)

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_c_segment1)

    # Segment 2: repeat practice 4-1 + practice 4-2 (if not pass accuracy requirements)
    def run_c_segment2(self, next_segment_func, repeat_count=0):
        instruction_flow = [(self.C_INSTRUCTION_p4, None)]
        for i in range(PRACTICE4_1_PAGE - 1, PRACTICE4_2_PAGE):
            if i == PRACTICE4_1_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.practice4_1))
            elif i == PRACTICE4_2_PAGE - 1:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], self.practice4_2))
            else:
                instruction_flow.append((self.C_ALL_INSTRUCTIONS[i], None))

        def after_c_segment2():
            if not (self._practice4_1_pass and self._practice4_2_pass) and repeat_count < PRACTICE_REPEAT - 1:
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
