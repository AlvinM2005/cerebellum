# ./src/utils/paths.py
"""
Path management module.

This module defines and centralizes all filesystem paths used throughout the application.
It also provides loader helpers for a single-mapping setup.
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
    Load instruction pages for a single mapping.

    :return: Ordered list of instruction image paths
    :rtype: list[pathlib.Path]
    """
    return [INSTRUCTIONS_DIR / f"{i+1}.png" for i in range(cfg.INSTRUCTION_COUNT)]


# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"


def load_stimuli() -> dict[str, Path]:
    """
    Load stimulus paths.

    Mapping rule:
    - MAPPING == 1: default mapping.
    - MAPPING == 2: swap CORRECT/INCORRECT for experimental blocks P1-P9.
      Practice blocks remain unchanged.

    :return: Mapping from stimulus key to file path
    :rtype: dict[str, pathlib.Path]
    """
    stimuli = {
        "PRACTICE1_CORRECT": STIMULI_DIR / "ied_circle_big.png",
        "PRACTICE1_INCORRECT": STIMULI_DIR / "ied_circle_little.png",
        "PRACTICE2_CORRECT": STIMULI_DIR / "ied_circle_little.png",
        "PRACTICE2_INCORRECT": STIMULI_DIR / "ied_circle_big.png",

        "P1_CORRECT": STIMULI_DIR / "ied_s1.png",
        "P1_INCORRECT": STIMULI_DIR / "ied_s2.png",
        "P2_CORRECT": STIMULI_DIR / "ied_s2.png",
        "P2_INCORRECT": STIMULI_DIR / "ied_s1.png",

        "P3_CORRECT": STIMULI_DIR / "ied_s2.png",
        "P3_INCORRECT": STIMULI_DIR / "ied_s1.png",
        "P3_BUFFER1": STIMULI_DIR / "ied_l1.png",
        "P3_BUFFER2": STIMULI_DIR / "ied_l2.png",

        "P4_CORRECT": STIMULI_DIR / "ied_s2.png",
        "P4_INCORRECT": STIMULI_DIR / "ied_s1.png",
        "P4_BUFFER1": STIMULI_DIR / "ied_l1.png",
        "P4_BUFFER2": STIMULI_DIR / "ied_l2.png",

        "P5_CORRECT": STIMULI_DIR / "ied_s1.png",
        "P5_INCORRECT": STIMULI_DIR / "ied_s2.png",
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

    if cfg.MAPPING == 2:
        for phase in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"):
            correct_key = f"{phase}_CORRECT"
            incorrect_key = f"{phase}_INCORRECT"
            stimuli[correct_key], stimuli[incorrect_key] = stimuli[incorrect_key], stimuli[correct_key]

    return stimuli


# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "feedback_correct.png"
FB_INCORRECT = FEEDBACK_DIR / "feedback_incorrect.png"


# ---------- Load Admin ----------

ADMIN_DIR = RESOURCES_DIR / "admin"

ADMIN_1 = ADMIN_DIR / "Admin_1.png"
ADMIN_2 = ADMIN_DIR / "Admin_2.png"
ADMIN_L = ADMIN_DIR / "Admin_L.png"
ADMIN_R = ADMIN_DIR / "Admin_R.png"
ADMIN_LL = ADMIN_DIR / "Admin_LL.png"
ADMIN_LR = ADMIN_DIR / "Admin_LR.png"
ADMIN_RL = ADMIN_DIR / "Admin_RL.png"
ADMIN_RR = ADMIN_DIR / "Admin_RR.png"
ADMIN_PLEASE_L = ADMIN_DIR / "Admin_Please_L.png"
ADMIN_PLEASE_R = ADMIN_DIR / "Admin_Please_R.png"
ADMIN_PLEASE_RL = ADMIN_DIR / "Admin_Please_RL.png"

ADMIN_LAN         = ADMIN_DIR / "Admin_Lan.png"
ADMIN_LAN_SPANISH = ADMIN_DIR / "Admin_Lan_Español.png"
ADMIN_LAN_ENGLISH = ADMIN_DIR / "Admin_Lan_English.png"
ADMIN_GRP         = ADMIN_DIR / "Admin_Grp.png"
ADMIN_GRP_1       = ADMIN_DIR / "Admin_Grp1.png"
ADMIN_GRP_2       = ADMIN_DIR / "Admin_Grp2.png"
ADMIN_GRP_3       = ADMIN_DIR / "Admin_Grp3.png"
ADMIN_GRP_4       = ADMIN_DIR / "Admin_Grp4.png"
ADMIN_GRP_5       = ADMIN_DIR / "Admin_Grp5.png"
ADMIN_GRP_6       = ADMIN_DIR / "Admin_Grp6.png"
ADMIN_SESSION     = ADMIN_DIR / "Admin_Session.png"
ADMIN_SESSION_1   = ADMIN_DIR / "Admin_Session1.png"
ADMIN_SESSION_2   = ADMIN_DIR / "Admin_Session2.png"
ADMIN_SESSION_3   = ADMIN_DIR / "Admin_Session3.png"
ADMIN_SESSION_4   = ADMIN_DIR / "Admin_Session4.png"
ADMIN_SESSION_5   = ADMIN_DIR / "Admin_Session5.png"
ADMIN_SESSION_6   = ADMIN_DIR / "Admin_Session6.png"
ADMIN_SESSION_7   = ADMIN_DIR / "Admin_Session7.png"
ADMIN_SESSION_8   = ADMIN_DIR / "Admin_Session8.png"
ADMIN_SESSION_9   = ADMIN_DIR / "Admin_Session9.png"
