# ./src/core/pull_stimuli.py
"""
Select a sequence of stimuli file paths for presentation.

Rules:
- Stimuli are stored at ./resources/stimuli/ as attneave_1.png ... attneave_12.png
- If trial_num <= STIMULI_COUNT: sample 'trial_num' unique items without replacement.
- If trial_num > STIMULI_COUNT: use a cycling queue:
    fill a queue with all 12 items in a random order; pop one per trial;
    when empty, refill with a fresh shuffled full set. This balances usage over long runs.
"""

from __future__ import annotations
from pathlib import Path
from typing import List
import random

import utils.config as cfg
from utils.logger import get_logger


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
    all_paths = _all_stimuli_paths()
    return random.choice(all_paths)


def _sequence_without_replacement(trial_num: int) -> list[int]:
    """Return indices sampled without replacement and shuffled (for short sequences)."""
    idxs = list(range(cfg.STIMULI_COUNT))  # 0..11
    random.shuffle(idxs)
    return idxs[:trial_num]


def _sequence_with_cycling_queue(trial_num: int) -> list[int]:
    """Return indices using a cycling queue (balanced usage for long sequences)."""
    order: list[int] = []
    queue: list[int] = []
    while len(order) < trial_num:
        if not queue:
            queue = list(range(cfg.STIMULI_COUNT))
            random.shuffle(queue)
        order.append(queue.pop())
    return order


def pull_stimuli(trial_num: int) -> List[Path]:
    """
    Build the final sequence of stimuli paths to present.
    Args:
        trial_num: how many trials to prepare
    Returns:
        List[Path]: length == trial_num; each element is a file path to show in order.
    """
    all_paths = _all_stimuli_paths()
    if trial_num <= cfg.STIMULI_COUNT:
        order = _sequence_without_replacement(trial_num)
    else:
        order = _sequence_with_cycling_queue(trial_num)
    return [all_paths[i] for i in order]
