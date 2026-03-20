"""Centralized path and loading definitions for the target task."""

from __future__ import annotations

from pathlib import Path

import utils.config as cfg


# ---------- Directories ----------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESOURCES_DIR = PROJECT_ROOT / "resources"
RESULTS_DIR = PROJECT_ROOT / "results"
LOGS_DIR = PROJECT_ROOT / "logs"

# ---------- Instruction Directories ----------

INSTRUCTIONS_V1_DIR = RESOURCES_DIR / "instructions_v1"
INSTRUCTIONS_V2_DIR = RESOURCES_DIR / "instructions_v2"


# ---------- Instruction Page Labels (1-based page index) ----------

TOTAL_INSTRUCTION_PAGES = 28

INTRO_PAGE_1 = 1
INTRO_PAGE_2 = 2
INTRO_PAGE_3 = 3
INTRO_PAGE_4 = 4
INTRO_PAGE_5 = 5
INTRO_PAGE_6 = 6
INTRO_PAGE_7 = 7

PRACTICE_BLOCK_TRIGGER_PAGE = 8
EXPERIMENTAL_BLOCK_1_TRIGGER_PAGE = 12
EXPERIMENTAL_BLOCK_2_TRIGGER_PAGE = 17
EXPERIMENTAL_BLOCK_3_TRIGGER_PAGE = 22
EXPERIMENTAL_BLOCK_4_TRIGGER_PAGE = 27

INTER_BLOCK_1_BREAK_START_PAGE = 13
INTER_BLOCK_2_BREAK_START_PAGE = 18
INTER_BLOCK_3_BREAK_START_PAGE = 23

FINAL_PAGE = 28


# ---------- Load Stimuli (single mapping) ----------

# Single-mapping stimuli root for the target task.
STIMULI_ROOT_DIR = RESOURCES_DIR / "stimuli"


# ---------- Load Mapping Overlay ----------

MAPPING_DIR = RESOURCES_DIR / "mapping"
FIXATION_CROSS_IMAGE = RESOURCES_DIR / "Fixation_Cross.png"


# ---------- Load Instructions ----------

def _instruction_dir_by_mapping(mapping: int) -> Path:
    if mapping == 1:
        return INSTRUCTIONS_V1_DIR
    if mapping == 2:
        return INSTRUCTIONS_V2_DIR
    return INSTRUCTIONS_V1_DIR


def _resolve_instruction_page(mapping: int, page_num: int) -> Path:
    """Resolve one instruction page path from mapping-specific instruction set."""
    page_path = _instruction_dir_by_mapping(mapping) / f"{page_num}.png"
    if page_path.exists():
        return page_path
    raise FileNotFoundError(
        f"Missing instruction page {page_num}.png in mapping-specific directory: "
        f"{_instruction_dir_by_mapping(mapping)}"
    )


def load_instruction_pages() -> dict[int, Path]:
    """Return page_num -> image path for all instruction pages in the task."""
    mapping = cfg.MAPPING if cfg.MAPPING in (1, 2) else 1
    pages: dict[int, Path] = {}
    for page_num in range(1, TOTAL_INSTRUCTION_PAGES + 1):
        pages[page_num] = _resolve_instruction_page(mapping, page_num)
    return pages


def load_stimuli_root() -> Path:
    """Return single-mapping stimuli root path."""
    return STIMULI_ROOT_DIR


def load_mapping_image() -> Path:
    """Return mapping overlay image by current mapping (1 -> 1.png, 2 -> 2.png)."""
    mapping = cfg.MAPPING if cfg.MAPPING in (1, 2) else 1
    mapping_path = MAPPING_DIR / f"{mapping}.png"
    if not mapping_path.exists():
        raise FileNotFoundError(f"Missing mapping image: {mapping_path}")
    return mapping_path


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
