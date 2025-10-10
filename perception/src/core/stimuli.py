"""
PEST implementation for duration discrimination task.
Uses absolute difference from standard as the difficulty metric.
"""

from __future__ import annotations
from pathlib import Path
from typing import List
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


logger = get_logger("./src/core/pull_stimuli")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STIMULUS_PATH_1000 = os.path.join(SCRIPT_DIR, "..", "..", "resources", "stimuli", "tapping_task_tone_1000Hz_50ms_0.25amp.wav")

# PEST PARAMETERS DURATION
STANDARD_INTERVAL = 0.400    # 400ms - fixed standard interval
STEP_START_DIFF = 0.160      # 160ms - starting difference (easy)
INITIAL_STEP_SIZE = 0.040    # 40ms - first step change magnitude
MAX_DIFFERENCE = 0.600       # 240ms - maximum difference
MIN_DIFFERENCE = 0.008       # 8ms - minimum difference (hardest)
# PEST PARAMETERS LOUDNESS
L_STANDARD_AMP = 0.500         # 0.5 amplitude - fixed standard amp
L_STEP_START_DIFF = 0.160      # 160ms - starting difference (easy)
L_INITIAL_STEP_SIZE = 0.040    # 40ms - first step change magnitude
L_MAX_DIFFERENCE = 1           # 240ms - maximum difference
L_MIN_DIFFERENCE = 0.01667       # 8ms - minimum difference (hardest)
L_NUM_LVLS = 60
# SHARED PARAMETERS
TARGET_ACCURACY = 0.90       # 90% target performance
DEVIATION_LIMIT = 1.5        # trials deviation tolerance


