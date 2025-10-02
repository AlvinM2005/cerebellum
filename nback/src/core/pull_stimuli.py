# ./src/core/pull_stimuli.py
"""
Select a sequence of stimuli file paths for presentation.

Rules:
- Stimuli live in ./resources/stimuli/ as attneave_1.png ... attneave_{STIMULI_COUNT}.png.
- All public builders return List[Path] with length == trial_num, elements are absolute Paths.
- 0-back (pull_stimuli_0back):
    - Requires a fixed target in cfg.ANSWER0 (Path). If None, pick one at random and persist.
    - For each trial, sample MATCH with 25% probability (the target), otherwise sample uniformly from all others.
- 1-back (pull_stimuli_1back):
    - Seed the first stimulus randomly.
    - From the 2nd trial onward: with 25% probability repeat the previous stimulus (MATCH),
      otherwise sample uniformly from all others (DIFFERENT).
    - cfg.ANSWER1 is updated each trial to the most recently shown Path (the current “target” to compare against).
- 2-back (pull_stimuli_2back):
    - Seed the first two stimuli randomly.
    - From the 3rd trial onward: with 25% probability repeat the item shown 2 trials ago,
      otherwise sample uniformly from all others.
    - cfg.ANSWER2 tracks the current 2-back target (Path) and updates each trial.
- 3-back (pull_stimuli_3back):
    - Seed the first three stimuli randomly.
    - From the 4th trial onward: with 25% probability repeat the item shown 3 trials ago,
      otherwise sample uniformly from all others.
    - cfg.ANSWER3 tracks the current 3-back target (Path) and updates each trial.
- Decision helper: _match_or_different() returns 1 (MATCH) with p=0.25, else 0 (DIFFERENT).
- Logging: INFO when (re)setting targets; DEBUG for each trial’s decision and chosen file name.
"""


from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import random

import utils.config as cfg
from utils.logger import get_logger
from utils.enums import Answer


logger = get_logger("./src/core/pull_stimuli")  # Create logger


def _all_stimuli_paths() -> list[Path]:
    """Return the list of all available stimuli paths (length = STIMULI_COUNT)."""
    base = cfg.RESOURCES_DIR / "stimuli"
    paths = [base / f"attneave_{i}.png" for i in range(1, cfg.STIMULI_COUNT + 1)]
    missing = [p for p in paths if not p.exists()]
    if missing:
        logger.error(f"Missing stimuli files: {', '.join(str(m) for m in missing)}")
        raise FileNotFoundError(f"Missing stimuli files: {', '.join(str(m) for m in missing)}")
    return paths


def _pick_0back_target_path() -> Path:
    """Randomly pick a stimulus as target for 0-back"""
    all_paths = _all_stimuli_paths()
    path  = random.choice(all_paths)
    cfg.ANSWER0 = path
    logger.info(f"ANSWER0 set to: {path.name}")
    return path


def _match_or_different() -> int:
    """
    Decide whether the next stimulus should match the target (25% match, 75% different).
    Returns:
        1 for match
        0 for different
    """
    dice = random.random()
    if dice <= 0.25:
        decision = 1
        logger.debug(f"Dice == {dice}, stimulus matches the target")
    else:
        decision = 0
        logger.debug(f"Dice == {dice}, stimulus is different from the target")
    return decision


def pull_stimuli_0back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Build the final sequence of stimuli paths to present for 0-back tasks"
    Args:
        trial_num: how many trials to prepare
    Returns:
        List[Path]: length == trial_num; each element is a file path to show in order.
    """
    
    all_paths = _all_stimuli_paths()
    trial_flow = []
    answers = []

    # Make sure there is a target selected
    if cfg.ANSWER0 is None:
        logger.warning(f"Target for 0-back not successfully saved; randomly selected a new target")
        _pick_0back_target_path()
    
    # Generate stimuli paths list
    while trial_num > 0:
        decision = _match_or_different()
        if decision == 0:
            candidates = [p for p in all_paths if p != cfg.ANSWER0]
            path = random.choice(candidates)
            logger.debug(f"A DIFFERENT stimulus {path.name} is selected")
            answers.append(Answer.DIFFERENT)
            logger.debug(f"Answer for the current trial is {answers[-1]}")
        else:
            path = cfg.ANSWER0
            logger.debug(f"A SAME stimulus {path.name} is selected")
            answers.append(Answer.SAME)
            logger.debug(f"Answers for the current trial is {answers[-1]}")
        trial_flow.append(path)
        trial_num -= 1

    return (trial_flow, answers)


def pull_stimuli_1back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Build the final sequence of stimuli paths to present for 1-back tasks"
    Args:
        trial_num: how many trials to prepare
    Returns:
        List[Path]: length == trial_num; each element is a file path to show in order.
    """
    all_paths = _all_stimuli_paths()
    answers = []

    # Randomly select the 1st stimulus and set it as the target
    stimulus1 = random.choice(all_paths)
    trial_flow = [stimulus1]
    cfg.ANSWER1 = stimulus1
    logger.debug(f"ANSWER1 set to: {stimulus1.name}")
    answers.append(Answer.NOGO)
    trial_num -= 1
    
    # Generate stimuli paths list
    while trial_num > 0:
        decision = _match_or_different()
        if decision == 0:
            candidates = [p for p in all_paths if p != cfg.ANSWER1]
            path = random.choice(candidates)
            logger.debug(f"A DIFFERENT stimulus {path.name} is selected")
            answers.append(Answer.DIFFERENT)
        else:
            path = cfg.ANSWER1
            logger.debug(f"A MATCH stimulus {path.name} is selected")
            answers.append(Answer.SAME)
        trial_flow.append(path)
        # Update target
        cfg.ANSWER1 = path
        logger.debug(f"ANSWER1 updated to: {path.name}")
        trial_num -= 1

    return (trial_flow, answers)


