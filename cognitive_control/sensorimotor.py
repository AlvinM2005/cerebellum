import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from motor import key_logging, run_trials

class Sensorimotor:
    def __init__(self, screen, all_results, all_acc, version):
        self.screen = screen
        self.all_results = all_results
        self.all_acc = all_acc
        self.version = version

        # ⭐️ 初始化并生成路径/图片
        self.instructions = Instructions(version)
        self.instructions.generate_paths(version)

        # 为了少写长名字，做个简短引用
        self.SM_ALL_INSTRUCTIONS = self.instructions.SM_ALL_INSTRUCTIONS
        self.SM_INSTRUCTION_p3 = self.instructions.SM_INSTRUCTION_p3

        # 创建 stimuli 实例
        self.stimuli = SensorimotorStimuli(version)

        # 生成 trial
        self.practice3_1_trials = self.create_sm_trials(
            PRACTICE3_1_NUM_RED, PRACTICE3_1_NUM_BLUE, PRACTICE3_1_NUM_NOGO, "practice3_1"
        )
        self.practice3_2_trials = self.create_sm_trials(
            PRACTICE3_2_NUM_RED, PRACTICE3_2_NUM_BLUE, PRACTICE3_2_NUM_NOGO, "practice3_2"
        )
        self.block3_trials = self.create_sm_trials(
            BLOCK3_NUM_RED, BLOCK3_NUM_BLUE, BLOCK3_NUM_NOGO, "block3"
        )
        self.block4_trials = self.create_sm_trials(
            BLOCK4_NUM_RED, BLOCK4_NUM_BLUE, BLOCK4_NUM_NOGO, "block4"
        )
    
    # Generate trials
    def create_sm_trials(self, num_red, num_blue, num_nogo, phase):
        trials = []
        for _ in range(num_red):
            time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
            trials.append([time, self.stimuli.SM_RED, phase])
        for _ in range(num_blue):
            time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
            trials.append([time, self.stimuli.SM_BLUE, phase])
        for _ in range(num_nogo):
            time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
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
        return run_trials(self.practice3_1_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", self.read_sensorimotor_trial, screen)

    def practice3_2(self, screen):
        return run_trials(self.practice3_2_trials, SM_RESPONSE_TIME, SM_ISI_TIME, "sensorimotor", self.read_sensorimotor_trial, screen)

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
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < 0.8:
                self.run_sm_segment2(next_segment_func)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_sm_segment1)

    # Segment 2: repeat practice 3-1 + practice 3-2 (if not pass accuracy requirements)
    def run_sm_segment2(self, next_segment_func, repeat_count=1):
        instruction_flow = [(self.SM_INSTRUCTION_p3, None)]
        for i in range(PRACTICE3_1_PAGE - 1, PRACTICE3_2_PAGE):
            if i == PRACTICE3_1_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.practice3_1))
            elif i == PRACTICE3_2_PAGE - 1:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], self.practice3_2))
            else:
                instruction_flow.append((self.SM_ALL_INSTRUCTIONS[i], None))

        def after_sm_segment2():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
                self.run_sm_segment2(repeat_count + 1)
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