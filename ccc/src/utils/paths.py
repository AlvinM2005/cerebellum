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


# ---------- Load Instructions (multiple mappings) ----------

def load_instructions() -> list[Path]:
    """
    Return instruction asset paths based on the configured mapping.
    """
    assert cfg.MAPPING in [1, 2, 3, 4]    # ensure cfg.MAPPING is set to 1..4

    mapping_to_dir = {
        1: "instructions_v11",
        2: "instructions_v21",
        3: "instructions_v12",
        4: "instructions_v22",
    }
    instructions_dir = STIMULI_DIR / mapping_to_dir[cfg.MAPPING]

    # Keep numeric page order: 1.png, 2.png, ..., 41.png
    instruction_pages = sorted(
        instructions_dir.glob("*.png"),
        key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem,
    )
    return instruction_pages



# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"
LETTERS_DIR = STIMULI_DIR / "Letters"

# Fixation Cross
FIXATION_CROSS = STIMULI_DIR / "Fixation_Cross.png"

# a
a_lower_pink = LETTERS_DIR / "a_lower_pink.png"
a_lower_yellow = LETTERS_DIR / "a_lower_yellow.png"
A_upper_pink = LETTERS_DIR / "A_upper_pink.png"
A_upper_yellow = LETTERS_DIR / "A_upper_yellow.png"

# b
b_lower_pink = LETTERS_DIR / "b_lower_pink.png"
b_lower_yellow = LETTERS_DIR / "b_lower_yellow.png"
B_upper_pink = LETTERS_DIR / "B_upper_pink.png"
B_upper_yellow = LETTERS_DIR / "B_upper_yellow.png"

# e
e_lower_pink = LETTERS_DIR / "e_lower_pink.png"
e_lower_yellow = LETTERS_DIR / "e_lower_yellow.png"
E_upper_pink = LETTERS_DIR / "E_upper_pink.png"
E_upper_yellow = LETTERS_DIR / "E_upper_yellow.png"

# g
g_lower_pink = LETTERS_DIR / "g_lower_pink.png"
g_lower_yellow = LETTERS_DIR / "g_lower_yellow.png"
G_upper_pink = LETTERS_DIR / "G_upper_pink.png"
G_upper_yellow = LETTERS_DIR / "G_upper_yellow.png"

# i
i_lower_pink = LETTERS_DIR / "i_lower_pink.png"
i_lower_yellow = LETTERS_DIR / "i_lower_yellow.png"
I_upper_pink = LETTERS_DIR / "I_upper_pink.png"
I_upper_yellow = LETTERS_DIR / "I_upper_yellow.png"

# p
p_lower_pink = LETTERS_DIR / "p_lower_pink.png"
p_lower_yellow = LETTERS_DIR / "p_lower_yellow.png"
P_upper_pink = LETTERS_DIR / "P_upper_pink.png"
P_upper_yellow = LETTERS_DIR / "P_upper_yellow.png"

# r
r_lower_pink = LETTERS_DIR / "r_lower_pink.png"
r_lower_yellow = LETTERS_DIR / "r_lower_yellow.png"
R_upper_pink = LETTERS_DIR / "R_upper_pink.png"
R_upper_yellow = LETTERS_DIR / "R_upper_yellow.png"

# u
u_lower_pink = LETTERS_DIR / "u_lower_pink.png"
u_lower_yellow = LETTERS_DIR / "u_lower_yellow.png"
U_upper_pink = LETTERS_DIR / "U_upper_pink.png"
U_upper_yellow = LETTERS_DIR / "U_upper_yellow.png"


# ---------- Load Mapping ----------

MAPPING_DIR = STIMULI_DIR / "Mapping"

MAPPING_1 = MAPPING_DIR / "CCC_Mapping_1.png"
MAPPING_1_PINK = MAPPING_DIR / "CCC_Mapping_1_Pink.png"
MAPPING_1_YELLOW = MAPPING_DIR / "CCC_Mapping_1_Yellow.png"

MAPPING_2 = MAPPING_DIR / "CCC_Mapping_2.png"
MAPPING_2_PINK = MAPPING_DIR / "CCC_Mapping_2_Pink.png"
MAPPING_2_YELLOW = MAPPING_DIR / "CCC_Mapping_2_Yellow.png"

PHONETIC_TASK_PHASES = {
    "phonetic_task_practice",
    "phonetic_task_experimental",
}
ORTHOGRAPHIC_TASK_PHASES = {
    "orthographic_task_practice",
    "orthographic_task_experimental",
}
MULTI_TASK_PHASES = {
    "multi_task_practice",
    "multi_task_experimental_block_1",
    "multi_task_experimental_block_2",
}


def load_mapping_images() -> tuple[Path, Path, Path]:
    """
    Return (base, pink, yellow) mapping images for current cfg.MAPPING.

    - MAPPING 1/3 -> Mapping 1 assets
    - MAPPING 2/4 -> Mapping 2 assets
    """
    assert cfg.MAPPING in [1, 2, 3, 4]

    if cfg.MAPPING in [1, 3]:
        return MAPPING_1, MAPPING_1_PINK, MAPPING_1_YELLOW
    return MAPPING_2, MAPPING_2_PINK, MAPPING_2_YELLOW


def get_mapping_image_for_task_phase(task_phase: str) -> Path:
    """
    Return the mapping image path by task phase.

    - phonetic phases      -> pink mapping image
    - orthographic phases  -> yellow mapping image
    - multi-task phases    -> base mapping image (no color suffix)
    """
    base_img, pink_img, yellow_img = load_mapping_images()

    if task_phase in PHONETIC_TASK_PHASES:
        return pink_img
    if task_phase in ORTHOGRAPHIC_TASK_PHASES:
        return yellow_img
    if task_phase in MULTI_TASK_PHASES:
        return base_img

    raise ValueError(f"Unsupported task phase: {task_phase}")


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

