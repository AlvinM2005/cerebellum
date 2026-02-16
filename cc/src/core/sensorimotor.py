import pygame

from core.feedback import *
from core.framework import *
from core.generate_trials import *
from core.motor import key_logging, run_trials, is_practice_passed
from core.stimuli import *
from utils.config import *

class Sensorimotor:
    def __init__(self, screen, all_results, all_acc, version):
        self.screen = screen
        self.all_results = all_results
        self.all_acc = all_acc
        self.version = version

        # Initialize and generate instruction paths/images
        self.instructions = Instructions(version)
        self.instructions.generate_paths(version)

        # Short aliases for instruction references
        self.SM_ALL_INSTRUCTIONS = self.instructions.SM_ALL_INSTRUCTIONS
        self.SM_INSTRUCTION_p3 = self.instructions.SM_INSTRUCTION_p3

        # Create stimuli instance
        self.stimuli = SensorimotorStimuli(version)

        # Generate trials
        self.practice3_1_trials = self.create_sm_trials(
            PRACTICE3_1_NUM_RED, PRACTICE3_1_NUM_BLUE, PRACTICE3_1_NUM_NOGO, "p3"
        )
        self.practice3_2_trials = self.create_sm_trials(
            PRACTICE3_2_NUM_RED, PRACTICE3_2_NUM_BLUE, PRACTICE3_2_NUM_NOGO, "p3"
        )
        self.block3_trials = self.create_sm_trials(
            BLOCK3_NUM_RED, BLOCK3_NUM_BLUE, BLOCK3_NUM_NOGO, "b3"
        )
        self.block4_trials = self.create_sm_trials(
            BLOCK4_NUM_RED, BLOCK4_NUM_BLUE, BLOCK4_NUM_NOGO, "b4"
        )
        self._practice3_1_pass = False
        self._practice3_2_pass = False
    
    # Generate trials
    def create_sm_trials(self, num_red, num_blue, num_nogo, phase):
        trials = []
        for _ in range(num_red):
            time = random.randint(SM_MIN_FIXATION_TIME, SM_MAX_FIXATION_TIME)
            trials.append([time, self.stimuli.SM_RED, phase])
        for _ in range(num_blue):
            time = random.randint(SM_MIN_FIXATION_TIME, SM_MAX_FIXATION_TIME)
            trials.append([time, self.stimuli.SM_BLUE, phase])
        for _ in range(num_nogo):
            time = random.randint(SM_MIN_FIXATION_TIME, SM_MAX_FIXATION_TIME)
            trials.append([time, self.stimuli.SM_NOGO, phase])
        random.shuffle(trials)
        return trials

    # Read information from trials
    def read_sensorimotor_trial(self, trial):
        fixation_time, stimulus_image, phase = trial
        if stimulus_image == self.stimuli.SM_BLUE:
            if self.version == 1:
                key_correct = pygame.K_d
            else:
                key_correct = pygame.K_k
            type = "actual"
        elif stimulus_image == self.stimuli.SM_RED:
            if self.version == 1:
                key_correct = pygame.K_k
            else:
                key_correct = pygame.K_d
            type = "actual"
        elif stimulus_image == self.stimuli.SM_NOGO:
            key_correct = None
            type = "no_go"
        return fixation_time, stimulus_image, type, phase, key_correct

    def practice3_1(self, screen):
        results, acc = run_trials(self.practice3_1_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", self.read_sensorimotor_trial, screen)
        self._practice3_1_pass = is_practice_passed(results)
        return results, acc

    def practice3_2(self, screen):
        results, acc = run_trials(self.practice3_2_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", self.read_sensorimotor_trial, screen)
        self._practice3_2_pass = is_practice_passed(results)
        return results, acc

    def block3(self, screen):
        return run_trials(self.block3_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", self.read_sensorimotor_trial, screen)

    def block4(self, screen):
        return run_trials(self.block4_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", self.read_sensorimotor_trial, screen)

    # Segment 1 practice 3-1 + practice 3-2
    def run_sm_segment1(self, next_segment_func):
        instruction_flow = []
        for i in range(0, PRACTICE3_2_PAGE):            
            if i == PRACTICE3_1_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.practice3_1))
            elif i == PRACTICE3_2_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.practice3_2))
            else:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], None))

        def after_sm_segment1():
            if self._practice3_1_pass and self._practice3_2_pass:
                next_segment_func()
            else:
                self.run_sm_segment2(next_segment_func, repeat_count=0)

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_sm_segment1)

    # Segment 2: repeat practice 3-1 + practice 3-2 (if not pass accuracy requirements)
    def run_sm_segment2(self, next_segment_func, repeat_count=0):
        instruction_flow = [(self.SM_INSTRUCTION_p3, None)]
        for i in range(PRACTICE3_1_PAGE - 1, PRACTICE3_2_PAGE):
            if i == PRACTICE3_1_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.practice3_1))
            elif i == PRACTICE3_2_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.practice3_2))
            else:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], None))

        def after_sm_segment2():
            if not (self._practice3_1_pass and self._practice3_2_pass) and repeat_count < PRACTICE_REPEAT - 1:
                self.run_sm_segment2(next_segment_func, repeat_count + 1)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_sm_segment2)

    # Segment 3: block 3 + block 4
    def run_sm_segment3(self, next_segment_func=None):
        instruction_flow = []
        for i in range(PRACTICE3_2_PAGE, len(self.SM_ALL_INSTRUCTIONS)):
            if i == BLOCK3_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.block3))
            elif i == BLOCK4_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.block4))
            else:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], None))

        def after_sm_segment3():
            if next_segment_func:
                next_segment_func()
            else:
                pygame.quit()
                quit()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_sm_segment3)
