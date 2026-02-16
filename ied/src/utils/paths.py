# ./src/utils/paths.py
"""
Path management module.

This module defines and centralizes all filesystem paths used throughout the application.
It also provides loader helpers for a single-version setup.
"""

from __future__ import annotations

from pathlib import Path

import utils.config as cfg


# ---------- Directories ----------

# project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# resources
RESOURCES_DIR = PROJECT_ROOT / "resources"

# results
RESULTS_DIR = PROJECT_ROOT / "results"

# logs
LOGS_DIR = PROJECT_ROOT / "logs"


# ---------- Load Instructions ----------

INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"


def load_instructions() -> list[Path]:
    """
    Load instruction pages for a single version.

    :return: Ordered list of instruction image paths
    :rtype: list[pathlib.Path]
    """
    return [INSTRUCTIONS_DIR / f"{i+1}.png" for i in range(cfg.INSTRUCTION_COUNT)]


# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"


def load_stimuli() -> dict[str, Path]:
    """
    Load stimulus paths for a single version (no VERSION grouping).

    :return: Mapping from stimulus key to file path
    :rtype: dict[str, pathlib.Path]
    """
    return {
        "PRACTICE1_CORRECT": STIMULI_DIR / "ied_circle_big.png",
        "PRACTICE1_INCORRECT": STIMULI_DIR / "ied_circle_little.png",
        "PRACTICE2_CORRECT": STIMULI_DIR / "ied_circle_little.png",
        "PRACTICE2_INCORRECT": STIMULI_DIR / "ied_circle_big.png",

        "P1_CORRECT": STIMULI_DIR / "ied_s1.png",
        "P1_INCORRECT": STIMULI_DIR / "ied_s2.png",
        "P2_CORRECT": STIMULI_DIR / "ied_s2.png",
        "P2_INCORRECT": STIMULI_DIR / "ied_s1.png",

        "P3_CORRECT": STIMULI_DIR / "ied_s1.png",
        "P3_INCORRECT": STIMULI_DIR / "ied_s2.png",
        "P3_BUFFER1": STIMULI_DIR / "ied_l1.png",
        "P3_BUFFER2": STIMULI_DIR / "ied_l2.png",

        "P4_CORRECT": STIMULI_DIR / "ied_s1.png",
        "P4_INCORRECT": STIMULI_DIR / "ied_s2.png",
        "P4_BUFFER1": STIMULI_DIR / "ied_l1.png",
        "P4_BUFFER2": STIMULI_DIR / "ied_l2.png",

        "P5_CORRECT": STIMULI_DIR / "ied_s2.png",
        "P5_INCORRECT": STIMULI_DIR / "ied_s1.png",
        "P5_BUFFER1": STIMULI_DIR / "ied_l1.png",
        "P5_BUFFER2": STIMULI_DIR / "ied_l2.png",

        "P6_CORRECT": STIMULI_DIR / "ied_s3.png",
        "P6_INCORRECT": STIMULI_DIR / "ied_s4.png",
        "P6_BUFFER1": STIMULI_DIR / "ied_l3.png",
        "P6_BUFFER2": STIMULI_DIR / "ied_l4.png",

        "P7_CORRECT": STIMULI_DIR / "ied_s4.png",
        "P7_INCORRECT": STIMULI_DIR / "ied_s3.png",
        "P7_BUFFER1": STIMULI_DIR / "ied_l3.png",
        "P7_BUFFER2": STIMULI_DIR / "ied_l4.png",

        "P8_CORRECT": STIMULI_DIR / "ied_l5.png",
        "P8_INCORRECT": STIMULI_DIR / "ied_l6.png",
        "P8_BUFFER1": STIMULI_DIR / "ied_s5.png",
        "P8_BUFFER2": STIMULI_DIR / "ied_s6.png",

        "P9_CORRECT": STIMULI_DIR / "ied_l6.png",
        "P9_INCORRECT": STIMULI_DIR / "ied_l5.png",
        "P9_BUFFER1": STIMULI_DIR / "ied_s5.png",
        "P9_BUFFER2": STIMULI_DIR / "ied_s6.png",
    }


# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "feedback_correct.png"
FB_INCORRECT = FEEDBACK_DIR / "feedback_incorrect.png"
