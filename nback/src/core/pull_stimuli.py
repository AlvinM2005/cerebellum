# ./src/core/pull_stimuli.py
"""
Select a sequence of stimuli file paths for presentation.

Rules:
- Stimuli live in ./resources/stimuli/ as attneave_1.png ... attneave_10.png.
- All public builders return List[Path] with length == trial_num, elements are absolute Paths.
- 1-back (pull_stimuli_1back):
    - Generates deterministic sequences with exactly 6 targets per block.
    - Ensures no more than 3 consecutive repetitions of the same stimulus.
    - Expected trials per block: 21 (14 non-targets + 6 targets + 1 for n-level).
- 2-back (pull_stimuli_2back):
    - Generates deterministic sequences with exactly 6 targets per block.
    - Ensures no more than 3 consecutive repetitions of the same stimulus.
    - Expected trials per block: 22 (14 non-targets + 6 targets + 2 for n-level).
- 3-back (pull_stimuli_3back):
    - Generates deterministic sequences with exactly 6 targets per block.
    - Ensures no more than 3 consecutive repetitions of the same stimulus.
    - Expected trials per block: 23 (14 non-targets + 6 targets + 3 for n-level).
- Logging: INFO when (re)setting targets; DEBUG for each trial's decision and chosen file name.
"""


from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import random

import utils.config as cfg
from utils.logger import get_logger
from utils.enums import Answer


logger = get_logger("./src/core/pull_stimuli")  # Create logger


def _is_practice_block(trial_num: int) -> bool:
    """
    Determine if this is a practice block based on trial count.
    Practice blocks have 10 trials, experimental blocks have 21-23 trials.
    
    Args:
        trial_num: Number of trials in the block
        
    Returns:
        True if this is a practice block, False otherwise
    """
    return trial_num == 10


def _all_stimuli_paths() -> list[Path]:
    """Return the list of all available stimuli paths (length = STIMULI_COUNT)."""
    base = cfg.RESOURCES_DIR / "stimuli"
    paths = [base / f"attneave_{i}.png" for i in range(1, cfg.STIMULI_COUNT + 1)]
    missing = [p for p in paths if not p.exists()]
    if missing:
        logger.error(f"Missing stimuli files: {', '.join(str(m) for m in missing)}")
        raise FileNotFoundError(f"Missing stimuli files: {', '.join(str(m) for m in missing)}")
    return paths


def _create_deterministic_sequence(n_back_level: int, total_trials: int) -> Tuple[List[Path], List[Answer]]:
    """
    Generate deterministic stimulus sequence with exact target count and repetition constraints.
    
    This function creates sequences that have exactly TARGETS_PER_BLOCK targets and ensures
    no stimulus repeats more than MAX_CONSECUTIVE_REPEATS times consecutively.
    
    Args:
        n_back_level: The n-back level (1, 2, or 3)
        total_trials: Total number of trials in the sequence
        
    Returns:
        Tuple containing stimulus paths and corresponding answer sequence
    """
    all_paths = _all_stimuli_paths()
    
    while True:  # Keep generating until valid sequence found
        # Step 1: Generate random sequence using available stimuli (1-10)
        sequence_numbers = [random.randint(1, cfg.STIMULI_COUNT) for _ in range(total_trials)]
        
        # Step 2: Identify targets automatically based on n-back rule
        target_count = 0
        target_positions = []
        
        for pos in range(n_back_level, len(sequence_numbers)):
            if sequence_numbers[pos] == sequence_numbers[pos - n_back_level]:
                target_count += 1
                target_positions.append(pos)
        
        # Step 3: Validate exact target count requirement
        if target_count != cfg.TARGETS_PER_BLOCK:
            continue  # Regenerate if wrong number of targets
            
        # Step 4: Validate consecutive repetition constraint
        has_too_many_repeats = False
        for i in range(len(sequence_numbers) - cfg.MAX_CONSECUTIVE_REPEATS):
            # Check if stimulus repeats more than allowed consecutive times
            consecutive_same = True
            for j in range(1, cfg.MAX_CONSECUTIVE_REPEATS + 1):
                if sequence_numbers[i] != sequence_numbers[i + j]:
                    consecutive_same = False
                    break
            if consecutive_same:
                has_too_many_repeats = True
                break
        
        if has_too_many_repeats:
            continue  # Regenerate if too many consecutive repeats
            
        # Step 5: Valid sequence found - convert to paths and generate answers
        stimulus_paths = [all_paths[num - 1] for num in sequence_numbers]  # Convert 1-based to 0-based indexing
        answers = []
        
        for pos in range(len(sequence_numbers)):
            if pos < n_back_level:
                answers.append(Answer.NOGO)  # First n positions cannot be evaluated
            elif pos in target_positions:
                answers.append(Answer.SAME)   # This is a target (match)
            else:
                answers.append(Answer.DIFFERENT)  # This is a non-target
                
        logger.info(f"Generated deterministic {n_back_level}-back sequence: {target_count} targets in {total_trials} trials")
        return stimulus_paths, answers


