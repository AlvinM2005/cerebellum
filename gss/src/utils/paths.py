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


# ---------- Load Stimuli (letter-coded set) ----------

# Convention in ./resources/stimuli:
# - Word-color: "B/G/R/Y_B/G/R/Y.png" (e.g., B_G.png means BLUE written in GREEN)
# - X-color:    "X_B/G/R/Y.png" (e.g., X_G.png means X written in GREEN)
# - Ignore subfolder: ./resources/stimuli/goal
#
# Auto-generate module-level variables like:
#   BLUE_in_GREEN = PROJECT_ROOT / 'resources/stimuli/B_G.png'
#   X_in_BLUE     = PROJECT_ROOT / 'resources/stimuli/X_B.png'
# Also expose dictionaries for programmatic access:
#   WORD_COLOR_STIMULI[("BLUE", "GREEN")] -> Path(.../B_G.png)
#   X_COLOR_STIMULI["BLUE"]               -> Path(.../X_B.png)

STIMULI_DIR = RESOURCES_DIR / "stimuli"

_COLOR_LETTER_TO_NAME = {
    'B': 'BLUE',
    'G': 'GREEN',
    'R': 'RED',
    'Y': 'YELLOW',
}

def _build_letter_stimuli_maps():
    """Scan current stimuli folder and bind variables/dicts accordingly."""
    word_color = {}
    x_color = {}

    # Word-color pairs
    for path in STIMULI_DIR.glob('[BGRY]_[BGRY].png'):
        stem = path.stem  # e.g., 'B_G'
        try:
            word_letter, color_letter = stem.split('_', 1)
        except ValueError:
            continue
        word_name = _COLOR_LETTER_TO_NAME.get(word_letter)
        color_name = _COLOR_LETTER_TO_NAME.get(color_letter)
        if not word_name or not color_name:
            continue
        var_name = f"{word_name}_in_{color_name}"
        globals()[var_name] = path
        word_color[(word_name, color_name)] = path

    # X-color
    for path in STIMULI_DIR.glob('X_[BGRY].png'):
        stem = path.stem  # e.g., 'X_G'
        parts = stem.split('_', 1)
        if len(parts) != 2:
            continue
        _, color_letter = parts
        color_name = _COLOR_LETTER_TO_NAME.get(color_letter)
        if not color_name:
            continue
        var_name = f"X_in_{color_name}"
        globals()[var_name] = path
        x_color[color_name] = path

    return word_color, x_color

# Build on import
WORD_COLOR_STIMULI, X_COLOR_STIMULI = _build_letter_stimuli_maps()


# ---------- Goal Stimuli ----------

GOAL_DIR = STIMULI_DIR / "goal"

def _bind_goal_stimuli():
    goal = {}
    if GOAL_DIR.exists():
        for path in GOAL_DIR.glob('*.png'):
            var_name = path.stem
            globals()[var_name] = path
            goal[var_name] = path
    return goal

GOAL_STIMULI = _bind_goal_stimuli()
