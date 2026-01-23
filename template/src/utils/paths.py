# ./src/utils/paths.py
"""
Path management module.

This module defines and centralizes all filesystem paths used throughout the application.
"""


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

# TODO: Add additional paths if necessary


# TODO: Pick one of the load_instructions() functions (SINGLE [line 39-62] / MULTIPLE [line 65-92] versions)

# # ---------- Load Instrucrtions (for task with SINGLE versions) ----------

# def load_instructions() -> tuple[list[Path], ...]:
#     """
#     Load file paths of instruction pages based on the current configuration (VERSION).
#     All instructions page should be in .png form.
    
#     :return: ordered instruction pages, special instruction pages
#     :rtype: tuple[list[Path], ...]
#     """

#     # Load general instruction pages
#     INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"
#     INSTRUCTIONS = []
#     for i in range(cfg.INSTRUCTIONS_COUNT):
#         INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

#     # Load special instruction page(s)
#     PRACTICE = INSTRUCTIONS_DIR / "practice.png"
#     TEST = INSTRUCTIONS_DIR / "test.png"

#     # TODO: Load additional instructions configurations if necessary

#     return INSTRUCTIONS, PRACTICE, TEST

# ---------- Load Instrucrtions (for task with MULTIPLE versions) ----------

def load_instructions() -> tuple[list[Path], ...]:
    """
    Load file paths of instruction pages based on the current configuration (VERSION).
    All instructions page should be in .png form.
    
    :return: ordered instruction pages, special instruction pages
    :rtype: tuple[list[Path], ...]
    """

    # Load general instruction pages
    if cfg.VERSION == 1:
        INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions" / "instructions_v1"
    else:   # cfg.VERSION == 2
        INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions" / "instructions_v2"
    
    INSTRUCTIONS = []
    for i in range(cfg.INSTRUCTIONS_COUNT):
        INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

    # Load special instruction page(s)
    PRACTICE = INSTRUCTIONS_DIR / "practice.png"
    TEST = INSTRUCTIONS_DIR / "test.png"

    # TODO: Load additional instructions configurations if necessary

    return INSTRUCTIONS, PRACTICE, TEST


# TODO: Pick one of the load_stimuli() functions (SINGLE [line 97-116] / MULTIPLE [line 120-145] VERSION)

# # ---------- Load Stimuli (for task with SINGLE versions) ----------

# def load_stimuli() -> tuple[Path, ...]:
#     """
#     Load file paths of stimuli based on the current configuration (VERSION).
#     All stimuli images should be in .png form.
    
#     :return: file paths of stimuli
#     :rtype: tuple[Path, ...]
#     """

#     STIMULI_DIR = RESOURCES_DIR / "stimuli"
    
#     STIMULI = []
#     for i in range(cfg.STIMULI_COUNT):
#         STIMULI.append(STIMULI_DIR / f"{i+1}.png")

#     # TODO: Load additional stimuli configurations if necessary

#     return STIMULI

# ---------- Load Stimuli (for task with MULTIPLE versions) ----------

def load_stimuli() -> tuple[Path, ...]:
    """
    Load file paths of stimuli based on the current configuration (VERSION).
    All stimuli images should be in .png form.
    
    :return: file paths of stimuli
    :rtype: tuple[Path, ...]
    """

    if cfg.VERSION == 1:
        STIMULI_DIR = RESOURCES_DIR / "stimuli" / "stimuli_v1"
    else:   # cfg.VERSION == 2
        STIMULI_DIR = RESOURCES_DIR / "stimuli" / "stimuli_v2"
    
    STIMULI = []
    for i in range(cfg.STIMULI_COUNT):
        STIMULI.append(STIMULI_DIR / f"{i+1}.png")

    # TODO: Load additional stimuli configurations if necessary

    return STIMULI

# ---------- Load Feedback ----------

FB_CORRECT = RESOURCES_DIR / "feedback" / "correct.png"
FB_INCORRECT = RESOURCES_DIR / "feedback" / "incorrect.png"
