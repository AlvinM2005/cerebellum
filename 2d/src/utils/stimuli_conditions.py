"""Stimulus condition tables migrated from CSV files.

This module replaces the legacy CSV condition files with in-code constants.
Only conditions used by the target 4-block design are kept:
- practice
- experimental block A (used by block 1 / block 3)
- experimental block B (used by block 2 / block 4)

All stimulus paths here are filenames under `resources/stimuli`.
Separate demo/short-test image folders are no longer used.

Version-specific key mapping is derived at runtime:
- version 1: normal -> d, mirrored -> k
- version 2: normal -> k, mirrored -> d
"""

from __future__ import annotations

from pathlib import Path


_BASE_COLUMNS = (
    "letter_name",
    "rotation_angle",
    "condition",
    "difficulty",
    "stimuli_path",
)


def _key_for_condition(condition: str, version: int) -> str:
    if version not in (1, 2):
        raise ValueError(f"Unsupported version: {version}")

    if condition not in ("normal", "mirrored"):
        raise ValueError(f"Unsupported condition: {condition}")

    if version == 1:
        return "d" if condition == "normal" else "k"
    return "k" if condition == "normal" else "d"


def _materialize(base_rows: list[tuple], version: int, script_dir: Path | None) -> list[dict]:
    items: list[dict] = []
    for letter_name, rotation_angle, condition, difficulty, stimuli_relpath in base_rows:
        stimuli_path = str((script_dir / stimuli_relpath).resolve()) if script_dir else stimuli_relpath
        items.append(
            {
                "letter_name": letter_name,
                "rotation_angle": rotation_angle,
                "mirrored": condition == "mirrored",
                "condition": condition,
                "difficulty": difficulty,
                "stimuli_path": stimuli_path,
                "key_correct": _key_for_condition(condition, version),
            }
        )
    return items


def get_conditions(phase: str, version: int, script_dir: Path | None = None) -> list[dict]:
    """Return condition rows for a phase and counterbalance version.

    Supported phase labels:
    - practice
    - experimental_block_1 / experimental_block_3 -> block A
    - experimental_block_2 / experimental_block_4 -> block B
    """
    if phase == "practice":
        base = PRACTICE_BASE
    elif phase in ("experimental_block_1", "experimental_block_3"):
        base = EXPERIMENTAL_BLOCK_A_BASE
    elif phase in ("experimental_block_2", "experimental_block_4"):
        base = EXPERIMENTAL_BLOCK_B_BASE
    else:
        raise ValueError(f"Unsupported phase: {phase}")

    return _materialize(base, version, script_dir)


PRACTICE_BASE: list[tuple[str, int, str, int, str]] = [
    ('G', 0, 'normal', 0, 'G_0.png'),
    ('F', -15, 'mirrored', 15, 'F_-15_M.png'),
    ('J', -75, 'mirrored', 75, 'J_-75_M.png'),
    ('J', -105, 'normal', 105, 'J_-105.png'),
    ('J', 105, 'normal', 105, 'J_105.png'),
]

EXPERIMENTAL_BLOCK_A_BASE: list[tuple[str, int, str, int, str]] = [
    ('G', 0, 'normal', 0, 'G_0.png'),
    ('F', -15, 'mirrored', 15, 'F_-15_M.png'),
    ('J', -75, 'mirrored', 75, 'J_-75_M.png'),
    ('J', -105, 'normal', 105, 'J_-105.png'),
    ('J', 105, 'normal', 105, 'J_105.png'),
    ('F', -45, 'normal', 45, 'F_-45.png'),
    ('G', 15, 'mirrored', 15, 'G_15_M.png'),
    ('J', -75, 'normal', 75, 'J_-75.png'),
    ('F', 15, 'mirrored', 15, 'F_15_M.png'),
    ('F', 135, 'normal', 135, 'F_135.png'),
    ('R', -75, 'mirrored', 75, 'R_-75_M.png'),
    ('G', 15, 'normal', 15, 'G_15.png'),
    ('G', -75, 'mirrored', 75, 'G_-75_M.png'),
    ('F', 135, 'mirrored', 135, 'F_135_M.png'),
    ('G', 135, 'normal', 135, 'G_135.png'),
    ('R', 135, 'normal', 135, 'R_135.png'),
    ('J', -135, 'mirrored', 135, 'J_-135_M.png'),
    ('R', 45, 'normal', 45, 'R_45.png'),
    ('J', 45, 'normal', 45, 'J_45.png'),
    ('F', 45, 'normal', 45, 'F_45.png'),
    ('G', -135, 'mirrored', 135, 'G_-135_M.png'),
    ('F', -105, 'mirrored', 105, 'F_-105_M.png'),
    ('R', -45, 'normal', 45, 'R_-45.png'),
    ('R', 15, 'mirrored', 15, 'R_15_M.png'),
    ('J', 75, 'mirrored', 75, 'J_75_M.png'),
    ('G', -45, 'normal', 45, 'G_-45.png'),
    ('J', -15, 'normal', 15, 'J_-15.png'),
    ('G', -15, 'mirrored', 15, 'G_-15_M.png'),
    ('F', 0, 'normal', 0, 'F_0.png'),
    ('G', 75, 'normal', 75, 'G_75.png'),
    ('R', -15, 'mirrored', 15, 'R_-15_M.png'),
    ('G', 75, 'mirrored', 75, 'G_75_M.png'),
    ('F', 75, 'mirrored', 75, 'F_75_M.png'),
    ('R', -105, 'normal', 105, 'R_-105.png'),
    ('J', -15, 'mirrored', 15, 'J_-15_M.png'),
    ('F', 0, 'normal', 0, 'F_0.png'),
    ('F', -75, 'mirrored', 75, 'F_-75_M.png'),
    ('R', -105, 'mirrored', 105, 'R_-105_M.png'),
    ('J', 15, 'mirrored', 15, 'J_15_M.png'),
    ('G', 135, 'mirrored', 135, 'G_135_M.png'),
    ('R', 75, 'mirrored', 75, 'R_75_M.png'),
    ('J', 0, 'mirrored', 0, 'J_0_M.png'),
    ('R', 135, 'mirrored', 135, 'R_135_M.png'),
    ('G', 0, 'normal', 0, 'G_0.png'),
    ('J', 135, 'mirrored', 135, 'J_135_M.png'),
    ('R', 0, 'normal', 0, 'R_0.png'),
    ('F', -105, 'normal', 105, 'F_-105.png'),
    ('G', -105, 'normal', 105, 'G_-105.png'),
]

