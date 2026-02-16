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

def _instruction_root(version: int | None = None) -> Path:
    if version is None:
        version = cfg.VERSION
    assert version in [1, 2]  # ensure version is set to 1 or 2
    return INSTRUCTIONS_DIR if version == 1 else INSTRUCTIONS_REVERSED_DIR


def load_instructions(task: str, count: int, version: int | None = None) -> list[Path]:
    """
    Return instruction asset paths for a given task based on the configured version.
    """
    root = _instruction_root(version)
    task_dir = root / task
    return [task_dir / f"{i}.jpg" for i in range(1, count + 1)]


def instruction_page(task: str, filename: str, version: int | None = None) -> Path:
    """
    Return a specific instruction image path for a task (e.g. p1.jpg, p2.jpg).
    """
    root = _instruction_root(version)
    return root / task / filename



# ---------- Load Stimuli (single version) ----------

def load_stimuli(version: int | None = None) -> dict[str, Path]:
    """
    Return sensorimotor stimulus asset paths based on the configured version.
    """
    if version is None:
        version = cfg.VERSION
    assert version in [1, 2]  # ensure version is set to 1 or 2

    sm_dir = STIMULI_DIR / ("sensorimotor_v1" if version == 1 else "sensorimotor_v2")
    return {
        "fixation": sm_dir / "circle_fixation.jpg",
        "blue": sm_dir / "circle_blue.jpg",
        "red": sm_dir / "circle_red.jpg",
        "white": sm_dir / "circle_white.jpg",
    }


# ---------- Load Stimuli (multiple versions) ----------

# def load_stimuli() -> tuple[list[Path], ...]:
#     """Return stimulus asset paths based on the configured version."""
#     assert cfg.VERSION in [1, 2]    # ensure cfg.VERSION is set to 1 or 2

#     # Select stimulus directory based on cfg.VERSION
#     if cfg.VERSION == 1:
#         STIMULI_DIR = RESOURCES_DIR / "stimuli_v1"
#     else:   # cfg.VERSION == 2
#         STIMULI_DIR = RESOURCES_DIR / "stimuli_v2"

#     STIMULI = []
#     for i in range(cfg.STIMULI_COUNT):
#         STIMULI.append(STIMULI_DIR / f"{i+1}.png")


#     return STIMULI



# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "feedback_correct.png"
FB_INCORRECT = FEEDBACK_DIR / "feedback_incorrect.png"

BEEP = FEEDBACK_DIR / "beep.wav"

