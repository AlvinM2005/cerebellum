# ./src/utils/paths.py
"""
Centralized filesystem path definitions for experiment resources and outputs.
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



# # ---------- Load Instructions (single mapping) ----------

# INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"
# INSTRUCTIONS = []
# for i in range(cfg.INSTRUCTIONS_COUNT):
#     INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

# PRACTICE_INSTRUCTION = INSTRUCTIONS_DIR / "practice.png"
# TEST_INSTRUCTION = INSTRUCTIONS_DIR / "test.png"


# ---------- Load Instructions (multiple mappings) ----------

def load_instructions() -> tuple[list[Path], ...]:
    """
    Return instruction asset paths based on the configured mapping.
    """
    assert cfg.MAPPING in [1, 2]    # ensure cfg.MAPPING is set to 1 or 2

    # Select instruction directory based on cfg.MAPPING
    if cfg.MAPPING == 1:
        INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions_v1"
    else:   # cfg.MAPPING == 2
        INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions_v2"
    
    INSTRUCTIONS = []
    for i in range(cfg.INSTRUCTIONS_COUNT):
        INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

    PRACTICE_INSTRUCTION = INSTRUCTIONS_DIR / "practice.png"
    TEST_INSTRUCTION = INSTRUCTIONS_DIR / "test.png"


    return INSTRUCTIONS, PRACTICE_INSTRUCTION, TEST_INSTRUCTION



# ---------- Load Stimuli (single mapping) ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"

STIMULI = []
for i in range(cfg.STIMULI_COUNT):
    STIMULI.append(STIMULI_DIR / f"{i+1}.png")


# ---------- Load Stimuli (multiple mappings) ----------

# def load_stimuli() -> tuple[list[Path], ...]:
#     """Return stimulus asset paths based on the configured mapping."""
#     assert cfg.MAPPING in [1, 2]    # ensure cfg.MAPPING is set to 1 or 2

#     # Select stimulus directory based on cfg.MAPPING
#     if cfg.MAPPING == 1:
#         STIMULI_DIR = RESOURCES_DIR / "stimuli_v1"
#     else:   # cfg.MAPPING == 2
#         STIMULI_DIR = RESOURCES_DIR / "stimuli_v2"

#     STIMULI = []
#     for i in range(cfg.STIMULI_COUNT):
#         STIMULI.append(STIMULI_DIR / f"{i+1}.png")


#     return STIMULI



# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "correct.png"
FB_INCORRECT = FEEDBACK_DIR / "incorrect.png"

BEEP = FEEDBACK_DIR / "beep.wav"


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