# PEST Algorithm (NEEDS FIXING)
class PESTState:
    """Tracks PEST algorithm state - adjusts DIFFERENCE from standard."""
    
    def __init__(self, start_diff: float, initial_step: float, 
                 target_acc: float, dev_limit: float,
                 min_diff: float, max_diff: float,
                 standard: float):
        self.standard_interval = standard
        self.current_difference = start_diff  # Absolute difference from standard
        self.target_accuracy = target_acc
        self.deviation_limit = dev_limit
        self.min_difference = min_diff
        self.max_difference = max_diff
        
        # Step tracking
        self.step_history = []
        self.step_count = 0
        
        # Direction tracking for DIFFERENCE (1 = increase diff/easier, -1 = decrease diff/harder)
        self.current_direction = 1  # Start by making it easier if needed
        self.previous_direction = None
        
        # Step size tracking
        self.current_step_size = abs(initial_step)
        self.previous_step_size = None
        self.steps_in_current_direction = 0
        self.previous_reversal_was_doubling = False
        
    def get_comparison_interval(self) -> float:
        """
        Get the actual comparison interval to present.
        Randomly choose longer or shorter than standard by current_difference.
        """
        if random.random() < 0.5:
            return self.standard_interval + self.current_difference  # Longer
        else:
            return self.standard_interval - self.current_difference  # Shorter
        
    def add_trial_result(self, correct: bool):
        """Add trial result to current step."""
        self.step_history.append(1 if correct else 0)
        
    def should_change_level(self) -> tuple[bool, str, str]:
        """
        Check if difficulty should change based on performance.
        Returns (should_change, reason).
        """
        n_trials = len(self.step_history)
        if n_trials == 0:
            return False, "No trials yet"
            
        n_correct = sum(self.step_history)
        expected_correct = self.target_accuracy * n_trials
        
        lower_bound = expected_correct - self.deviation_limit
        upper_bound = expected_correct + self.deviation_limit
        
        if n_correct > upper_bound:
            return True, "EASY", f"Too easy: {n_correct}/{n_trials} correct (>{upper_bound:.1f})"
        elif n_correct < lower_bound:
            return True, "HARD", f"Too hard: {n_correct}/{n_trials} correct (<{lower_bound:.1f})"
        else:
            return False, "SAME", f"In range: {n_correct}/{n_trials} correct ({lower_bound:.1f}-{upper_bound:.1f})"
    
    def change_level(self):
        """
        Change the difficulty level according to PEST rules.
        Adjusts the DIFFERENCE from standard interval.
        """
        # Determine new direction based on performance
        n_correct = sum(self.step_history)
        n_trials = len(self.step_history)
        accuracy = n_correct / n_trials if n_trials > 0 else 0
        
        # If too easy (high accuracy), make HARDER by DECREASING difference
        # If too hard (low accuracy), make EASIER by INCREASING difference
        if accuracy > self.target_accuracy:
            new_direction = -1  # Decrease difference = harder
        else:
            new_direction = 1   # Increase difference = easier
            
        # Check if we reversed direction
        reversed_direction = (new_direction != self.current_direction)
        
        if reversed_direction:
            self.previous_direction = self.current_direction
            self.current_direction = new_direction
            self.steps_in_current_direction = 0
        
        self.steps_in_current_direction += 1
        
        # Apply PEST rules for step size
        new_step_size = self._calculate_step_size(reversed_direction)
        
        # Apply step change to DIFFERENCE
        diff_change = new_direction * new_step_size
        unclamped_difference = self.current_difference + diff_change
        
        # Enforce valid range
        new_difference = max(self.min_difference, min(self.max_difference, unclamped_difference))
        
        # Check if we hit a boundary
        hit_boundary = (new_difference != unclamped_difference)
        actual_change = new_difference - self.current_difference
        
        if hit_boundary:
            if new_difference == self.max_difference:
                logger.warning(f"  HIT MAX BOUNDARY: Wanted {unclamped_difference*1000:.1f}ms, clamped to {new_difference*1000:.1f}ms")
            else:
                logger.warning(f"  HIT MIN BOUNDARY: Wanted {unclamped_difference*1000:.1f}ms, clamped to {new_difference*1000:.1f}ms")
            logger.warning(f"  Actual change: {actual_change*1000:.1f}ms (intended: {diff_change*1000:.1f}ms)")
            
            # If stuck at boundary with no change, reduce step size to try smaller adjustments
            if abs(actual_change) < 0.001:  # No movement (floating point tolerance)
                logger.warning(f"  STUCK AT BOUNDARY! Cannot move further in this direction.")
                logger.warning(f"  Task may be too easy/hard for participant at boundary limits.")
        
        logger.info(f"PEST: Step {self.step_count} -> {self.step_count+1}")
        logger.info(f"  Accuracy: {accuracy:.2%} ({n_correct}/{n_trials})")
        logger.info(f"  Difference: {self.current_difference*1000:.1f}ms -> {new_difference*1000:.1f}ms")
        logger.info(f"  Comparison range: {(self.standard_interval-new_difference)*1000:.1f}-{(self.standard_interval+new_difference)*1000:.1f}ms")
        logger.info(f"  Step size: {new_step_size*1000:.1f}ms, Direction: {'EASIER' if new_direction > 0 else 'HARDER'}")
        logger.info(f"  Steps in direction: {self.steps_in_current_direction}")
        
        self.current_difference = new_difference
        self.previous_step_size = self.current_step_size
        self.current_step_size = new_step_size
        
        # Reset step history
        self.step_history = []
        self.step_count += 1
        
    def _calculate_step_size(self, reversed_direction: bool) -> float:
        """
        Calculate step size.
        
        Rules:
        1. First step after reversal: halve the step size
        2. Second step in direction: same step size
        3. Third step: double if no prior doubling before reversal, else same
        4. Fourth+ step: always double
        
        On the very first step of the experiment (before any reversal), use the initial step size as-is.
        """
        step_num = self.steps_in_current_direction
        
        if step_num == 1:
            if reversed_direction:
                # Rule 1: First step after reversal - half
                new_size = self.current_step_size / 2.0
                self.previous_reversal_was_doubling = False
                logger.debug(f"  Rule 1: Halving step size to {new_size*1000:.1f}ms")
            else:
                # Very first step of experiment - use current size
                new_size = self.current_step_size
                logger.debug(f"  First step: Using initial step size {new_size*1000:.1f}ms")
            
        elif step_num == 2:
            # Rule 2: Second step - same size
            new_size = self.current_step_size
            logger.debug(f"  Rule 2: Same step size {new_size*1000:.1f}ms")
            
        elif step_num == 3:
            # Rule 3: Third step - double unless prior doubling
            if self.previous_reversal_was_doubling:
                new_size = self.current_step_size
                logger.debug(f"  Rule 3: No doubling (prior doubling) {new_size*1000:.1f}ms")
            else:
                new_size = self.current_step_size * 2.0
                self.previous_reversal_was_doubling = True
                logger.debug(f"  Rule 3: Doubling to {new_size*1000:.1f}ms")
                
        else:  # step_num >= 4
            # Rule 4: Fourth+ step - always double
            new_size = self.current_step_size * 2.0
            self.previous_reversal_was_doubling = True
            logger.debug(f"  Rule 4: Doubling to {new_size*1000:.1f}ms")
        
        return new_size

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
    Run duration discrimination task with PEST adaptive procedure.
    """
    time.sleep(1)

    # Initialize PEST
    pest = PESTState(
        start_diff=STEP_START_DIFF,
        initial_step=INITIAL_STEP_SIZE,
        target_acc=TARGET_ACCURACY,
        dev_limit=DEVIATION_LIMIT,
        min_diff=MIN_DIFFERENCE,
        max_diff=MAX_DIFFERENCE,
        standard=STANDARD_INTERVAL
    )
    
    all_results = []  # Store trial results
    trial_counter = 1

    while trial_counter <= trial_num:
        stimulus = pygame.mixer.Sound(STIMULUS_PATH_1000)
        stimulus.set_volume(0.5)

        logger.info(f"\n--- Trial {trial_counter}/{trial_num} ---")
        
        # Get intervals for current trial
        standard_interval = pest.standard_interval
        comparison_interval = pest.get_comparison_interval()
        
        logger.info(f"Standard: {standard_interval*1000:.1f}ms")
        logger.info(f"Comparison: {comparison_interval*1000:.1f}ms")
        logger.info(f"Difference: {abs(comparison_interval-standard_interval)*1000:.1f}ms")
        
        # First Pair (standard: 400ms)
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 1 (pair 1) played")
        _wait_ms_with_events_capture(standard_interval, screen)
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 2 (pair 1) played - standard interval")
        
        # Inter-pair interval (1000ms)
        time.sleep(1.0)
        
        # Second Pair (comparison: varies)
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 3 (pair 2) played")
        _wait_ms_with_events_capture(comparison_interval, screen)
        stimulus.play()
        logger.info(f"Trial {trial_counter} Sound 4 (pair 2) played - comparison interval")
        
        # Get user response
        correct, correct_answer, participant_ans, timeRec = evaluateResponse(
            standard_interval, 
            comparison_interval, 
            trial_counter, 
            screen, 
            block=block_name,
        )
            
        # Record result
        all_results.append({
            'trial': trial_counter,
            'step': pest.step_count,
            'standard': standard_interval,
            'comparison': comparison_interval,
            'difference': abs(comparison_interval - standard_interval),
            'correct': correct
        })
        
        # Update PEST state
        pest.add_trial_result(correct)
        
        # Check if level should change
        should_change, logReason, reason = pest.should_change_level()
        logger.info(f"PEST check: {reason}")
        
        if should_change:
            pest.change_level()

        saves.update_save(participant_id=pid, block=block_name, condition="duration", difficulty=logReason, key_correct=correct_answer.value, key_response=participant_ans.value, 
                          iv=f"{comparison_interval:.2f} ms", response_time=f"{timeRec:.2f} ms", start_time=start_time)
        screen.fill(cfg.GRAY_RGB)
        pygame.display.flip()
        trial_counter += 1
    
    # Log final results
    logger.info("\n=== Final PEST Results ===")
    logger.info(f"Total trials: {len(all_results)}")
    logger.info(f"Total steps: {pest.step_count}")
    logger.info(f"Final difference threshold: {pest.current_difference*1000:.1f}ms")
    logger.info(f"Final comparison range: {(pest.standard_interval-pest.current_difference)*1000:.1f}-{(pest.standard_interval+pest.current_difference)*1000:.1f}ms")
    
    overall_accuracy = sum(r['correct'] for r in all_results) / len(all_results) if all_results else 0
    logger.info(f"Overall accuracy: {overall_accuracy:.2%}")

    return all_results

def loudnessTask_stimuli(trial_num, block_name, pid, screen, start_time):
    """
    Run duration discrimination task with PEST adaptive procedure.
    """
    time.sleep(1)

    # Initialize PEST
    pest = PESTState(
        start_diff=L_STEP_START_DIFF,
        initial_step=L_INITIAL_STEP_SIZE,
        target_acc=TARGET_ACCURACY,
        dev_limit=DEVIATION_LIMIT,
        min_diff=L_MIN_DIFFERENCE,
        max_diff=L_MAX_DIFFERENCE,
        standard=L_STANDARD_AMP
    )
    
    all_results = []  # Store trial results
    trial_counter = 1

    standard_amp = pygame.mixer.Sound(STIMULUS_PATH_1000)
    

    while trial_counter <= trial_num:
        comparison_amp = pygame.mixer.Sound(STIMULUS_PATH_1000)
        comparison_amp_val = pest.get_comparison_interval()

        standard_amp = pygame.mixer.Sound(STIMULUS_PATH_1000)
        standard_amp_val = pest.standard_interval


        logger.info(f"\n--- Trial {trial_counter}/{trial_num} ---")
        
        # Get intervals for current trial
        standard_amp.set_volume(standard_amp_val)
        comparison_amp.set_volume(comparison_amp_val)
        x = pest.get_comparison_interval()
        
        logger.info(f"Standard: {standard_amp_val} amp")
        logger.info(f"Comparison: {comparison_amp_val:.1f} amp")
        logger.info(f"Difference: {abs(standard_amp_val-comparison_amp_val):.1f} amp")
        
        # First Pair (standard: __ dbA)
        standard_amp.play()
        logger.info(f"Trial {trial_counter} Sound 1 (pair 1) played")
        _wait_ms_with_events_capture(STANDARD_INTERVAL, screen)
        standard_amp.play()
        logger.info(f"Trial {trial_counter} Sound 2 (pair 1) played")
        
        # Inter-pair interval (1000ms)
        time.sleep(1.0)
        
        # Second Pair (comparison: varies)
        comparison_amp.play()
        logger.info(f"Trial {trial_counter} Sound 3 (pair 2) played - comparison interval")
        _wait_ms_with_events_capture(STANDARD_INTERVAL, screen)
        comparison_amp.play()
        logger.info(f"Trial {trial_counter} Sound 4 (pair 2) played - comparison interval")
        
        # Get user response
        correct, correct_answer, participant_ans, timeRec = evaluateResponse(
            standard_amp_val, 
            comparison_amp_val, 
            trial_counter, 
            screen, 
            block=block_name,
        )
            
        # Record result
        all_results.append({
            'trial': trial_counter,
            'step': pest.step_count,
            'standard': standard_amp_val,
            'comparison': comparison_amp_val,
            'difference': abs(comparison_amp_val - standard_amp_val),
            'correct': correct
        })
        
        # Update PEST state
        pest.add_trial_result(correct)
        
        # Check if level should change
        should_change, logReason, reason = pest.should_change_level()
        logger.info(f"PEST check: {reason}")
        
        if should_change:
            pest.change_level()

        saves.update_save(participant_id=pid, block=block_name, condition="loudness", difficulty=logReason, key_correct=correct_answer.value, key_response=participant_ans.value, 
                          iv=f"{comparison_amp_val:.2f} amps", response_time=f"{timeRec:.2f}ms", start_time=start_time)
        screen.fill(cfg.GRAY_RGB)
        pygame.display.flip()
        trial_counter += 1
    
    # Log final results
    logger.info("\n=== Final PEST Results ===")
    logger.info(f"Total trials: {len(all_results)}")
    logger.info(f"Total steps: {pest.step_count}")
    logger.info(f"Final difference threshold: {pest.current_difference*1000:.1f}ms")
    logger.info(f"Final comparison range: {(pest.standard_interval-pest.current_difference)*1000:.1f}-{(pest.standard_interval+pest.current_difference)*1000:.1f}ms")
    
    overall_accuracy = sum(r['correct'] for r in all_results) / len(all_results) if all_results else 0
    logger.info(f"Overall accuracy: {overall_accuracy:.2%}")

    return all_results

def evaluateResponse(standard, comparison, trial_num, screen, block):
    """
    Get user key response and evaluate correctness.
    
    The second pair (comparison) is either shorter or longer than first pair (standard).
    User presses D or K to indicate which interval was longer.
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
        correct_answer = Answer.LONGER_LOUDER  # Second pair was longer
    else:
        correct_answer = Answer.SHORTER_QUIETER  # Second pair was shorter
    
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
