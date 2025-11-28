"""
BEST PEST implementation for duration and loudness discrimination tasks.
Uses Maximum Likelihood Estimation to track psychometric function parameters,
with an adaptive sampling strategy targeting the upper and lower thresholds (90% accuracy)
Same.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
from scipy.optimize import minimize
import random
import os
import pygame
import time
import numpy as np 
from ui.main_window import *

import utils.config as cfg
import utils.feedback as fb
from utils.logger import get_logger
from utils.enums import *
import utils.saves as saves


logger = get_logger("./src/core/pull_stimuli")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STIMULUS_PATH_1000 = os.path.join(SCRIPT_DIR, "..", "..", "resources", "stimuli", "tapping_task_tone_1000Hz_50ms_0.25amp.wav")

# BEST PEST PARAMETERS FOR DURATION TASK
STANDARD_INTERVAL = 0.400    # 400ms - fixed standard interval (PSE center)
MIN_INTERVAL_MS = 160.0      # 160ms - minimum interval (lower bound)
MAX_INTERVAL_MS = 640.0      # 640ms - maximum interval (upper bound)  
STEP_SIZE_MS = 8.0           # 8ms - discrete step size (resolution)
RANGE_STEPS = int(round((MAX_INTERVAL_MS - MIN_INTERVAL_MS) / STEP_SIZE_MS)) + 1  # 61 steps
TARGET_STD_MULTIPLIER = 1.5  # 1.5 * sigma = 90% threshold for T_U and T_I

# BEST PEST PARAMETERS FOR LOUDNESS TASK
L_STANDARD_AMP = 0.500         # 0.5 amplitude - fixed standard amplitude
L_MIN_AMPLITUDE = 0.001       # 0.001 amplitude - minimum amplitude
L_MAX_AMPLITUDE = 1.0          # 1.0 amplitude - maximum amplitude
L_STEP_SIZE = 0.01667          # discrete step size for amplitude
L_RANGE_STEPS = int(round((L_MAX_AMPLITUDE - L_MIN_AMPLITUDE) / L_STEP_SIZE)) + 1  # 61 steps

# SHARED PARAMETERS
TARGET_ACCURACY = 0.90       # 90% target performance


# BEST PEST Algorithm - Maximum Likelihood Estimation
class PESTState:
    """
    Tracks BEST PEST algorithm state using Maximum Likelihood Estimation.
    Estimates psychometric function parameters to find stimulus levels.
    """
    
    def __init__(self, min_val: float, max_val: float, step_size: float, standard: float,
                 target_acc: float, task_type: str, initial_std_slope_factor: float = 5.0):
        
        self.standard_interval = standard
        self.min_val = min_val
        self.max_val = max_val
        self.step_size = step_size
        self.range_steps = int(round((max_val - min_val) / step_size)) + 1
        self.target_accuracy = target_acc
        self.task_type = task_type  # 'DURATION' or 'LOUDNESS'

        # MLE arrays for log-probability calculations
        self.stimulus_levels = np.linspace(min_val, max_val, self.range_steps)
        self.prob = np.zeros(self.range_steps, dtype=np.float64)  # log-likelihood array
        self.stimulus_history = []  # stores (stimulus_level, response) pairs
        self.step_count = 0
        
        # Initialize threshold tracking fields
        center_index = self.range_steps // 2 
        # MLE estimate tracks the PSE (50% point)
        self.current_mle_estimate = self.stimulus_levels[center_index] 
        self.current_mle_estimate_index = center_index
        self.current_sigma_estimate = (max_val - min_val) / initial_std_slope_factor # Initial guess for sigma
        self.target_std_multi = TARGET_STD_MULTIPLIER
        self.target_upper = True # Controls the alternating sampling strategy
        self.threshold_list = np.append(np.ones(25), np.zeros(25))
        random.shuffle(self.threshold_list)

        
        # Build log-likelihood lookup tables
        self._precalculate_log_likelihood(initial_std_slope_factor)
        
    def _precalculate_log_likelihood(self, slope_factor: float):
        """
        Calculate PLGIT and MLGIT (log-probabilities for correct/incorrect responses)
        for all possible PSE positions using logistic psychometric function.
        """
        # Steepness parameter based on range discretization
        std_scale = self.range_steps / slope_factor 
        
        # Logit distances from center (center has L=0)
        L = np.linspace(-self.range_steps / std_scale, self.range_steps / std_scale, self.range_steps)
        
        # Logistic psychometric function: P(positive) = 1.0 / (1.0 + exp(-L))
        P_positive = 1.0 / (1.0 + np.exp(-L))
        
        # Store log-probabilities to avoid repeated calculations
        self.plgit = np.log(P_positive)  # log P(positive response | PSE at center)
        self.mlgit = np.log(1.0 - P_positive)  # log P(negative response | PSE at center)
        
        # Initialize probability array (log-likelihood = 0 means likelihood = 1)
        self.prob = np.zeros(self.range_steps, dtype=np.float64)

    def _get_current_thresholds(self) -> tuple[float, float, float]:
        """
        Estimate T_U, T_I, and sigma from the current PEST state.
        """
        final_pse = self.current_mle_estimate
        
        # Estimate sigma from final probability distribution width (same logic as final calculation)
        half_max = np.max(self.prob) - np.log(2)
        above_half_max = self.prob >= half_max
        
        if np.any(above_half_max) and self.step_count > 5: # Only trust sigma after initial trials
            width_indices = np.where(above_half_max)[0]
            width_steps = width_indices[-1] - width_indices[0] + 1
            estimated_sigma = (width_steps * self.step_size) / 3.0
        else:
            estimated_sigma = self.current_sigma_estimate # Use last updated sigma or initial guess

        threshold_distance = self.target_std_multi * estimated_sigma
        
        t_u = final_pse + threshold_distance  # upper threshold
        t_i = final_pse - threshold_distance  # lower threshold
        
        self.current_sigma_estimate = estimated_sigma # Update sigma for next iteration
        return t_u, t_i, estimated_sigma

    def get_comparison_interval(self) -> float:
        """
        Returns the next stimulus to test based on the adaptive sampling strategy:
        Alternately targets the current estimate of the Upper (T_U) or Lower (T_I) Thresholds.
        
        """
        
        # First, update the T_U and T_I estimates based on the most recent PSE and Sigma
        t_u, t_i, _ = self._get_current_thresholds()
        
        assess = self.threshold_list[0]
        self.threshold_list = np.delete(self.threshold_list, 0)
        
        if assess == 1:
            # Sample the estimated Upper Threshold (T_U) (point where response is 'longer/louder' 90% of time)
            comparison = t_u
            self.target_upper = True
        else:
            # Sample the estimated Lower Threshold (T_I) (point where response is 'shorter/quieter' 90% of time)
            comparison = t_i
            self.target_upper = False
        
        # Round the continuous estimate to the nearest discrete stimulus level
        index = int(np.round((comparison - self.min_val) / self.step_size))
        
        # Keep index within valid range
        index = np.clip(index, 0, self.range_steps - 1)
        
        final_comparison_value = self.stimulus_levels[index]
        
        return final_comparison_value

    def add_trial_result(self, stimulus_value: float, is_longer_response: bool):
        """
        Stores trial result for MLE processing and flips the target for the next trial.
        """
        # Convert response to +1 (longer/louder) or -1 (shorter/quieter) format
        r_response = 1 if is_longer_response else -1
        
        # Store the trial data for MLE update
        self.stimulus_history.append((stimulus_value, r_response))
        
        # Flip the target for the next trial (alternating sampling)
        self.target_upper = not self.target_upper
    
    def _get_log_likelihood_update(self, stimulus_val: float, response: int) -> np.ndarray:
        """
        Calculates log-likelihood update array for a single trial.
        Shifts the canonical psychometric curve to the stimulus position.
        """
        # Distance from *each possible PSE*
        distances = stimulus_val - self.stimulus_levels
        
        # Convert distance to index shifts for the log-likelihood array
        std_scale = self.range_steps / 5.0 # Use the initial_std_slope_factor=5.0
        
        # Get L directly for each PSE candidate
        L_candidates = distances / (self.step_size * std_scale) 
        
        # Recalculate P_positive for the current stimulus value relative to all PSE candidates
        P_positive_candidates = 1.0 / (1.0 + np.exp(-L_candidates))
        
        # Select appropriate log-likelihood array
        if response == 1:  # Positive response (longer/louder)
            # log P(response | PSE candidate)
            log_likelihood_update = np.log(P_positive_candidates)
        else:  # Negative response (shorter/quieter)
            log_likelihood_update = np.log(1.0 - P_positive_candidates)
            
        return log_likelihood_update

    def should_change_level(self) -> tuple[bool, str]:
        """
        BEST PEST updates after every trial.
        """
        return True, f"MLE update: Trial {len(self.stimulus_history)}"
    
    def change_level(self):
        """
        Update MLE estimation and find new PSE estimate.
        Updates the probability distribution and finds the peak.
        """
        if not self.stimulus_history:
            return

        # Process the latest trial result
        stimulus_value, response = self.stimulus_history[-1]
        
        # Update log-likelihood array
        log_likelihood_update = self._get_log_likelihood_update(stimulus_value, response)
        self.prob += log_likelihood_update
        
        # Find maximum likelihood estimate (peak of probability distribution)
        max_log_likelihood = np.max(self.prob)
        peak_indices = np.where(self.prob == max_log_likelihood)[0]
        
        # Get new MLE estimate as center of peak region
        p1 = peak_indices[0]  # first index of peak
        p2 = peak_indices[-1]  # last index of peak
        new_mle_index = int(np.round((p1 + p2) / 2))
        
        # Convert index back to stimulus value
        new_mle_estimate = self.stimulus_levels[new_mle_index]
        
        # Update PEST state
        self.current_mle_estimate = new_mle_estimate
        self.current_mle_estimate_index = new_mle_index
        self.step_count += 1

        #self._adapt_threshold_multiplier()
        
        logger.info(f"BEST PEST: Trial {self.step_count} -> MLE Update")
        logger.info(f"  Max Log-Likelihood: {max_log_likelihood:.2f}")
        logger.info(f"  New PSE Estimate: {new_mle_estimate*1000:.1f}ms (Index {new_mle_index})")
        
        # Clear trial history for next update
        self.stimulus_history = []

    def get_final_thresholds(self, target_std_multi: float = TARGET_STD_MULTIPLIER) -> tuple[float, float, float]:
        """
        Calculate final thresholds (T_U, T_I) and sigma from MLE estimate.
        """
        # Final PSE estimate from MLE
        final_pse = self.current_mle_estimate
        
        # Estimate sigma from final probability distribution width
        # Find width of probability distribution at half-maximum
        half_max = np.max(self.prob) - np.log(2)  # half-maximum in log space
        above_half_max = self.prob >= half_max
        
        if np.any(above_half_max):
            width_indices = np.where(above_half_max)[0]
            width_steps = width_indices[-1] - width_indices[0] + 1
            # Convert to stimulus units
            estimated_sigma = (width_steps * self.step_size) / 3.0
        else:
            # Use initial estimate
            estimated_sigma = self.current_sigma_estimate
        
        # Thresholds at target_std_multi * sigma from PSE
        threshold_distance = target_std_multi * estimated_sigma
        
        t_u = final_pse + threshold_distance  # upper threshold
        t_i = final_pse - threshold_distance  # lower threshold
        
        # Keep thresholds within bounds
        t_u = min(t_u, self.max_val)
        t_i = max(t_i, self.min_val)
        
        # Reported sigma (actual distance / multiplier)
        reported_sigma = (t_u - t_i) / (2 * target_std_multi)

        return t_u, t_i, reported_sigma

# Stimuli
def stimuli(trial_count, screen, task_type, block_name, pid, start_time):
    """
    Sort between task types

    0 -> durationTask_sound function
    ELSE (1) -> loudnessTask_sound function
    """
    pygame.event.clear()
    screen.fill(cfg.GRAY_RGB)
    pygame.display.flip()

    if task_type == 0:
       return durationTask_stimuli(trial_count, block_name, pid, screen, start_time)
    else:
        return loudnessTask_stimuli(trial_count, block_name, pid, screen, start_time)

def durationTask_stimuli(trial_num, block_name, pid, screen, start_time):
    """
    Run duration discrimination task with BEST PEST adaptive procedure.
    Uses maximum likelihood estimation for threshold estimation.
    """
    time.sleep(1)

    # Set trial count for threshold estimation using BEST PEST
    total_trials = trial_num
    
    logger.info(f"=== BEST PEST Duration Task (Targeting T_U/T_I) ===")
    logger.info(f"Total trials: {total_trials}")
    logger.info(f"Standard interval: {STANDARD_INTERVAL*1000:.1f}ms")
    logger.info(f"Range: {MIN_INTERVAL_MS:.1f}ms - {MAX_INTERVAL_MS:.1f}ms")

    # Initialize BEST PEST with duration task parameters
    pest = PESTState(
        min_val=MIN_INTERVAL_MS/1000.0,
        max_val=MAX_INTERVAL_MS/1000.0,
        step_size=STEP_SIZE_MS/1000.0,
        standard=STANDARD_INTERVAL,
        target_acc=TARGET_ACCURACY,
        task_type='DURATION'
    )
    
    all_results = []  # Store trial results

    trial_counter = 1

    while trial_counter <= total_trials:
        stimulus = pygame.mixer.Sound(STIMULUS_PATH_1000)
        stimulus.set_volume(0.5)

        logger.info(f"\n--- Trial {trial_counter}/{trial_num} ---")
        
        # Get current MLE estimate (next stimulus to test)
        # This will alternate between the best T_U estimate and the best T_I estimate
        mle_estimate = pest.get_comparison_interval()
        
        # Determine presentation order for 2AFC task
        standard_interval = pest.standard_interval
        
        # Present standard vs. MLE estimate based on initialized random list
        interval_1 = standard_interval
        interval_2 = mle_estimate

        logger.info(f"Standard: {standard_interval*1000:.1f}ms")
        logger.info(f"MLE Target: {mle_estimate*1000:.1f}ms (Targeting {'Upper' if pest.target_upper else 'Lower'} Threshold)")
        #logger.info(f"Presentation order: {'Standard->Target' if comparison_is_second else 'Target->Standard'}")
        
        # First Pair
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 1 (pair 1) played")
        _wait_ms_with_events_capture(interval_1, screen)
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 2 (pair 1) played")
        
        # Inter-pair interval (1000ms)
        time.sleep(1.0)
        
        # Second Pair  
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 3 (pair 2) played")
        _wait_ms_with_events_capture(interval_2, screen)
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 4 (pair 2) played")
        
        # Get user response
        # Standard first, MLE second
        correct, correct_answer, participant_ans, timeRec = evaluateResponse(
            standard_interval,  # first pair
            mle_estimate,      # second pair
            trial_counter, 
            screen, 
            block=block_name,
        )

        # Determine if participant considered MLE stimulus as 'longer' (+1) or 'shorter' (-1)
        # Need to account for presentation order
        participant_said_longer = (participant_ans == Answer.LONGER_LOUDER)
        
        # Standard first, MLE second: if participant said "second longer" → MLE is longer
        mle_perceived_as_longer = participant_said_longer

        
        # Update BEST PEST with trial result - only raw perception matters for MLE
        pest.add_trial_result(mle_estimate, mle_perceived_as_longer)
        
        # Check if level should change (always True for BEST PEST)
        should_change, reason = pest.should_change_level()
        logger.info(f"BEST PEST check: {reason}")
        
        if should_change:
            pest.change_level()  # Perform MLE update

        # Record trial data
        all_results.append({
            'trial': trial_counter,
            'mle_estimate': mle_estimate,
            'standard': standard_interval,
            'comparison': mle_estimate,
            'correct': correct,
            'response': participant_ans.value if participant_ans else None
        })
        # Final thresholds using BEST PEST
        t_u, t_i, reported_sigma = pest.get_final_thresholds(TARGET_STD_MULTIPLIER)

        overall_accuracy = sum(r['correct'] for r in all_results) / len(all_results) if all_results else 0

        saves.update_save(participant_id=pid, block=block_name, condition="duration",
                          key_correct=correct_answer.value, key_response=participant_ans.value, comp = f"{mle_estimate*1000:.2f} ms",
                          pse=f"{pest.current_mle_estimate*1000:.2f} ms", t_u = f"{t_u*1000:.2f} ms", t_i= f"{t_i*1000:.2f} ms", 
                          acuity = f"{reported_sigma*1000:.2f} ms",accuracy=f"{overall_accuracy:.2%}", 
                          response_time=f"{timeRec:.2f} ms", start_time=start_time)
        screen.fill(cfg.GRAY_RGB)
        pygame.display.flip()
        trial_counter += 1
    
    
    logger.info("\n=== Final BEST PEST Results ===")
    logger.info(f"Total trials: {len(all_results)}")
    logger.info(f"Final PSE Estimate (50%): {pest.current_mle_estimate*1000:.1f}ms")
    logger.info(f"Final Upper Threshold (T_U @ 90%): {t_u*1000:.1f}ms")
    logger.info(f"Final Lower Threshold (T_I @ 90%): {t_i*1000:.1f}ms")
    logger.info(f"Perceptual Acuity (Sigma): {reported_sigma*1000:.1f}ms")
    logger.info(f"Overall accuracy: {overall_accuracy:.2%}")

    return all_results

def loudnessTask_stimuli(trial_num, block_name, pid, screen, start_time):
    """
    Run loudness discrimination task with BEST PEST adaptive procedure.
    Uses maximum likelihood estimation for threshold estimation.
    """
    time.sleep(1)

    # Set trial count for threshold estimation using BEST PEST
    total_trials = trial_num
    
    logger.info(f"=== BEST PEST Loudness Task (Targeting T_U/T_I) ===")
    logger.info(f"Total trials: {total_trials}")
    logger.info(f"Standard amplitude: {L_STANDARD_AMP:.3f}")
    logger.info(f"Range: {L_MIN_AMPLITUDE:.3f} - {L_MAX_AMPLITUDE:.3f}")

    # Initialize BEST PEST with loudness task parameters
    pest = PESTState(
        min_val=L_MIN_AMPLITUDE,
        max_val=L_MAX_AMPLITUDE,
        step_size=L_STEP_SIZE,
        standard=L_STANDARD_AMP,
        target_acc=TARGET_ACCURACY,
        task_type='LOUDNESS'
    )
    
    all_results = []  # Store trial results
    trial_counter = 1

    threshold_list = np.append(np.ones(25), np.zeros(25))
    random.shuffle(threshold_list)

    while trial_counter <= total_trials:
        logger.info(f"\n--- Trial {trial_counter}/{trial_num} ---")
        
        # Get current MLE estimate (next amplitude to test)
        # This will alternate between the best T_U estimate and the best T_I estimate
        mle_estimate = pest.get_comparison_interval()
        
        # Create sound objects with different amplitudes
        standard_amp = pygame.mixer.Sound(STIMULUS_PATH_1000)
        comparison_amp = pygame.mixer.Sound(STIMULUS_PATH_1000)
        
        standard_amp_val = pest.standard_interval
        comparison_amp_val = mle_estimate
        
        # Set volumes
        standard_amp.set_volume(standard_amp_val)
        comparison_amp.set_volume(comparison_amp_val)
        
        # Determine presentation order for 2AFC task
        first_sound = standard_amp
        second_sound = comparison_amp
        first_val = standard_amp_val
        second_val = comparison_amp_val

        logger.info(f"Standard: {standard_amp_val:.3f} amp")
        logger.info(f"MLE Target: {comparison_amp_val:.3f} amp (Targeting {'Upper' if pest.target_upper else 'Lower'} Threshold)")
        #logger.info(f"Presentation order: {'Standard->Target' if comparison_is_second else 'Target->Standard'}")
        
        # First Pair
        first_sound.play()
        logger.info(f"Trial {trial_counter} Sound 1 (pair 1) played")
        _wait_ms_with_events_capture(STANDARD_INTERVAL, screen)
        first_sound.play()
        logger.info(f"Trial {trial_counter} Sound 2 (pair 1) played")
        
        # Inter-pair interval (1000ms)
        time.sleep(1.0)
        
        # Second Pair
        second_sound.play()
        logger.info(f"Trial {trial_counter} Sound 3 (pair 2) played")
        _wait_ms_with_events_capture(STANDARD_INTERVAL, screen)
        second_sound.play()
        logger.info(f"Trial {trial_counter} Sound 4 (pair 2) played")
        
        # Get user response
        correct, correct_answer, participant_ans, timeRec = evaluateResponse(
            standard_amp_val,  # first pair
            comparison_amp_val, # second pair
            trial_counter, 
            screen, 
            block=block_name,
        )

            
        # Determine if participant considered MLE stimulus as 'louder' (+1) or 'quieter' (-1)
        # Need to account for presentation order
        participant_said_louder = (participant_ans == Answer.LONGER_LOUDER)
        
       # Standard first, MLE second: if participant said "second louder" → MLE is louder
        mle_perceived_as_louder = participant_said_louder
    
        
        # Update BEST PEST with trial result - only raw perception matters for MLE
        pest.add_trial_result(mle_estimate, mle_perceived_as_louder)
        
        # Check if level should change (always True for BEST PEST)
        should_change, reason = pest.should_change_level()
        logger.info(f"BEST PEST check: {reason}")
        
        if should_change:
            pest.change_level()  # Perform MLE update

        # Record trial data
        all_results.append({
            'trial': trial_counter,
            'mle_estimate': mle_estimate,
            'standard': standard_amp_val,
            'comparison': comparison_amp_val,
            'correct': correct,
            'response': participant_ans.value if participant_ans else None
        })
        t_u, t_i, reported_sigma = pest.get_final_thresholds(TARGET_STD_MULTIPLIER)

        overall_accuracy = sum(r['correct'] for r in all_results) / len(all_results) if all_results else 0

        saves.update_save(participant_id=pid, block=block_name, condition="loudness",
                          key_correct=correct_answer.value, key_response=participant_ans.value, comp = f"{mle_estimate*1000:.2f} amps",
                          pse=f"{pest.current_mle_estimate:.3f} amps", t_u = f"{t_u:.3f} amps", t_i= f"{t_i:.3f} amps", 
                          acuity = f"{reported_sigma:.2f} amps", accuracy=f"{overall_accuracy:.2%}", 
                          response_time=f"{timeRec:.2f} ms", start_time=start_time)
        
        screen.fill(cfg.GRAY_RGB)
        pygame.display.flip()
        trial_counter += 1
    
    # Final thresholds using BEST PEST
    #t_u, t_i, reported_sigma = pest.get_final_thresholds(TARGET_STD_MULTIPLIER)
    
    logger.info("\n=== Final BEST PEST Results ===")
    logger.info(f"Total trials: {len(all_results)}")
    logger.info(f"Final PSE Estimate (50%): {pest.current_mle_estimate:.3f} amp")
    logger.info(f"Final Upper Threshold (T_U @ 90%): {t_u:.3f} amp")
    logger.info(f"Final Lower Threshold (T_I @ 90%): {t_i:.3f} amp")
    logger.info(f"Perceptual Acuity (Sigma): {reported_sigma:.3f} amp")
    logger.info(f"Overall accuracy: {overall_accuracy:.2%}")

    return all_results

def evaluateResponse(standard, comparison, trial_num, screen, block):
    """
    Get user key response and evaluate correctness.
    
    The second pair (comparison) is either shorter/quieter or longer/louder than first pair (standard).
    User presses D or K to indicate which interval was longer/louder.
    """
    interrupted, participant_ans, raw_key, timeRec = _wait_for_response_capture(screen)
    
    if interrupted:
        logger.info(f"Interrupted during response collection at trial {trial_num}.")
        return None, None, None
    
    if participant_ans is None:
        logger.warning("No response received")
        return False, None, None
    
    # Determine correct answer
    if comparison > standard:
        correct_answer = Answer.LONGER_LOUDER  # Second pair was perceived as longer/louder
    else:
        correct_answer = Answer.SHORTER_QUIETER  # Second pair was perceived as shorter/quieter
    
    is_correct = (participant_ans == correct_answer)
    
    logger.info(f"Response: {raw_key} -> {participant_ans.value}")
    logger.info(f"Correct answer: {correct_answer.value}")
    logger.info(f"Result: {'CORRECT' if is_correct else 'INCORRECT'}")
    
    # Show feedback
    if block == "PRACTICE1" or block == "PRACTICE2":
        try:
            fb.show_after_trial(
                screen,
                block_name=block,
                is_practice_only=True,
                participant_ans=1,
                correct=True,
                is_correct=is_correct,
                wait_ms=getattr(cfg, "FEEDBACK_DURATION", getattr(cfg, "FEEDBACK_DURATION_MS", 600)),
            )
        except Exception as e:
            logger.warning(f"Immediate feedback failed: {e}")
    else:
        if cfg.ISI_MS > 0:
            screen.fill(cfg.GRAY_RGB)
            pygame.display.flip()
            if _wait_ms_with_events_wait(cfg.ISI_MS, screen):
                logger.info(f"Interrupted during ISI at trial {trial_num}.")
    return is_correct, participant_ans, correct_answer, timeRec


# Key Responses
def _map_key_to_answer(key: int) -> tuple[Answer | None, str | None]:
    """Map keyboard to Answer based on VERSION."""
    if key == pygame.K_d:
        return ((Answer.SHORTER_QUIETER if cfg.VERSION == 1 else Answer.LONGER_LOUDER), "d")
    if key == pygame.K_k:
        return ((Answer.LONGER_LOUDER if cfg.VERSION == 1 else Answer.SHORTER_QUIETER), "k")
    return (None, None)

def _wait_for_response_capture(screen) -> tuple[bool, Answer | None, str | None]:
    """
    Wait indefinitely for participant response (D or K).
    Returns (interrupt, participant_answer, raw_key).

    """
    start = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("User requested quit during response collection.")
                pygame.quit()
                raise SystemExit
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed: toggling full screen.")
                    try:
                        from ui.main_window import toggle_full_screen
                        screen = toggle_full_screen(screen)
                        screen.fill(cfg.GRAY_RGB)
                        pygame.display.flip()
                    except ImportError:
                        logger.warning("Full Screen not available")
                    
                elif event.key in (pygame.K_q, pygame.K_x):
                    logger.info("User aborted response collection with key (Q/X).")
                    return True, None, None
                
                else:
                    mapped, raw = _map_key_to_answer(event.key)
                    if mapped is not None:
                        logger.info(f"Participant response: '{raw}' -> {mapped.value}")
                        responseTime = pygame.time.get_ticks()-start
                        return False, mapped, raw, responseTime
        
        pygame.time.delay(5)

def _wait_ms_with_events_capture(ms: float, screen) -> tuple[bool, Answer | None, str | None]:
    """
    Function for duration stimulus, no capturing inputs d/k, but plays sound
    """
    start = pygame.time.get_ticks()
    waiting_ms = int(ms*1000)
    participant_ans: Answer | None = None
    raw_key: str | None = None

    while pygame.time.get_ticks() - start < waiting_ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("User requested quit during stimulus presentation.")
                pygame.quit()
                raise SystemExit
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed: toggling full screen.")
                    try:
                        from ui.main_window import toggle_full_screen
                        screen = toggle_full_screen(screen)
                        screen.fill(cfg.GRAY_RGB)
                        pygame.display.flip()
                    except ImportError:
                        logger.warning("Full Screen not available")
                    
                elif event.key in (pygame.K_q, pygame.K_x):
                    logger.info("User aborted stimulus presentation.")
                    pygame.quit()
                    raise SystemExit
                
                # Ignore D and K keys during stimulus presentation
                elif event.key in (pygame.K_d, pygame.K_k):
                    logger.debug(f"Ignoring {pygame.key.name(event.key)} during stimulus presentation")
                    continue
            
        #pygame.time.delay(10)

    return False, participant_ans, raw_key

def _handle_events_only_interrupt(screen) -> bool:
    """
    Handle events without capturing answers (used during ISI).
    Returns True if playback should be interrupted (QUIT or Q/X).
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logger.info("User requested quit during ISI.")
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                logger.info("ESC pressed: toggling full screen.")
                toggle_full_screen(screen)
            elif event.key in (pygame.K_q, pygame.K_x):
                logger.info("User aborted stimuli during ISI.")
                return True
    return False

def _wait_ms_with_events_wait(ms: int, screen) -> bool:
    """
    Wait for `ms` ms, keep UI responsive, do not capture D/K, only honor QUIT or Q/X.
    Returns True if interrupted.
    """
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < ms:
        if _handle_events_only_interrupt(screen):
            return True
        pygame.time.delay(5)
    return False