EXPERIMENTAL_BLOCK_B_BASE: list[tuple[str, int, str, int, str]] = [
    ('F', 0, 'mirrored', 0, 'F_0_M.png'),
    ('R', 15, 'normal', 15, 'R_15.png'),
    ('J', -105, 'mirrored', 105, 'J_-105_M.png'),
    ('J', 15, 'normal', 15, 'J_15.png'),
    ('F', 15, 'normal', 15, 'F_15.png'),
    ('F', 105, 'mirrored', 105, 'F_105_M.png'),
    ('G', -135, 'normal', 135, 'G_-135.png'),
    ('F', -135, 'normal', 135, 'F_-135.png'),
    ('J', 45, 'mirrored', 45, 'J_45_M.png'),
    ('F', -135, 'mirrored', 135, 'F_-135_M.png'),
    ('F', 0, 'mirrored', 0, 'F_0_M.png'),
    ('R', -15, 'normal', 15, 'R_-15.png'),
    ('G', -105, 'mirrored', 105, 'G_-105_M.png'),
    ('G', -15, 'normal', 15, 'G_-15.png'),
    ('R', -135, 'normal', 135, 'R_-135.png'),
    ('J', -45, 'mirrored', 45, 'J_-45_M.png'),
    ('J', 0, 'normal', 0, 'J_0.png'),
    ('F', -15, 'normal', 15, 'F_-15.png'),
    ('J', 0, 'normal', 0, 'J_0.png'),
    ('G', 0, 'mirrored', 0, 'G_0_M.png'),
    ('G', -45, 'mirrored', 45, 'G_-45_M.png'),
    ('R', 0, 'mirrored', 0, 'R_0_M.png'),
    ('G', 45, 'normal', 45, 'G_45.png'),
    ('R', -45, 'mirrored', 45, 'R_-45_M.png'),
    ('J', 0, 'mirrored', 0, 'J_0_M.png'),
    ('R', 105, 'mirrored', 105, 'R_105_M.png'),
    ('R', 45, 'mirrored', 45, 'R_45_M.png'),
    ('G', 105, 'mirrored', 105, 'G_105_M.png'),
    ('R', -75, 'normal', 75, 'R_-75.png'),
    ('G', -75, 'normal', 75, 'G_-75.png'),
    ('G', 0, 'mirrored', 0, 'G_0_M.png'),
    ('G', 105, 'normal', 105, 'G_105.png'),
    ('R', 105, 'normal', 105, 'R_105.png'),
    ('R', 75, 'normal', 75, 'R_75.png'),
    ('J', 105, 'mirrored', 105, 'J_105_M.png'),
    ('J', 75, 'normal', 75, 'J_75.png'),
    ('R', 0, 'mirrored', 0, 'R_0_M.png'),
    ('F', 75, 'normal', 75, 'F_75.png'),
    ('J', -45, 'normal', 45, 'J_-45.png'),
    ('F', 105, 'normal', 105, 'F_105.png'),
    ('R', 0, 'normal', 0, 'R_0.png'),
    ('F', 45, 'mirrored', 45, 'F_45_M.png'),
    ('G', 45, 'mirrored', 45, 'G_45_M.png'),
    ('F', -45, 'mirrored', 45, 'F_-45_M.png'),
    ('R', -135, 'mirrored', 135, 'R_-135_M.png'),
    ('J', -135, 'normal', 135, 'J_-135.png'),
    ('J', 135, 'normal', 135, 'J_135.png'),
    ('F', -75, 'normal', 75, 'F_-75.png'),
]
