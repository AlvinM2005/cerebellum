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


# ---------- Load Instrucrtions ----------

# Load general instruction pages
INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"
INSTRUCTIONS = []
for i in range(cfg.INSTRUCTIONS_COUNT):
    INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.png")

def get_instructions(mapping: int = None) -> list[Path]:
    """Load instruction pages based on mapping version."""
    if mapping is None:
        mapping = cfg.MAPPING
    
    if mapping == 1:
        instructions_dir = RESOURCES_DIR / "instructions" / "instructions_v1"
    else:
        instructions_dir = RESOURCES_DIR / "instructions" / "instructions_v2"
    
    return [instructions_dir / f"{i+1}.PNG" for i in range(cfg.INSTRUCTIONS_COUNT)]

# Load special instruction page(s)
PRACTICE_INSTRUCTIONS = INSTRUCTIONS_DIR / "practice.png"
TEST_INSTRUCTIONS = INSTRUCTIONS_DIR / "stim_instruction.png"

# TODO: Load additional instructions configurations if necessary


# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"

CONTEXTUAL_IMG = STIMULI_DIR / "contextual" / "frames"
BASELINE_IMG = STIMULI_DIR / "baseline" / "frames"

STIMPATHS_CSV_A = STIMULI_DIR / "stimPaths_Context_A.csv"

PRACTICE = STIMULI_DIR / "practice.mp4"

# ---------- Load Feedback ----------

FB_CORRECT = RESOURCES_DIR / "feedback" / "correct.png"
FB_INCORRECT = RESOURCES_DIR / "feedback" / "incorrect.png"

# ---------- Load Admin (dynamic) ----------

# Read and bind all .png files under ADMINH_DIR; variable names
# match filenames (without extension). Example: Admin.png -> Admin
# This supports runtime composition rules (e.g., adding _Next, _1-6, _L/R).

ADMIN_DIR = RESOURCES_DIR / "admin"

def _bind_adminh_images():
    images = {}
    if ADMIN_DIR.exists():
        for path in ADMIN_DIR.glob('*.png'):
            var_name = path.stem  # filename without extension
            globals()[var_name] = path
            images[var_name] = path
    return images

ADMIN_IMAGES = _bind_adminh_images()