def pull_stimuli_2back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Build the final sequence of stimuli paths to present for 1-back tasks"
    Args:
        trial_num: how many trials to prepare
    Returns:
        List[Path]: length == trial_num; each element is a file path to show in order.
    """
    all_paths = _all_stimuli_paths()
    target_pointer = 0
    answers = []

    # Randomly select the 1st stimulus and set it as the target
    stimulus1 = random.choice(all_paths)
    trial_flow = [stimulus1]
    cfg.ANSWER2 = stimulus1
    logger.debug(f"ANSWER2 set to: {stimulus1.name}")
    answers.append(Answer.NOGO)
    trial_num -= 1

    # Randomly select the 2nd stimulus
    stimulus2 = random.choice(all_paths)
    trial_flow.append(stimulus2)
    logger.debug(f"A RANDOM stimulus {stimulus2.name} is selected")
    answers.append(Answer.NOGO)
    trial_num -= 1
    
    # Generate stimuli paths list
    while trial_num > 0:
        decision = _match_or_different()
        if decision == 0:
            candidates = [p for p in all_paths if p != cfg.ANSWER2]
            path = random.choice(candidates)
            logger.debug(f"A DIFFERENT stimulus {path.name} is selected")
            answers.append(Answer.DIFFERENT)
        else:
            path = cfg.ANSWER2
            logger.debug(f"A MATCH stimulus {path.name} is selected")
            answers.append(Answer.SAME)
        trial_flow.append(path)
        # Update target
        target_pointer += 1
        target = trial_flow[target_pointer]
        cfg.ANSWER2 = target
        logger.debug(f"ANSWER2 updated to: {target.name}")
        trial_num -= 1

    return (trial_flow, answers)


def pull_stimuli_3back(trial_num: int) -> Tuple[List[Path], List[Answer]]:
    """
    Build the final sequence of stimuli paths to present for 1-back tasks"
    Args:
        trial_num: how many trials to prepare
    Returns:
        List[Path]: length == trial_num; each element is a file path to show in order.
    """
    all_paths = _all_stimuli_paths()
    target_pointer = 0
    answers = []

    # Randomly select the 1st stimulus and set it as the target
    stimulus1 = random.choice(all_paths)
    trial_flow = [stimulus1]
    cfg.ANSWER3 = stimulus1
    logger.debug(f"ANSWER3 set to: {stimulus1.name}")
    answers.append(Answer.NOGO)
    trial_num -= 1

    # Randomly select the 2nd and 3rd stimulus
    stimulus2 = random.choice(all_paths)
    trial_flow.append(stimulus2)
    logger.debug(f"A RANDOM stimulus {stimulus2.name} is selected")
    answers.append(Answer.NOGO)
    stimulus3 = random.choice(all_paths)
    trial_flow.append(stimulus3)
    logger.debug(f"A RANDOM stimulus {stimulus3.name} is selected")
    answers.append(Answer.NOGO)
    trial_num -= 2
    
    # Generate stimuli paths list
    while trial_num > 0:
        decision = _match_or_different()
        if decision == 0:
            candidates = [p for p in all_paths if p != cfg.ANSWER3]
            path = random.choice(candidates)
            logger.debug(f"A DIFFERENT stimulus {path.name} is selected")
            answers.append(Answer.DIFFERENT)
        else:
            path = cfg.ANSWER3
            logger.debug(f"A MATCH stimulus {path.name} is selected")
            answers.append(Answer.SAME)
        trial_flow.append(path)
        # Update target
        target_pointer += 1
        target = trial_flow[target_pointer]
        cfg.ANSWER3 = target
        logger.debug(f"ANSWER2 updated to: {target.name}")
        trial_num -= 1

    return (trial_flow, answers)


# ---------- Tests ----------
# print(_all_stimuli_paths())
# print(_match_or_different())
# print(pull_stimuli_0back(5))
# print(len(pull_stimuli_0back(20)))
# print(pull_stimuli_1back(5))
# print(len(pull_stimuli_1back(20)))
# print(len(pull_stimuli_2back(5)))
# print(len(pull_stimuli_2back(20)))
# print(pull_stimuli_3back(5))
# print(len(pull_stimuli_3back(20)))