def _create_practice_sequence(n_back_level: int, total_trials: int) -> Tuple[List[Path], List[Answer]]:
    """
    Generate deterministic stimulus sequence for practice blocks with 3 targets.
    
    This function creates practice sequences that have exactly 3 targets and ensures
    no stimulus repeats more than MAX_CONSECUTIVE_REPEATS times consecutively.
    
    Args:
        n_back_level: The n-back level (1, 2, or 3)
        total_trials: Total number of trials in the sequence (typically 10)
        
    Returns:
        Tuple containing stimulus paths and corresponding answer sequence
    """
    all_paths = _all_stimuli_paths()
    
    while True:  # Keep generating until valid sequence found
        # Step 1: Generate random sequence using available stimuli (1-10)
        sequence_numbers = [random.randint(1, cfg.STIMULI_COUNT) for _ in range(total_trials)]
        
        # Step 2: Identify targets automatically based on n-back rule
        target_count = 0
        target_positions = []
        
        for pos in range(n_back_level, len(sequence_numbers)):
            if sequence_numbers[pos] == sequence_numbers[pos - n_back_level]:
                target_count += 1
                target_positions.append(pos)
        
        # Step 3: Validate exact target count requirement (3 for practice)
        if target_count != 3:
            continue  # Regenerate if wrong number of targets
            
        # Step 4: Validate consecutive repetition constraint
        has_too_many_repeats = False
        for i in range(len(sequence_numbers) - cfg.MAX_CONSECUTIVE_REPEATS):
            # Check if stimulus repeats more than allowed consecutive times
            consecutive_same = True
            for j in range(1, cfg.MAX_CONSECUTIVE_REPEATS + 1):
                if sequence_numbers[i] != sequence_numbers[i + j]:
                    consecutive_same = False
                    break
            if consecutive_same:
                has_too_many_repeats = True
                break
        
        if has_too_many_repeats:
            continue  # Regenerate if too many consecutive repeats
            
        # Step 5: Valid sequence found - convert to paths and generate answers
        stimulus_paths = [all_paths[num - 1] for num in sequence_numbers]  # Convert 1-based to 0-based indexing
        answers = []
        
        for pos in range(len(sequence_numbers)):
            if pos < n_back_level:
                answers.append(Answer.NOGO)  # First n positions cannot be evaluated
            elif pos in target_positions:
                answers.append(Answer.SAME)   # This is a target (match)
            else:
                answers.append(Answer.DIFFERENT)  # This is a non-target
                
        logger.info(f"Generated practice {n_back_level}-back sequence: {target_count} targets in {total_trials} trials")
        return stimulus_paths, answers


def pull_stimuli_1back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Generate deterministic stimulus sequence for 1-back tasks.
    
    Creates sequences with exactly TARGETS_PER_BLOCK targets for experimental blocks (21 trials)
    or 3 targets for practice blocks (10 trials), and validates that no stimulus repeats 
    more than MAX_CONSECUTIVE_REPEATS times consecutively.
    
    Args:
        trial_num: Number of trials to prepare
        
    Returns:
        Tuple containing stimulus paths and answer sequence
    """
    # Check if this is a practice block
    if _is_practice_block(trial_num):
        logger.info(f"Detected 1-back practice block with {trial_num} trials")
        return _create_practice_sequence(1, trial_num)
    
    # Regular experimental block
    expected_trials = cfg.NON_TARGETS_BASE + cfg.TARGETS_PER_BLOCK + 1  # 14 + 6 + 1 = 21
    
    if trial_num != expected_trials:
        logger.warning(f"1-back expects {expected_trials} trials, got {trial_num}. Using deterministic generation anyway.")
    
    return _create_deterministic_sequence(1, trial_num)


def pull_stimuli_2back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Generate deterministic stimulus sequence for 2-back tasks.
    
    Creates sequences with exactly TARGETS_PER_BLOCK targets for experimental blocks (22 trials)
    or 3 targets for practice blocks (10 trials), and validates that no stimulus repeats 
    more than MAX_CONSECUTIVE_REPEATS times consecutively.
    
    Args:
        trial_num: Number of trials to prepare
        
    Returns:
        Tuple containing stimulus paths and answer sequence
    """
    # Check if this is a practice block
    if _is_practice_block(trial_num):
        logger.info(f"Detected 2-back practice block with {trial_num} trials")
        return _create_practice_sequence(2, trial_num)
    
    # Regular experimental block
    expected_trials = cfg.NON_TARGETS_BASE + cfg.TARGETS_PER_BLOCK + 2  # 14 + 6 + 2 = 22
    
    if trial_num != expected_trials:
        logger.warning(f"2-back expects {expected_trials} trials, got {trial_num}. Using deterministic generation anyway.")
    
    return _create_deterministic_sequence(2, trial_num)


def pull_stimuli_3back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Generate deterministic stimulus sequence for 3-back tasks.
    
    Creates sequences with exactly TARGETS_PER_BLOCK targets for experimental blocks (23 trials)
    or 3 targets for practice blocks (10 trials), and validates that no stimulus repeats 
    more than MAX_CONSECUTIVE_REPEATS times consecutively.
    
    Args:
        trial_num: Number of trials to prepare
        
    Returns:
        Tuple containing stimulus paths and answer sequence
    """
    # Check if this is a practice block
    if _is_practice_block(trial_num):
        logger.info(f"Detected 3-back practice block with {trial_num} trials")
        return _create_practice_sequence(3, trial_num)
    
    # Regular experimental block
    expected_trials = cfg.NON_TARGETS_BASE + cfg.TARGETS_PER_BLOCK + 3  # 14 + 6 + 3 = 23
    
    if trial_num != expected_trials:
        logger.warning(f"3-back expects {expected_trials} trials, got {trial_num}. Using deterministic generation anyway.")
    
    return _create_deterministic_sequence(3, trial_num)


# ---------- Tests ----------
# print(_all_stimuli_paths())
# print(pull_stimuli_1back(5))
# print(len(pull_stimuli_1back(21)))
# print(len(pull_stimuli_2back(22)))
# print(len(pull_stimuli_2back(22)))
# print(pull_stimuli_3back(5))
# print(len(pull_stimuli_3back(23)))