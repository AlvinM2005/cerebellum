# ./src/utils/config.py
from pathlib import Path

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
INSTRUCTION_COUNT = 24  # instruction count

# Main Task - Time Perception
PRACTICE1 = 7   # Practice 1 (10 trials) begins after page ~
BLOCK1 = 11      # Block 1 (50 trials) begins after page ~
#BLOCK2 = 16     # Block 2 (25 trials) begins after page ~

# Control Task - Loudness
PRACTICE2 = 19  # Practice 2 (10 trials) begins after page ~
BLOCK2 = 23     # Block 3 (50 trials) begins after page ~
#BLOCK4 = 33     # Block 4 (25 trials) begins after page ~


# ——---------- Stimuli settings ----------
# STIMULI_COUNT = 12              # stimuli count
# FEEDBACK_ICON_RATIO = 0.12      # feedback icon size (ratio)
# FEEDBACK_ICON_MAX_PX = 160      # feedback icon size (pixel)

# test mode (for testing only)
if MODE == "test":
    STIMULUS_DURATION_MS = ...     # time per stimulus (ms)
    ISI_MS = 500                    # inter-stimulus interval (ISI) (ms)
    TARGET_DISPLAY = 1000           # 0-back target displayed time (ms)
    # number of trials for each block
    PRACTICE1_COUNT, PRACTICE2_COUNT = (10, 10)
    BLOCK1_COUNT, BLOCK2_COUNT = (50, 50)

# actual mode
else:
    STIMULUS_DURATION_MS = ... #inf     # time per stimulus (ms)
    ISI_MS = 1000                   # inter-stimulus interval (ISI) (ms)
    #TARGET_DISPLAY = 10000          # 0-back target displayed time (ms)
    # number of trials for each block
    PRACTICE1_COUNT, PRACTICE2_COUNT = (10, 10)
    BLOCK1_COUNT, BLOCK2_COUNT = (50, 50)

# ---------- Post-response pause (jitter in ms) ----------
# Pausa tras la respuesta del participante antes del siguiente ensayo.
# Se usa un jitter aleatorio entre MIN y MAX para evitar predictibilidad y "efecto de contraste"
# Esta pausa aplica tanto en bloques de práctica como en bloques experimentales.
# Default: 3000-5000 ms (3-5 segundos)
POST_RESPONSE_PAUSE_MIN_MS = 3000
POST_RESPONSE_PAUSE_MAX_MS = 5000


# ---- Stimulus placement region (normalized coordinates: left, top, width, height) ----
# This defines the blank top-center area in the mapping where the stimuli should be displayed.
STIM_REGION = (0.25, 0.12, 0.50, 0.55)
# TARGET_REGION = (0.25, )


# ---------- Runtime condition assignment ----------
VERSION: int | None = None      # task version (1/2)
ANSWER0: str | None = None      # path string to the chosen 0-back target image
