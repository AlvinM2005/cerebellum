# ./src/utils/config.py
"""
Centralized configuration constants for experiment parameters and runtime state.
"""


# ---------- Default ----------
MODE = "demo"       # quick testing
# MODE = "full"     # real participant runs


# ---------- Pygame UI ----------

# color
RED_RGB = (255, 72, 72)     # #FF4848
BLUE_RGB = (72, 197, 255)   # #48C5FF
WHITE_RGB = (236, 236, 236) # #ECECEC
COCO_RGB = (192, 192, 192)  # #C0C0C0
BLACK_RGB = (0, 0, 0)       # #000000
GRAY_RGB = (128, 128, 128)  # #808080
YELLOW_RGB = (255, 255, 0)  # #FFFF00

# screen size
SCREEN_W = 1280 # screen width (px)
SCREEN_H = 720  # screen height (px)

# font size
FONT_SMALL = 48 # body text (px)
FONT_LARGE = 72 # titles (px)


# ---------- Instructions ----------

INSTRUCTIONS_COUNT = 5

# Task order for the full contextual control protocol.
INSTRUCTION_TASK_ORDER = (
    "phonetic_task_practice",      # 1
    "phonetic_task_experimental",  # 2
    "orthographic_task_practice",  # 3
    "orthographic_task_experimental",    # 4
    "multi_task_practice",         # 5
    "multi_task_experimental_block_1",   # 6
    "multi_task_experimental_block_2",   # 7
)

# Task checkpoint definition:
# each value means "start this task right after X.png".
#
# Mapping-to-instruction-version:
# - MAPPING 1 -> instructions_v11
# - MAPPING 2 -> instructions_v21
# - MAPPING 3 -> instructions_v12
# - MAPPING 4 -> instructions_v22
#
# For v11/v21, task distribution is:
#   8, 11, 20, 23, 34, 37, 40
# For v12/v22, the first four task positions are swapped
#   (task 1/2 <-> task 3/4 positions).
INSTRUCTION_TASK_AFTER_PNG_BY_MAPPING = {
    1: (8, 11, 20, 23, 34, 37, 40),   # instructions_v11
    2: (8, 11, 20, 23, 34, 37, 40),   # instructions_v21
    3: (20, 23, 8, 11, 34, 37, 40),   # instructions_v12 (swapped positions)
    4: (20, 23, 8, 11, 34, 37, 40),   # instructions_v22 (swapped positions)
}

if MODE == "demo":
    MIN_READING_TIME = 100  # minimum time per instruction page before allowing next (ms)
else:   # MODE = "full"
    MIN_READING_TIME = 1000



# ---------- Stimuli ----------

if MODE == "demo":
    MAX_RESPONSE_TIME = 1000    # maximum response time (ms)
    FIXATION_CROSS_TIME = 1000        # fixation cross duration (ms)
else:   # MODE = "full"
    MAX_RESPONSE_TIME = 2000
    FIXATION_CROSS_TIME = 1000



# ---------- Feedback ----------

FB_W = 200  # feedback image width (px)
FB_H = 200  # feedback image height (px)

if MODE == "demo":
    FB_DURATION = 1000   # feedback duration (ms)
else:   # MODE == "full"
    FB_DURATION = 1000



# ---------- Joystick Control ----------

DZ_X = 0.5      # deadzone for x-axis ([0,1])
DZ_Y = 0.5      # deadzone for y-axis ([0,1])

JOY_MODE = 2    # number of discrete joystick directions
# JOY_MODE = 4


# ---------- Runtime State ----------
PID: str | None = None                  # participant ID
MAPPING: int | None = None              # task mapping (1 / 2 / 3 / 4)
DH: str | None = None                   # participant's dominant hand (left / right)
UH: str | None = None                   # hand used during task (left / right)
START_TIME: str | None = None           # task start time (ISO format)
GLOBAL_END_TIME: str | None = None      # task end time (ISO format)

_is_fullscreen: bool = True         # current fullscreen state
_input_source: str | None = None    # response input source (key = keyboard / joy = joystick)
_start_time: str | None = None      # block start time (ISO format)
_end_time: str | None = None        # block end time (ISO format)
key_response: str | None = None     # actual keyboard key pressed
joy_response: str | None = None     # actual joystick direction
