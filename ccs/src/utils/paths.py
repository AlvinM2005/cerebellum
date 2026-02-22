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

# instructions
INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions_v1"
INSTRUCTIONS_REVERSED_DIR = RESOURCES_DIR / "instructions_v2"

# stimuli
STIMULI_DIR = RESOURCES_DIR / "stimuli"



# # ---------- Load Instructions (single version) ----------

# INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"
# INSTRUCTIONS = []
# for i in range(cfg.INSTRUCTIONS_COUNT):
#     INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

# PRACTICE_INSTRUCTION = INSTRUCTIONS_DIR / "practice.png"
# TEST_INSTRUCTION = INSTRUCTIONS_DIR / "test.png"


# ---------- Load Instructions (multiple versions) ----------

def _instruction_root(mapping: int | None = None) -> Path:
    if mapping is None:
        mapping = cfg.MAPPING
    assert mapping in [1, 2]  # ensure mapping is set to 1 or 2
    return INSTRUCTIONS_DIR if mapping == 1 else INSTRUCTIONS_REVERSED_DIR


def load_instructions(task: str, count: int, mapping: int | None = None) -> list[Path]:
    """
    Return instruction asset paths for a given task based on the configured version.
    """
    root = _instruction_root(mapping)
    task_dir = root / task
    return [task_dir / f"{i}.jpg" for i in range(1, count + 1)]


def instruction_page(task: str, filename: str, mapping: int | None = None) -> Path:
    """
    Return a specific instruction image path for a task (e.g. p1.jpg, p2.jpg).
    """
    root = _instruction_root(mapping)
    return root / task / filename



def load_stimuli(mapping: int | None = None) -> dict[str, Path]:
    """
    Return stimulus asset paths for motor/sensorimotor tasks.
    Mapping image depends on task mapping version (1 or 2).
    """
    if mapping is None:
        mapping = getattr(cfg, "version", None) or cfg.MAPPING
    assert mapping in [1, 2]  # ensure mapping is set to 1 or 2

    return {
        "fixation": STIMULI_DIR / "CCS_Fixation.png",
        "blue": STIMULI_DIR / "CCS_Blue.png",
        "red": STIMULI_DIR / "CCS_Red.png",
        "white": STIMULI_DIR / "CCS_Fixation.png",
        "mapping": STIMULI_DIR / ("CCS_Mapping_1.png" if mapping == 1 else "CCS_Mapping_2.png"),
    }



# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "feedback_correct.png"
FB_INCORRECT = FEEDBACK_DIR / "feedback_incorrect.png"

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
