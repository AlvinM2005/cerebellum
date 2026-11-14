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



# ---------- Load Instructions ----------

INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"

# break screen of the mandatory pause (the countdown number is drawn on top by the clamp task)
COUNTDOWN_IMAGE = INSTRUCTIONS_DIR / "count_down.png"

# understanding check screen (answered with the 'a' / 'b' keys, not SPACE)
UNDERSTANDING_CHECK_IMAGE = INSTRUCTIONS_DIR / "understanding_check.png"

def load_instructions() -> dict[int, Path]:
    """
    Return the instruction images keyed by their slide number in the source deck
    (resources/instructions/<n>.png; the numbers are those listed in cfg.INSTRUCTION_PAGES).
    """
    return {n: INSTRUCTIONS_DIR / f"{n}.png" for n in cfg.INSTRUCTION_PAGES}



# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"

FIXATION_CROSS_IMAGE = STIMULI_DIR / "Fixation_Cross.png"

STIMULI = []
for i in range(cfg.STIMULI_COUNT):
    STIMULI.append(STIMULI_DIR / f"{i+1}.png")


# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "correct.png"
FB_INCORRECT = FEEDBACK_DIR / "incorrect.png"

BEEP = FEEDBACK_DIR / "beep.wav"


# ---------- Load Sounds ----------

# "knock" played when the hand crosses the target distance fast enough
# (converted from knock_short_quiet.mat of the original MATLAB task: stereo, 22500 Hz, 58 ms)
KNOCK_SOUND = RESOURCES_DIR / "sounds" / "knock_short_quiet.wav"


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
