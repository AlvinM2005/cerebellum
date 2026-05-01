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


# ---------- Load Instrucrtions ----------

# Load general instruction pages
INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"
INSTRUCTIONS = []
for i in range(cfg.INSTRUCTIONS_COUNT):
    INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

# Load special instruction page(s)
PRACTICE_INSTRUCTIONS = INSTRUCTIONS_DIR / "practice.png"
TEST_INSTRUCTIONS = INSTRUCTIONS_DIR / "test.png"

# TODO: Load additional instructions configurations if necessary


# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"

STIMULI = []
for i in range(cfg.STIMULI_COUNT):
    STIMULI.append(STIMULI_DIR / f"{i+1}.png")

# TODO: Load additional stimuli configurations if necessary

# ---------- Load Feedback ----------

FB_CORRECT = RESOURCES_DIR / "feedback" / "correct.png"
FB_INCORRECT = RESOURCES_DIR / "feedback" / "incorrect.png"
