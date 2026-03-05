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
from utils.paths import load_stimuli
from utils.saves import SaveResultsToCsv


def _clear_trial_input_residue(event_handler, max_wait_ms=3000, stable_ms=120):
    """
    Clear queued input and wait until controls return to a neutral state.
    This prevents held/repeated input from leaking into the next trial.
    """
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None


def _reset_phase_input(expected_direction: str | None = None, expected_key: int | None = None) -> EventHandler:
    """
    Hard-reset all input residues at phase boundary, then create a phase-local handler.
    
    :param expected_direction: For motor tasks, filter joystick to only accept this direction
                               ('left' or 'right'). Use None for sensorimotor (accepts any).
    :param expected_key: For motor tasks, filter keyboard to only accept this key
                         (pygame.K_d or pygame.K_k). Use None for sensorimotor (accepts any).
    """
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None

    event_handler = EventHandler(expected_direction=expected_direction, expected_key=expected_key)

    # Clear events again in case handler init introduced residual device events.
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None
    return event_handler


def _arm_phase_input(event_handler: EventHandler, timeout_ms: int = 1000) -> bool:
    """
    Wait until one neutral frame is observed before accepting responses.
    """
    start_tick = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_tick < timeout_ms:
        state = event_handler.poll()
        if state.quit:
            pygame.quit()
            quit()
        if not (state.option_1 or state.option_2):
            return True
        pygame.time.delay(1)
    return False

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
                    fixation_scaled = get_scaled_stimulus(M_FIXATION, screen)
                    fixation_rect = fixation_scaled.get_rect(center=screen_rect.center)
                    screen.blit(fixation_scaled, fixation_rect)

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
    is_motor_or_sensorimotor = condition in ("motor", "sensorimotor")
    mapping_background = None
    if condition == "sensorimotor":
        mapping_version = getattr(cfg, "version", None) or cfg.MAPPING
        mapping_path = load_stimuli(mapping_version)["mapping"]
        mapping_background = pygame.image.load(str(mapping_path))

    def _scale_contain_to_screen(image, target_screen):
        screen_width, screen_height = target_screen.get_size()
        img_width, img_height = image.get_size()
        scale = min(screen_width / img_width, screen_height / img_height)
        new_size = (max(1, int(img_width * scale)), max(1, int(img_height * scale)))
        return pygame.transform.smoothscale(image, new_size)

    for trial_index, trial in enumerate(trials, start=1):
        print(f"=== STARTING TRIAL - Participant ID: {GetParticipantId()} ===")
        startTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        fixation_time, stimulus_image, type, phase, key_correct = read_trial(trial)


        # Clear event queue/state before each trial starts.
        pygame.event.clear()

        # Trial-level response policy:
        # accept only the first response across fixation/stimulus/ISI.
        _clear_trial_input_residue(EventHandler())
        trial_start_tick = pygame.time.get_ticks()
        trial_end_tick = trial_start_tick + fixation_time + response_time + isi_time

        stimulus_key_response = None
        stimulus_reaction_time = 0
        isi_key_response = None
        isi_reaction_time = 0
        stimulus_joy_response = None
        isi_joy_response = None

        response_recorded = False
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
                if condition == "sensorimotor":
                    screen.fill(BLACK_RGB)
                fixation_rect = M_FIXATION.get_rect(center=screen_rect.center)
                screen.blit(M_FIXATION, fixation_rect)

            elif phase_name == "stimulus":
                pygame.event.clear()
                if condition == "sensorimotor" and mapping_background is not None:
                    screen.fill(BLACK_RGB)
                    mapping_scaled = _scale_contain_to_screen(mapping_background, screen)
                    mapping_rect = mapping_scaled.get_rect(center=screen_rect.center)
                    screen.blit(mapping_scaled, mapping_rect)
                stimulus_rect = stimulus_image.get_rect(center=screen_rect.center)
                screen.blit(stimulus_image, stimulus_rect)
            else:
                screen.fill(BLACK_RGB)

        def _activate_feedback(now_tick):
            nonlocal feedback_active, feedback_deadline_tick
            feedback_active = phase.startswith("p")
            if feedback_active:
                feedback_deadline_tick = min(now_tick + FB_MAX_DURATION, trial_end_tick)

        def _register_first_response(phase_name, now_tick, phase_start_tick, phase_key):
            nonlocal response_recorded
            nonlocal stimulus_key_response, stimulus_reaction_time
            nonlocal isi_key_response, isi_reaction_time
            nonlocal stimulus_joy_response, isi_joy_response
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

            # For motor/sensorimotor stimulus responses, feedback is handled
            # as a blocking overlay in the stimulus phase loop (fixed FB_DURATION).
            if not (is_motor_or_sensorimotor and phase_name == "stimulus"):
                _activate_feedback(now_tick)

        def _run_phase(phase_name, duration_ms):
            nonlocal screen
            phase_start_tick = pygame.time.get_ticks()
            phase_end_tick = phase_start_tick + duration_ms

            # Motor input filters: only accept correct direction/key
            expected_direction = None  # default for sensorimotor
            expected_key = None  # default for sensorimotor
            if condition == "motor" and phase_name == "stimulus" and key_correct is not None:
                expected_direction = "left" if key_correct == pygame.K_d else "right"
                expected_key = key_correct  # pygame.K_d or pygame.K_k

            # Phase-level input isolation: reset queue/state and use a fresh handler.
            event_handler = _reset_phase_input(expected_direction=expected_direction, expected_key=expected_key)
            phase_input_armed = _arm_phase_input(event_handler, timeout_ms=1000)

            # Stimulus onset hard reset: only inputs after actual onset are accepted.
            if phase_name == "stimulus":
                pygame.event.clear()
                cfg.key_response = None
                cfg.joy_response = None
                cfg._input_source = None

            # Motor / Sensorimotor: only stimulus phase accepts input.
            if is_motor_or_sensorimotor and phase_name != "stimulus":
                while pygame.time.get_ticks() < phase_end_tick:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("=== QUIT EVENT DETECTED - EXITING GRACEFULLY ===")
                            pygame.quit()
                            quit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            screen = toggle_fullscreen(screen)
                    _draw_base(phase_name)
                    pygame.display.flip()
                    pygame.time.delay(1)
                return

            while pygame.time.get_ticks() < phase_end_tick:
                state = event_handler.poll()
                now_tick = pygame.time.get_ticks()

                if state.quit:
                    print("=== QUIT EVENT DETECTED - EXITING GRACEFULLY ===")
                    pygame.quit()
                    quit()

                if state.toggle_full_screen:
                    screen = toggle_fullscreen(screen)

                if not phase_input_armed:
                    if not (state.option_1 or state.option_2):
                        phase_input_armed = True
                elif (not response_recorded) and (state.option_1 or state.option_2):
                    phase_key = pygame.K_d if state.option_1 else pygame.K_k
                    _register_first_response(phase_name, now_tick, phase_start_tick, phase_key)

                    # Motor / Sensorimotor rule:
                    # once stimulus gets a response, stimulus phase ends immediately.
                    if is_motor_or_sensorimotor and phase_name == "stimulus":
                        # Practice blocks: show feedback on top of current stimulus,
                        # keep stimulus visible, then move to ISI.
                        if phase.startswith("p"):
                            feedback_until = pygame.time.get_ticks() + FB_DURATION
                            while pygame.time.get_ticks() < feedback_until:
                                _draw_base("stimulus")
                                draw_feedback_overlay(screen, feedback_correct, feedback_timeout)
                                pygame.display.flip()
                                pygame.time.delay(1)
                        break

                _draw_base(phase_name)
                if feedback_active and now_tick < feedback_deadline_tick:
                    draw_feedback_overlay(screen, feedback_correct, feedback_timeout)
                pygame.display.flip()
                pygame.time.delay(1)

            # Practice blocks: if no response during stimulus phase, show "Too Late!" feedback
            # (but not for catch trials)
            if (is_motor_or_sensorimotor and phase_name == "stimulus" and 
                phase.startswith("p") and not response_recorded and type != "no_go"):
                feedback_until = pygame.time.get_ticks() + FB_DURATION
                while pygame.time.get_ticks() < feedback_until:
                    _draw_base("stimulus")
                    draw_feedback_overlay(screen, correct=False, timeout=True)
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
            else SM_AVG_FIXATION_TIME  # fallback
        )
        correct = 1 if (error_type is None) else 0

        # Ensure mutually-exclusive stage recording:
        # if stimulus has input, isi must remain empty.
        if stimulus_key_response is not None:
            isi_key_response = None
        if stimulus_joy_response is not None:
            isi_joy_response = None

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
            "stimulus_key_response": stimulus_key_response,
            "stimulus_reaction_time_ms": stimulus_reaction_time,
            "isi_key_response": isi_key_response,
            "isi_reaction_time_ms": isi_reaction_time,
            "stimulus_joy_response": stimulus_joy_response,
            "isi_joy_response": isi_joy_response,
            "reaction_time_ms": reaction_time,
            "correct": correct,
            "error_type": error_type,
            "input_source": trial_input_source,
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

    def practice1(self, screen):
        results, acc = run_trials(practice1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
        return results, acc

    def block1(self, screen):
        return run_trials(block1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
    
    def practice2(self, screen):
        results, acc = run_trials(practice2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)
        return results, acc

    def block2(self, screen):
        return run_trials(block2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", self.read_motor_trial, screen)

    # Segments (page constants are defined in config)
    def run_m_segment1(self, next_segment_func):
        instruction_flow = []
        # Show instructions 1-5, run practice1 after page 5, skip pages 6-7
        for i in range(0, PRACTICE1_1_PAGE):  # 0-4 (pages 1-5)
            if i == PRACTICE1_1_PAGE - 1:  # After page 5 (index 4)
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.practice1))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment1():
            # No practice pass check - always continue to next segment
            next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment1)

    def run_m_segment3(self, next_segment_func):
        instruction_flow = []
        # Start from page 8 (index 7) to page 15, run practice2 after page 15, skip pages 16-17, then continue from page 18
        for i in range(PRACTICE1_2_PAGE, PRACTICE2_1_PAGE):  # Pages 8-14
            if i == BLOCK1_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.block1))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))
        # Add page 15 with practice2
        instruction_flow.append((self.M_ALL_INSTRUCTIONS[PRACTICE2_1_PAGE - 1], self.practice2))
        # Skip pages 16-17 (PRACTICE2_2_PAGE)
        # Continue from page 18 onwards
        for i in range(PRACTICE2_2_PAGE, BLOCK2_PAGE):
            instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment3():
            # No practice pass check - always continue to next segment
            next_segment_func()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment3)

    def run_m_segment4(self, next_segment_func=None):
        instruction_flow = []
        for i in range(BLOCK2_PAGE - 1, len(self.M_ALL_INSTRUCTIONS)):
            if i == BLOCK2_PAGE - 1:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], self.block2))
            else:
                instruction_flow.append((self.M_ALL_INSTRUCTIONS[i], None))

        def after_segment4():
            if next_segment_func:
                next_segment_func()
            else:
                pygame.quit()
                quit()

        run_instruction_sequence(self.screen, instruction_flow, self.all_results, self.all_acc, after_segment4)
