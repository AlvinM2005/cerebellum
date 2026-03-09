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


def load_instructions(count: int, mapping: int | None = None) -> list[Path]:
    """
    Return instruction asset paths from the unified instructions directory.
    """
    root = _instruction_root(mapping)
    return [root / f"{i}.png" for i in range(1, count + 1)]



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
