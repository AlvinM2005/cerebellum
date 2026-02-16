from datetime import datetime

import pygame

from core.feedback import *
from core.framework import *
from core.generate_trials import *
from core.instructions import *
from core.instructions import Instructions
from core.stimuli import *
from utils.event_handler import EventHandler
import utils.config as cfg
from utils.config import *
from utils.save_results import *


def _clear_trial_input_residue(event_handler, max_wait_ms=3000, stable_ms=120):
    """
    Clear queued input and wait until controls return to a neutral state.
    This prevents held/repeated input from leaking into the next trial.
    """
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None

    start_tick = pygame.time.get_ticks()
    neutral_start = None
    while pygame.time.get_ticks() - start_tick < max_wait_ms:
        state = event_handler.poll()
        if state.quit:
            pygame.quit()
            quit()
        active = state.option_1 or state.option_2 or state.next_page or state.confirm
        if not active:
            if neutral_start is None:
                neutral_start = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - neutral_start >= stable_ms:
                break
        else:
            neutral_start = None
        pygame.time.delay(1)

    # Final hard reset right before trial starts.
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None

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
    event_handler = EventHandler()

    while pygame.time.get_ticks() - start_time < time_allowed:
        state = event_handler.poll()

        if state.quit:
            print("=== QUIT EVENT DETECTED - EXITING GRACEFULLY ===")
            pygame.quit()
            quit()

        if state.toggle_full_screen:
            # Handle fullscreen toggle
            screen = toggle_fullscreen(screen)

            # Redraw the current screen after toggle
            screen.fill(BLACK_RGB)
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

        if key_response is None and (state.option_1 or state.option_2):
            key_response = pygame.K_d if state.option_1 else pygame.K_k
            reaction_time = pygame.time.get_ticks() - start_time

        # Small delay to prevent high CPU usage
        pygame.time.delay(1)

    pygame.event.clear()
    return key_response, reaction_time


def is_practice_passed(trial_results):
    """
    Practice pass rule:
    1) at least ACCURACY proportion of trials are correct
    2) no trial has error_type == "catch_error"
    """
    if not trial_results:
        return False
    total = len(trial_results)
    correct_count = sum(1 for row in trial_results if bool(row.get("correct")))
    has_catch_error = any((row.get("error_type") == "catch_error") for row in trial_results)
    return (correct_count / total) >= ACCURACY and (not has_catch_error)


