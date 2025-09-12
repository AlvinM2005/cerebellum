import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from save_results import *
from instructions import *
from datetime import datetime
from instructions import Instructions

# General key input / response function 
def key_logging(time_allowed, screen, current_image=None, is_fixation=False, condition="motor"):
    """
    Enhanced key logging with fullscreen toggle support and screen redraw
    current_image: the current image being displayed (for redraw after toggle)
    is_fixation: whether we're currently showing fixation or stimulus
    condition: task condition to determine which fixation to use
    """
    start_time = pygame.time.get_ticks()
    key_response = None
    reaction_time = 0

    while pygame.time.get_ticks() - start_time < time_allowed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Handle window close button (X) - graceful exit
                print("=== QUIT EVENT DETECTED - EXITING GRACEFULLY ===")
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Handle ESC key for fullscreen toggle
                    from framework import toggle_fullscreen
                    screen = toggle_fullscreen(screen)  # Update screen reference
                    
                    # Redraw the current screen after toggle
                    screen.fill(GRAY_RGB)  # Clear screen first
                    screen_rect = screen.get_rect()
                    
                    if current_image is not None:
                        # Redraw the current image with new scaling
                        if is_fixation:
                            # Redraw fixation
                            if condition in ["motor", "sensorimotor"]:
                                fixation_scaled = get_scaled_stimulus(M_FIXATION, screen)
                                fixation_rect = fixation_scaled.get_rect(center=screen_rect.center)
                                screen.blit(fixation_scaled, fixation_rect)
                            else:
                                contextual_fixation_scaled = get_scaled_stimulus(CONTEXTUAL_FIXATION, screen)
                                contextual_fixation_rect = contextual_fixation_scaled.get_rect(center=screen_rect.center)
                                screen.blit(contextual_fixation_scaled, contextual_fixation_rect)
                        else:
                            # Redraw stimulus
                            stimulus_scaled = get_scaled_stimulus(current_image, screen)
                            stimulus_rect = stimulus_scaled.get_rect(center=screen_rect.center)
                            screen.blit(stimulus_scaled, stimulus_rect)
                    
                    pygame.display.flip()
                    
                elif key_response is None and event.key in [pygame.K_d, pygame.K_k]:
                    # Only accept D and K keys as valid responses
                    key_response = event.key
                    reaction_time = pygame.time.get_ticks() - start_time
                    # Break immediately after getting a valid response
                    break
                # Ignore all other keys (no feedback, no action)
        
        # Break the outer loop if we got a response
        if key_response is not None:
            break
        
        # Small delay to prevent high CPU usage
        pygame.time.delay(1)

    pygame.event.clear()
    return key_response, reaction_time

# Run trials
def run_trials(trials, response_time, isi_time, condition, read_trial, screen):
    total_trials = 0
    correct_count = 0
    results = []

    for trial in trials:
        print(f"=== STARTING TRIAL - Participant ID: {GetParticipantId()} ===")
        startTime = datetime.now().strftime("%y/%m/%d %H:%M:%S")

        fixation_time, stimulus_image, type, phase, key_correct = read_trial(trial)

        # Fixation - centered on screen with appropriate scaling
        screen_rect = screen.get_rect()
        if (condition == "motor"
            or condition == "sensorimotor"):
            fixation_scaled = get_scaled_stimulus(M_FIXATION, screen)
            fixation_rect = fixation_scaled.get_rect(center=screen_rect.center)
            screen.blit(fixation_scaled, fixation_rect)
            pygame.display.flip()
            fixation_key_response, fixation_reaction_time = key_logging(fixation_time, screen, M_FIXATION, True, condition)
        else:
            contextual_fixation_scaled = get_scaled_stimulus(CONTEXTUAL_FIXATION, screen)
            contextual_fixation_rect = contextual_fixation_scaled.get_rect(center=screen_rect.center)
            screen.blit(contextual_fixation_scaled, contextual_fixation_rect)
            pygame.display.flip()
            fixation_key_response, fixation_reaction_time = key_logging(fixation_time, screen, CONTEXTUAL_FIXATION, True, condition)

        # Stimulus - centered on screen with appropriate scaling
        screen.fill(GRAY_RGB)  # Clear screen before showing stimulus
        stimulus_scaled = get_scaled_stimulus(stimulus_image, screen)
        stimulus_rect = stimulus_scaled.get_rect(center=screen_rect.center)
        screen.blit(stimulus_scaled, stimulus_rect)
        pygame.display.flip()
        stimulus_key_response, stimulus_reaction_time = key_logging(response_time, screen, stimulus_image, False, condition)

        if phase.startswith("practice"):
            if type == "no_go":
                correct = 1 if (fixation_key_response is None and stimulus_key_response is None) else 0
                timeout = False
            else:
                correct = 1 if (stimulus_key_response == key_correct) else 0
                timeout = (fixation_key_response is None and stimulus_key_response is None)
            show_feedback(screen, correct, timeout, stimulus_image)

        # ISI
        screen.fill(GRAY_RGB)
        pygame.display.flip()
        isi_key_response, isi_reaction_time = key_logging(isi_time, screen, None, False, condition)

        # Determine error type
        error_type = None
        if stimulus_key_response != key_correct:
            if type == "no_go":
                if stimulus_key_response is not None:
                    error_type = "no_go_error"
                elif isi_key_response is not None:
                    error_type = "no_go_delay_error"
            else:
                if stimulus_key_response is None:
                    if isi_key_response is not None:
                        error_type = "delay_error"
                    else:
                        error_type = "no_response"

        avg_fixation_time = (
            M_AVG_FIXATION_TIME if condition == "motor"
            else C_AVG_FIXATION_TIME if condition == "contextual"
            else SM_AVG_FIXATION_TIME  # fallback
        )
        correct = 1 if (error_type is None) else 0

        endTime = datetime.now().strftime("%y/%m/%d %H:%M:%S")

        partResult = {
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
        }
        print("=== TRIAL COMPLETE - SAVING DATA ===")
        print("record part result, participateID=", GetParticipantId())
        print("Trial data:", partResult)
        print("Start time:", startTime, "End time:", endTime)
        try:
            SaveResultsToCsv("results.csv", GetParticipantId(), partResult, startTime, endTime)
            print("=== DATA SAVED SUCCESSFULLY ===")
        except Exception as e:
            print("=== ERROR SAVING DATA ===")
            print("Error:", str(e))
            import traceback
            traceback.print_exc()

        total_trials += 1
        if correct:
            correct_count += 1

    accuracy = correct_count / total_trials
    return results, accuracy

