"""
Stimulus loading and balancing for the 3D mental-rotation task.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import re

import utils.config as cfg
from utils.logger import get_logger
from utils.paths import RESOURCES_DIR


logger = get_logger("./src/utils/stimuli")

ANGLES = (0, 50, 100, 150)
ANSWERS = ("normal", "mirrored")
STIMULUS_RE = re.compile(r"^(?P<item_id>\d+)_(?P<angle>0|50|100|150)(?P<mirror>_R)?\.jpg$")


@dataclass(frozen=True)
class StimulusTrial:
    """
    Parsed stimulus metadata derived from the image filename.
    """
    condition: str
    stimuli_path: Path
    item_id: int
    rotation_angle: int
    correct_answer: str


def _stimuli_dir() -> Path:
    """
    Return the flat stimulus directory.
    """
    preferred = RESOURCES_DIR / "stimuli"
    if preferred.exists():
        return preferred
    return RESOURCES_DIR / "strimuli"


def _parse_stimulus(path: Path) -> StimulusTrial | None:
    """
    Parse an image filename like 34_150_R.jpg into trial metadata.
    """
    match = STIMULUS_RE.match(path.name)
    if match is None:
        return None

    item_id = int(match.group("item_id"))
    angle = int(match.group("angle"))
    correct_answer = "mirrored" if match.group("mirror") else "normal"
    condition = f"id_{item_id}_rot_{angle}_{correct_answer}"

    return StimulusTrial(
        condition=condition,
        stimuli_path=path,
        item_id=item_id,
        rotation_angle=angle,
        correct_answer=correct_answer,
    )


def _ids_for_block(block: str) -> set[int]:
    """
    Return item IDs for practice/test blocks under the current mode.
    """
    if block == "practice":
        return {13}

    if block == "block1":
        return {1, 2} if cfg.MODE == "demo" else set(range(1, 7))

    if block == "block2":
        return {7, 8} if cfg.MODE == "demo" else set(range(7, 13))

    raise ValueError(f"Unknown stimulus block: {block}")


def _load_for_ids(item_ids: set[int]) -> list[StimulusTrial]:
    """
    Load all parsed stimuli whose item ID is in item_ids.
    """
    stim_dir = _stimuli_dir()
    trials: list[StimulusTrial] = []

    for path in sorted(stim_dir.glob("*.jpg")):
        trial = _parse_stimulus(path)
        if trial is not None and trial.item_id in item_ids:
            trials.append(trial)

    return trials


def _balanced_bucket_order(trials: list[StimulusTrial]) -> list[StimulusTrial]:
    """
    Interleave trials from balanced angle x answer buckets.
    """
    buckets: dict[tuple[int, str], list[StimulusTrial]] = {
        (angle, answer): []
        for angle in ANGLES
        for answer in ANSWERS
    }

    for trial in trials:
        buckets[(trial.rotation_angle, trial.correct_answer)].append(trial)

    bucket_sizes = {key: len(value) for key, value in buckets.items()}
    if len(set(bucket_sizes.values())) != 1:
        raise ValueError(f"Unbalanced stimulus buckets: {bucket_sizes}")

    for bucket in buckets.values():
        random.shuffle(bucket)

    balanced: list[StimulusTrial] = []
    n_rounds = next(iter(bucket_sizes.values()), 0)

    for i in range(n_rounds):
        round_trials = [buckets[key][i] for key in buckets]
        random.shuffle(round_trials)
        balanced.extend(round_trials)

    return balanced


def load_balanced_stimuli(block: str) -> list[StimulusTrial]:
    """
    Load and balance stimuli for practice, block1, or block2.
    """
    item_ids = _ids_for_block(block)
    trials = _load_for_ids(item_ids)
    expected = len(item_ids) * len(ANGLES) * len(ANSWERS)

    if len(trials) != expected:
        logger.warning(
            "Expected %d stimuli for %s IDs %s, found %d",
            expected,
            block,
            sorted(item_ids),
            len(trials),
        )

    return _balanced_bucket_order(trials)


def answer_for_option(option_selected: int | None) -> str | None:
    """
    Convert left/right option selection into normal/mirrored by mapping.
    """
    if option_selected is None:
        return None

    mapping = cfg.MAPPING if cfg.MAPPING in (1, 2) else 1
    if mapping == 1:
        return "normal" if option_selected == 1 else "mirrored"
    return "mirrored" if option_selected == 1 else "normal"


def option_for_answer(answer: str) -> int:
    """
    Convert a correct normal/mirrored answer into left/right option by mapping.
    """
    mapping = cfg.MAPPING if cfg.MAPPING in (1, 2) else 1
    if mapping == 1:
        return 1 if answer == "normal" else 2
    return 1 if answer == "mirrored" else 2
