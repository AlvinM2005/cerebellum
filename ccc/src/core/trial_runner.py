from datetime import datetime

import pygame

from core.feedback import draw_feedback_overlay
from core.framework import GetParticipantId, get_scaled_stimulus, toggle_fullscreen
from core.stimuli import CONTEXTUAL_FIXATION, get_contextual_mapping_background
from utils.config import *
from utils.event_handler import EventHandler
from utils.saves import SaveResultsToCsv
import utils.config as cfg

_MAPPING_BG_CACHE: dict[tuple[int, int, int], pygame.Surface] = {}


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


def _clear_trial_input_residue(event_handler):
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None


def _reset_phase_input() -> EventHandler:
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None

    event_handler = EventHandler()
    pygame.event.clear()
    cfg.key_response = None
    cfg.joy_response = None
    cfg._input_source = None
    return event_handler


def _arm_phase_input(event_handler: EventHandler, timeout_ms: int = 1000) -> bool:
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


def run_trials(trials, response_time, isi_time, read_trial, screen):
    total_trials = 0
    correct_count = 0
    results = []

    block_start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    for trial_index, trial in enumerate(trials, start=1):
        startTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        trial_info = read_trial(trial)
        if len(trial_info) >= 6:
            fixation_time, stimulus_image, trial_type, phase, key_correct, trial_meta = trial_info
        else:
            fixation_time, stimulus_image, trial_type, phase, key_correct = trial_info
            trial_meta = {}

        _clear_trial_input_residue(EventHandler())

        trial_start_tick = pygame.time.get_ticks()
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
        trial_input_source = None
        error_type = None
        correct = 0
        reaction_time = 0

        feedback_active = False
        feedback_correct = False
        feedback_timeout = False
        feedback_deadline_tick = 0

        def _get_scaled_mapping_bg():
            mapping = cfg.MAPPING if cfg.MAPPING in (1, 2) else 1
            bg_raw = get_contextual_mapping_background(mapping)
            sw, sh = screen.get_size()
            key = (mapping, sw, sh)
            if key not in _MAPPING_BG_CACHE:
                _MAPPING_BG_CACHE[key] = pygame.transform.smoothscale(bg_raw, (sw, sh))
            return _MAPPING_BG_CACHE[key]

        def _draw_base(phase_name):
            screen_rect = screen.get_rect()
            if phase_name == "fixation":
                contextual_fixation_rect = CONTEXTUAL_FIXATION.get_rect(center=screen_rect.center)
                screen.fill(BLACK_RGB)
                screen.blit(CONTEXTUAL_FIXATION, contextual_fixation_rect)
            elif phase_name == "stimulus":
                screen.blit(_get_scaled_mapping_bg(), (0, 0))
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
                if trial_type == "no_go":
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
                if trial_type == "no_go":
                    error_type = "catch_delay_error"
                else:
                    error_type = "delay_error"
                correct = 0
                feedback_correct = False
                reaction_time = 0

            _activate_feedback(now_tick)

        def _run_phase(phase_name, duration_ms):
            nonlocal screen
            phase_start_tick = pygame.time.get_ticks()
            phase_end_tick = phase_start_tick + duration_ms

            event_handler = _reset_phase_input()
            phase_input_armed = _arm_phase_input(event_handler, timeout_ms=1000)

            while pygame.time.get_ticks() < phase_end_tick:
                state = event_handler.poll()
                now_tick = pygame.time.get_ticks()

                if state.quit:
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

                _draw_base(phase_name)
                if feedback_active and now_tick < feedback_deadline_tick:
                    draw_feedback_overlay(screen, feedback_correct, feedback_timeout)
                pygame.display.flip()
                pygame.time.delay(1)

        _run_phase("fixation", fixation_time)
        _run_phase("stimulus", response_time)
        _run_phase("isi", isi_time)

        if not response_recorded:
            if trial_type == "no_go":
                correct = 1
                error_type = None
            else:
                correct = 0
                error_type = "no_response"
                reaction_time = 0

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
            "type": trial_type,
            "fixation_time": fixation_time,
            "condition": "contextual",
            "is_catch": (trial_type == "no_go"),
            "difficulty": abs(fixation_time - C_AVG_FIXATION_TIME),
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

        SaveResultsToCsv("results.csv", GetParticipantId(), partResult, startTime, endTime)

        results.append(partResult)
        total_trials += 1
        if correct:
            correct_count += 1

    accuracy = correct_count / total_trials
    return results, accuracy
