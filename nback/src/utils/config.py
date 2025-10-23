# ./src/utils/config.py
from pathlib import Path
from utils.enums import Answer, Status

# ---------- Directories ----------

# root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# resources
RESOURCES_DIR = BASE_DIR / "resources"

# results
RESULTS_DIR = BASE_DIR / "results"

# logs
LOGS_DIR = BASE_DIR / "logs"


# ---------- Default settings ----------
#MODE = "test"
MODE = "actual"

FEEDBACK_ICON_RATIO = 0.12      # feedback icon size (ratio)
FEEDBACK_ICON_MAX_PX = 160      # feedback icon size (pixel)

# test mode (for testing only)
if MODE == "test":
    MIN_READING_TIME = 100      # minimum reading time per page (ms)
    FEEDBACK_DURATION = 1000    # feedback display duration (ms)

# actual mode
else:
    MIN_READING_TIME = 1000     # minimum reading time per page (ms)
    FEEDBACK_DURATION = 1000    # feedback display duration (ms)


# ---------- Pygame settings ----------

# color
RED_RGB = (255, 72, 72)     # FF4848
BLUE_RGB = (72, 197, 255)   # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0,0,0)         # 000000
GRAY_RGB = (128,128,128)    # 808080
YELLOW_RGB = (255,255,0)    # FFFF00

# screen size
SCREEN_WIDTH = 1516
SCREEN_HEIGHT = 852

# font size
FONT_SIZE = 48


# ---------- Instructions settings ----------
INSTRUCTION_COUNT = 39  # instruction count (adjusted to remove 0-back pages 1-12)

# 1-back (now starts at page 1)
START_PAGE_1BACK = 13    # 1back tasks begins on page ~
PRACTICE1 = 18   # Practice 1 (10 trials for actual) begins after page ~
BLOCK1 = 21      # Block 1 (21 trials for actual begins after page ~
BLOCK2 = 24     # Block 2 (21 trials for actual) begins after page ~

# 2-back
START_PAGE_2BACK = 25   # 2back tasks begins on page ~
PRACTICE2 = 31  # Practice 2 (10 trials for actual) begins after page ~
BLOCK3 = 34     # Block 3 (22 trials for actual) begins after page ~
BLOCK4 = 37     # Block 4 (22 trials for actual) begins after page ~

# 3-back
START_PAGE_3BACK = 38   # 3back tasks begins on page ~
PRACTICE3 = 44  # Practice 3 (10 trials for actual) begins after page ~
BLOCK5 = 47     # Block 5 (23 trials for actual) begins after page ~
BLOCK6 = 50     # Block 6 (23 trials for actual) begins after page ~


# ——---------- Stimuli settings ----------
STIMULI_COUNT = 10              # stimuli count (attneave_1.png to attneave_10.png)

# Deterministic sequence generation parameters
TARGETS_PER_BLOCK = 6           # exact number of targets per block
NON_TARGETS_BASE = 14           # base number of non-targets (14 + n for each level)
MAX_CONSECUTIVE_REPEATS = 3     # maximum allowed consecutive repetitions of same stimulus

# test mode (for testing only)
if MODE == "test":
    STIMULUS_DURATION_MS = 500     # time per stimulus (ms)
    ISI_MS = 2500                    # inter-stimulus interval (ISI) (ms)
    # number of trials for each block
    # PRACTICE1_COUNT, PRACTICE2_COUNT, PRACTICE3_COUNT = (5, 5, 5)
    PRACTICE1_COUNT, PRACTICE2_COUNT, PRACTICE3_COUNT = (10, 10, 10)
    # Block counts follow formula: NON_TARGETS_BASE + TARGETS_PER_BLOCK + n_level
    BLOCK1_COUNT, BLOCK2_COUNT = (10, 10)                              # 1-back blocks
    BLOCK3_COUNT, BLOCK4_COUNT = (22, 22)                              # 2-back blocks (14+6+2)
    BLOCK5_COUNT, BLOCK6_COUNT = (23, 23)                              # 3-back blocks (14+6+3)

# actual mode
else:
    STIMULUS_DURATION_MS = 500     # time per stimulus (ms)
    ISI_MS = 2500                   # inter-stimulus interval (ISI) (ms)
    # number of trials for each block
    PRACTICE1_COUNT, PRACTICE2_COUNT, PRACTICE3_COUNT = (10, 10, 10)
    # Block counts follow formula: NON_TARGETS_BASE + TARGETS_PER_BLOCK + n_level
    BLOCK1_COUNT, BLOCK2_COUNT = (21, 21)                              # 1-back blocks (14+6+1)
    BLOCK3_COUNT, BLOCK4_COUNT = (22, 22)                              # 2-back blocks (14+6+2)
    BLOCK5_COUNT, BLOCK6_COUNT = (23, 23)                              # 3-back blocks (14+6+3)


# ---- Stimulus placement region (normalized coordinates: left, top, width, height) ----
# This defines the blank top-center area in the mapping where the stimuli should be displayed.
STIM_REGION = (0.25, 0.12, 0.50, 0.55)


# ---------- Runtime condition assignment ----------
ANSWER1: str | None = None      # path string to the chosen 1-back target image
ANSWER2: str | None = None      # path string to the chosen 2-back target image
ANSWER3: str | None = None      # path string to the chosen 3-back target image

ANSWER: Answer | None = None               # answer for the current trial
STATUS: Status = Status.NO_RESPONSE     # the current response is correct / incorrect / timeout 
