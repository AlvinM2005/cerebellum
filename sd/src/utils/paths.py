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
    
    return [instructions_dir / f"{i+1}.PNG" for i in range(cfg.INSTRUCTIONS_COUNT)]

def get_sd_mapping(mapping: int = None) -> Path:
    """Get SD mapping image path based on mapping version."""
    if mapping is None:
        mapping = cfg.MAPPING
    if mapping == 1:
        return RESOURCES_DIR / "mapping" / "SD_Mapping_1.png"
    return RESOURCES_DIR / "mapping" / "SD_Mapping_2.png"

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

# ---------- Font ----------

FONT = RESOURCES_DIR / "OpenSans.ttf"