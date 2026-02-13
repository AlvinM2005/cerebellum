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


# ---------- Load Instructions ----------

# Load general instruction pages
if cfg.VERSION == 1:
    INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions" / "instructions_v1"   
else:
    INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions" / "instructions_v1"   
INSTRUCTIONS = []
for i in range(cfg.INSTRUCTIONS_COUNT):
    INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.JPG")

# Load special instruction page(s)
# PRACTICE_INSTRUCTIONS = INSTRUCTIONS_DIR / "practice.png"
# TEST_INSTRUCTIONS = INSTRUCTIONS_DIR / "test.png"

BLOCK1_PG = 14 # speed
BLOCK2_PG = 18 # speed acc
BLOCK3_PG = 23 # speed acc
LAST_PG = 28 # done
# after practice start jpg 14, after speed block start jpg 18, after speed acc start jpg 23, after speed acc start jpg 28 DONE

# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"
SENTENCES_CSV_PRAC = STIMULI_DIR / "semantic_decision_PracticeData.csv"
SENTENCES_CSV_TEST = STIMULI_DIR / "semantic_decision_ExperimentalData.csv"

# ---------- Load Feedback ----------

FB_CORRECT = RESOURCES_DIR / "feedback" / "correct.png"
FB_INCORRECT = RESOURCES_DIR / "feedback" / "incorrect.png"
