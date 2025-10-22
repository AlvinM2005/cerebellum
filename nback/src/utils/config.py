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
MODE = "test"
# MODE = "actual"

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
INSTRUCTION_COUNT = 51  # instruction count

# 0-back
START_PAGE_0BACK = 1    # 0back tasks begins on page ~
PRACTICE1 = 6   # Practice 1 (10 trials for actual) begins after page ~
BLOCK1 = 9      # Block 1 (20 trials for actual) begins after page ~
BLOCK2 = 12     # Block 2 (20 trials for actual) begins after page ~

# 1-back
START_PAGE_1BACK = 13   # 1back tasks begins on page ~
PRACTICE2 = 18  # Practice 2 (10 trials for actual) begins after page ~
BLOCK3 = 21     # Block 3 (20 trials for actual begins after page ~
BLOCK4 = 24     # Block 4 (20 trials for actual) begins after page ~

# 2-back
START_PAGE_2BACK = 25   # 2back tasks begins on page ~
PRACTICE3 = 31  # Pracitice 3 (10 trials for actual) begins after page ~
BLOCK5 = 34     # Block 5 (20 trials for actual) begins after page ~
BLOCK6 = 37     # Block 6 (20 trials for actual) begins after page ~

# 3-back
START_PAGE_3BACK = 38   # 3back tasks begins on page ~
PRACTICE4 = 44   # Pracitice 4 (10 trials for actual) begins after page ~
BLOCK7 = 47     # Block 6 (20 trials for actual) begins after page ~
BLOCK8 = 50     # Block 7 (20 trials for actual) begins after page ~


# ——---------- Stimuli settings ----------
STIMULI_COUNT = 12              # stimuli count

# test mode (for testing only)
if MODE == "test":
    STIMULUS_DURATION_MS = 1500     # time per stimulus (ms)
    ISI_MS = 500                    # inter-stimulus interval (ISI) (ms)
    TARGET_DISPLAY = 1000           # 0-back target displayed time (ms)
    # number of trials for each block
    # PRACTICE1_COUNT, PRACTICE2_COUNT, PRACTICE3_COUNT, PRACTICE4_COUNT = (5, 5, 5, 5)
    PRACTICE1_COUNT, PRACTICE2_COUNT, PRACTICE3_COUNT, PRACTICE4_COUNT = (10, 10, 10, 10)
    # BLOCK1_COUNT, BLOCK2_COUNT, BLOCK3_COUNT, BLOCK4_COUNT, BLOCK5_COUNT, BLOCK6_COUNT, BLOCK7_COUNT, BLOCK8_COUNT = (5, 5, 5, 5, 5, 5, 5, 5)
    BLOCK1_COUNT, BLOCK2_COUNT, BLOCK3_COUNT, BLOCK4_COUNT, BLOCK5_COUNT, BLOCK6_COUNT, BLOCK7_COUNT, BLOCK8_COUNT = (10, 10, 10, 10, 10, 10, 10, 10)

# actual mode
else:
    STIMULUS_DURATION_MS = 3000     # time per stimulus (ms)
    ISI_MS = 1000                   # inter-stimulus interval (ISI) (ms)
    TARGET_DISPLAY = 10000          # 0-back target displayed time (ms)
    # number of trials for each block
    PRACTICE1_COUNT, PRACTICE2_COUNT, PRACTICE3_COUNT, PRACTICE4_COUNT = (10, 10, 10, 10)
    BLOCK1_COUNT, BLOCK2_COUNT, BLOCK3_COUNT, BLOCK4_COUNT, BLOCK5_COUNT, BLOCK6_COUNT, BLOCK7_COUNT, BLOCK8_COUNT = (20, 20, 20, 20, 20, 20, 20, 20)


# ---- Stimulus placement region (normalized coordinates: left, top, width, height) ----
# This defines the blank top-center area in the mapping where the stimuli should be displayed.
STIM_REGION = (0.25, 0.12, 0.50, 0.55)


# ---------- Runtime condition assignment ----------
VERSION: int | None = None      # task version (1/2)

ANSWER0: str | None = None      # path string to the chosen 0-back target image
ANSWER1: str | None = None      # path string to the chosen 1-back target image
ANSWER2: str | None = None      # path string to the chosen 2-back target image
ANSWER3: str | None = None      # path string to the chosen 3-back target image

ANSWER: Answer | None = None               # answer for the current trial
STATUS: Status = Status.NO_RESPONSE     # the current response is correct / incorrect / timeout 
