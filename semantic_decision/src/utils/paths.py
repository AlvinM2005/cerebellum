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

STIMULI_DIR = RESOURCES_DIR / "stimuli"


# ---------- Load Instructions ----------

# Load general instruction pages
def get_instructions(mapping: int = None) -> list[Path]:
    """Load instruction pages based on mapping version."""
    if mapping is None:
        mapping = cfg.MAPPING
    
    if mapping == 1:
        instructions_dir = RESOURCES_DIR / "instructions" / "instructions_v1"
    else:
        instructions_dir = RESOURCES_DIR / "instructions" / "instructions_v2"
    
    return [instructions_dir / f"{i+1}.JPG" for i in range(cfg.INSTRUCTIONS_COUNT)]

def get_sem_mapping(mapping: int = None) -> Path:
    if mapping is None:
        mapping = cfg.MAPPING
    if mapping == 1:
        return RESOURCES_DIR / "instructions" / "SEM_Mapping_1.jpg"
    return RESOURCES_DIR / "instructions" / "SEM_Mapping_2.jpg"

BLOCK1_PG = 14 # speed
BLOCK2_PG = 18 # speed acc
BLOCK3_PG = 23 # speed acc
LAST_PG = 28 # done
# after practice start jpg 14, after speed block start jpg 18, after speed acc start jpg 23, after speed acc start jpg 28 DONE

# ---------- Load Stimuli ----------

SENTENCES_LIST_A = STIMULI_DIR / "SD_listA_sentences.csv"
SENTENCES_LIST_B = STIMULI_DIR / "SD_listB_sentences.csv"

# ---------- Load Feedback ----------

FB_CORRECT = RESOURCES_DIR / "feedback" / "correct.png"
FB_INCORRECT = RESOURCES_DIR / "feedback" / "incorrect.png"

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