# ========== Motor 类（加入 version + Instructions 实例） ==========
class Motor:
    def __init__(self, screen, all_results, all_acc, version):
        self.screen = screen
        self.all_results = all_results
        self.all_acc = all_acc

        # ⭐️ 初始化并生成路径/图片
        self.instructions = Instructions(version)
        self.instructions.generate_paths(version)

        # 为了少写长名字，做个简短引用
        self.M_ALL_INSTRUCTIONS = self.instructions.M_ALL_INSTRUCTIONS
        self.M_INSTRUCTION_p1 = self.instructions.M_INSTRUCTION_p1
        self.M_INSTRUCTION_p2 = self.instructions.M_INSTRUCTION_p2

        self.version = version
    
    # Read information from trials
    def read_motor_trial(self, trial):
        fixation_time, stimulus_image, phase = trial
        if stimulus_image == M_BLUE:
            if self.version == 1:
                key_correct = pygame.K_d
            else:
                key_correct = pygame.K_k
            type = "actual"
        elif stimulus_image == M_RED:
            if self.version == 1:
                key_correct = pygame.K_k
            else:
                key_correct = pygame.K_d
            type = "actual"
        elif stimulus_image == M_NOGO:
            key_correct = None
            type = "no_go"
        return fixation_time, stimulus_image, type, phase, key_correct

    def practice1_1(self, screen):
        return run_trials(practice1_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    def practice1_2(self, screen):
        return run_trials(practice1_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    def block1(self, screen):
        return run_trials(block1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
    
    def practice2_1(self, screen):
        return run_trials(practice2_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    def practice2_2(self, screen):
        return run_trials(practice2_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    def block2(self, screen):
        return run_trials(block2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    # Segments （把全局常量页码依旧用 meta_parameters 里的）
    def run_m_segment1(self, next_segment_func):
        instruction_flow = []
        for i in range(0, PRACTICE1_2_PAGE):
            if i == PRACTICE1_1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1_1))
            elif i == PRACTICE1_2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1_2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment1():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < 0.8:
                self.run_m_segment2(next_segment_func)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment1)

    def run_m_segment2(self, next_segment_func, repeat_count=1):
        instruction_flow = [(self.M_INSTRUCTION_p1, None)]
        for i in range(PRACTICE1_1_PAGE - 1, PRACTICE1_2_PAGE):
            if i == PRACTICE1_1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1_1))
            elif i == PRACTICE1_2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1_2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment2():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
                self.run_m_segment2(next_segment_func, repeat_count + 1)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment2)

    def run_m_segment3(self, next_segment_func):
        instruction_flow = []
        for i in range(PRACTICE1_2_PAGE, PRACTICE2_2_PAGE):
            if i == BLOCK1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.block1))
            elif i == PRACTICE2_1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice2_1))
            elif i == PRACTICE2_2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice2_2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment3():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < ACCURACY:
                self.run_m_segment4(next_segment_func)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment3)

    def run_m_segment4(self, next_segment_func, repeat_count=1):
        instruction_flow = [(self.M_INSTRUCTION_p2, None)]
        for i in range(PRACTICE2_1_PAGE - 1, PRACTICE2_2_PAGE):
            if i == PRACTICE2_1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice2_1))
            elif i == PRACTICE2_2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice2_2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment4():
            acc_mean = sum(self.all_acc[-2:]) / 2
            if acc_mean < ACCURACY and repeat_count < MAX_REPEAT - 1:
                self.run_m_segment4(next_segment_func, repeat_count + 1)
            else:
                next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment4)

    def run_m_segment5(self, next_segment_func=None):
        instruction_flow = []
        for i in range(PRACTICE2_2_PAGE, len(self.M_ALL_INSTRUCTIONS)):
            if i == BLOCK2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.block2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment5():
            if next_segment_func:
                next_segment_func()
            else:
                pygame.quit()
                quit()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment5)