# Run trials
def run_trials(trials, response_time, isi_time, condition, read_trial, screen):
    total_trials = 0
    correct_count = 0
    results = []

    block_start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    for trial_index, trial in enumerate(trials, start=1):
        print(f"=== STARTING TRIAL - Participant ID: {GetParticipantId()} ===")
        startTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        trial_info = read_trial(trial)
        if len(trial_info) >= 6:
            fixation_time, stimulus_image, type, phase, key_correct, trial_meta = trial_info
        else:
            fixation_time, stimulus_image, type, phase, key_correct = trial_info
            trial_meta = {}

        # Trial-level response policy:
        # accept only the first response across fixation/stimulus/ISI.
        event_handler = EventHandler()
        _clear_trial_input_residue(event_handler)
        trial_start_tick = pygame.time.get_ticks()
        stimulus_start_tick = trial_start_tick + fixation_time
        trial_end_tick = trial_start_tick + fixation_time + response_time + isi_time

        fixation_key_response = None
        fixation_reaction_time = 0
        stimulus_key_response = None
        stimulus_reaction_time = 0
        isi_key_response = None
        isi_reaction_time = 0
        fixation_joy_response = None
        stimulus_joy_response = None
        isi_joy_response = None

        response_recorded = False
        # Arm input only after seeing a neutral frame in this trial,
        # so held keys/stick from previous trial cannot be captured.
        input_armed = False
        trial_input_source = None
        error_type = None
        correct = 0
        reaction_time = 0

        feedback_active = False
        feedback_correct = False
        feedback_timeout = False
        feedback_deadline_tick = 0

        def _draw_base(phase_name):
            screen_rect = screen.get_rect()
            if phase_name == "fixation":
                if condition in ["motor", "sensorimotor"]:
                    fixation_scaled = get_scaled_stimulus(M_FIXATION, screen)
                    fixation_rect = fixation_scaled.get_rect(center=screen_rect.center)
                    screen.fill(BLACK_RGB)
                    screen.blit(fixation_scaled, fixation_rect)
                else:
                    contextual_fixation_scaled = get_scaled_stimulus(CONTEXTUAL_FIXATION, screen)
                    contextual_fixation_rect = contextual_fixation_scaled.get_rect(center=screen_rect.center)
                    screen.fill(BLACK_RGB)
                    screen.blit(contextual_fixation_scaled, contextual_fixation_rect)
            elif phase_name == "stimulus":
                stimulus_scaled = get_scaled_stimulus(stimulus_image, screen)
                stimulus_rect = stimulus_scaled.get_rect(center=screen_rect.center)
                screen.fill(BLACK_RGB)
                screen.blit(stimulus_scaled, stimulus_rect)
            else:
                screen.fill(BLACK_RGB)

        def _activate_feedback(now_tick):
            nonlocal feedback_active, feedback_deadline_tick
            feedback_active = phase.startswith("p")
            if feedback_active:
                feedback_deadline_tick = min(now_tick + FB_MAX_DURATION, trial_end_tick)

        def _register_first_response(phase_name, now_tick, phase_start_tick, phase_key):
            nonlocal response_recorded
            nonlocal fixation_key_response, fixation_reaction_time
            nonlocal stimulus_key_response, stimulus_reaction_time
            nonlocal isi_key_response, isi_reaction_time
            nonlocal fixation_joy_response, stimulus_joy_response, isi_joy_response
            nonlocal error_type, correct, feedback_correct, feedback_timeout
            nonlocal reaction_time
            nonlocal trial_input_source

            if response_recorded:
                return
            response_recorded = True

            phase_rt = now_tick - phase_start_tick
            source = cfg._input_source
            trial_input_source = source
            joy_raw = cfg.joy_response
            if phase_name == "fixation":
                if source == "joy":
                    fixation_joy_response = joy_raw
                else:
                    fixation_key_response = phase_key
                fixation_reaction_time = phase_rt
                error_type = "pre-mature_error"
                correct = 0
                feedback_correct = False
                reaction_time = 0
            elif phase_name == "stimulus":
                if source == "joy":
                    stimulus_joy_response = joy_raw
                else:
                    stimulus_key_response = phase_key
                stimulus_reaction_time = phase_rt
                reaction_time = phase_rt
                if type == "no_go":
                    error_type = "catch_error"
                    correct = 0
                    feedback_correct = False
                else:
                    correct = 1 if (phase_key == key_correct) else 0
                    error_type = None if correct else "response_error"
                    feedback_correct = bool(correct)
            else:
                if source == "joy":
                    isi_joy_response = joy_raw
                else:
                    isi_key_response = phase_key
                isi_reaction_time = phase_rt
                if type == "no_go":
                    error_type = "catch_delay_error"
                else:
                    error_type = "delay_error"
                correct = 0
                feedback_correct = False
                reaction_time = 0

            _activate_feedback(now_tick)

        def _run_phase(phase_name, duration_ms):
            nonlocal screen
            nonlocal input_armed
            phase_start_tick = pygame.time.get_ticks()
            while pygame.time.get_ticks() - phase_start_tick < duration_ms:
                state = event_handler.poll()
                now_tick = pygame.time.get_ticks()

                if state.quit:
                    print("=== QUIT EVENT DETECTED - EXITING GRACEFULLY ===")
                    pygame.quit()
                    quit()

                if state.toggle_full_screen:
                    screen = toggle_fullscreen(screen)

                if not input_armed:
                    if not (state.option_1 or state.option_2):
                        input_armed = True
                elif (not response_recorded) and (state.option_1 or state.option_2):
                    phase_key = pygame.K_d if state.option_1 else pygame.K_k
                    _register_first_response(phase_name, now_tick, phase_start_tick, phase_key)

                _draw_base(phase_name)
                if feedback_active and now_tick < feedback_deadline_tick:
                    draw_feedback_overlay(screen, feedback_correct, feedback_timeout)
                pygame.display.flip()
                pygame.time.delay(1)

        _run_phase("fixation", fixation_time)
        _run_phase("stimulus", response_time)
        _run_phase("isi", isi_time)

        # No response across all three phases
        if not response_recorded:
            if type == "no_go":
                correct = 1
                error_type = None
            else:
                correct = 0
                error_type = "no_response"
                reaction_time = 0

        avg_fixation_time = (
            M_AVG_FIXATION_TIME if condition == "motor"
            else C_AVG_FIXATION_TIME if condition == "contextual"
            else SM_AVG_FIXATION_TIME  # fallback
        )
        correct = 1 if (error_type is None) else 0

        endTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        key_correct_out = key_correct
        joy_correct_out = None
        if key_correct == pygame.K_d:
            joy_correct_out = "left"
        elif key_correct == pygame.K_k:
            joy_correct_out = "right"

        partResult = {
            "trial_number": trial_index,
            "block": phase,
            "type": type,
            "fixation_time": fixation_time,
            "condition": condition,
            "is_catch": (type == "no_go"),
            "difficulty": abs(fixation_time - avg_fixation_time),
            "key_correct": key_correct_out,
            "joy_correct": joy_correct_out,
            "fixation_key_response": fixation_key_response,
            "fixation_reaction_time_ms": fixation_reaction_time,
            "stimulus_key_response": stimulus_key_response,
            "stimulus_reaction_time_ms": stimulus_reaction_time,
            "isi_key_response": isi_key_response,
            "isi_reaction_time_ms": isi_reaction_time,
            "fixation_joy_response": fixation_joy_response,
            "stimulus_joy_response": stimulus_joy_response,
            "isi_joy_response": isi_joy_response,
            "reaction_time_ms": reaction_time,
            "correct": correct,
            "error_type": error_type,
            "input_source": trial_input_source,
            "context_color": trial_meta.get("context_color"),
            "case_type": trial_meta.get("case_type"),
            "phonetic_type": trial_meta.get("phonetic_type"),
            "congruency": trial_meta.get("congruency"),
            "switch_type": trial_meta.get("switch_type"),
            "letter": trial_meta.get("letter"),
            "block_start_time": block_start_time,
            "block_end_time": endTime,
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

        results.append(partResult)
        total_trials += 1
        if correct:
            correct_count += 1

    accuracy = correct_count / total_trials
    return results, accuracy

# ========== Motor class (with version + Instructions instance) ==========
class Motor:
    def __init__(self, screen, all_results, all_acc, version):
        self.screen = screen
        self.all_results = all_results
        self.all_acc = all_acc

        # Initialize and generate instruction paths/images
        self.instructions = Instructions(version)
        self.instructions.generate_paths(version)

        # Short aliases for instruction references
        self.M_ALL_INSTRUCTIONS = self.instructions.M_ALL_INSTRUCTIONS
        self.M_INSTRUCTION_p1 = self.instructions.M_INSTRUCTION_p1
        self.M_INSTRUCTION_p2 = self.instructions.M_INSTRUCTION_p2

        self.version = version
        self._practice1_1_pass = False
        self._practice1_2_pass = False
        self._practice2_1_pass = False
        self._practice2_2_pass = False
    
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
        results, acc = run_trials(practice1_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
        self._practice1_1_pass = is_practice_passed(results)
        return results, acc

    def practice1_2(self, screen):
        results, acc = run_trials(practice1_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
        self._practice1_2_pass = is_practice_passed(results)
        return results, acc

    def block1(self, screen):
        return run_trials(block1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
    
    def practice2_1(self, screen):
        results, acc = run_trials(practice2_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
        self._practice2_1_pass = is_practice_passed(results)
        return results, acc

    def practice2_2(self, screen):
        results, acc = run_trials(practice2_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
        self._practice2_2_pass = is_practice_passed(results)
        return results, acc

    def block2(self, screen):
        return run_trials(block2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    # Segments (page constants are defined in config)
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
            if self._practice1_1_pass and self._practice1_2_pass:
                next_segment_func()
            else:
                self.run_m_segment2(next_segment_func, repeat_count=0)

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment1)

    def run_m_segment2(self, next_segment_func, repeat_count=0):
        instruction_flow = [(self.M_INSTRUCTION_p1, None)]
        for i in range(PRACTICE1_1_PAGE - 1, PRACTICE1_2_PAGE):
            if i == PRACTICE1_1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1_1))
            elif i == PRACTICE1_2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1_2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment2():
            if not (self._practice1_1_pass and self._practice1_2_pass) and repeat_count < PRACTICE_REPEAT - 1:
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
            if self._practice2_1_pass and self._practice2_2_pass:
                next_segment_func()
            else:
                self.run_m_segment4(next_segment_func, repeat_count=0)

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment3)

    def run_m_segment4(self, next_segment_func, repeat_count=0):
        instruction_flow = [(self.M_INSTRUCTION_p2, None)]
        for i in range(PRACTICE2_1_PAGE - 1, PRACTICE2_2_PAGE):
            if i == PRACTICE2_1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice2_1))
            elif i == PRACTICE2_2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice2_2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment4():
            if not (self._practice2_1_pass and self._practice2_2_pass) and repeat_count < PRACTICE_REPEAT - 1:
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
