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

if MODE == "demo":
    READ_TIME = 100  # minimum time spent on each instruction page (ms)
else:   # MODE = "full"
    READ_TIME = 1000

LAST_INSTRUCTION_AUTO_EXIT_DEMO_MS = 1000
LAST_INSTRUCTION_AUTO_EXIT_FULL_MS = 10000
if MODE == "demo":
    LAST_INSTRUCTION_AUTO_EXIT_MS = LAST_INSTRUCTION_AUTO_EXIT_DEMO_MS
else:
    LAST_INSTRUCTION_AUTO_EXIT_MS = LAST_INSTRUCTION_AUTO_EXIT_FULL_MS



# ---------- Stimuli ----------

if MODE == "demo":
    MAX_RESPONSE_TIME = 1000    # maximum response time (ms)
    FIXATION_CROSS = 500        # fixation cross duration (ms)
else:   # MODE = "full"
    MAX_RESPONSE_TIME = 3000
    FIXATION_CROSS = 500



# ---------- Feedback ----------

FB_W = 200  # feedback image width (px)
FB_H = 200  # feedback image height (px)
FB_MAX_DURATION = 2000  # max non-blocking feedback overlay duration (ms)

if MODE == "demo":
    FB_DURATION = 500   # feedback duration (ms)
else:   # MODE == "full"
    FB_DURATION = 1000


# ---------- Accuracy & Repeats ----------

ACCURACY = 0.8 # Accuracy required to pass practices
MAX_REPEAT = 3 # Maximum repeated rounds of practice (when called, use MAX_REPEAT - 1)
PRACTICE_REPEAT = 1 # Additional practice rounds after a failed practice check


# ---------- Trial Settings [Contextual] ----------

C_MIN_FIXATION_TIME = 800 # Minimum fixation time [Contextual]
C_MAX_FIXATION_TIME = 1200 # Maximum fixation time [Contextual]
C_AVG_FIXATION_TIME = (C_MIN_FIXATION_TIME + C_MAX_FIXATION_TIME) // 2 # Average fixation time [Contextual]
if MODE == "demo":
    C_RESPONSE_TIME = 2000 # Response time [Contextual]
    C_ISI_TIME = 250 # ISI time [Contextual]
else:
    C_RESPONSE_TIME = 2000 # Response time [Contextual]
    C_ISI_TIME = 500 # ISI time [Contextual]


# ---------- Instruction Pages ----------

# Contextual
PRACTICE4_1_PAGE = 11 # Practice 4-1 begins after page ~
PRACTICE4_2_PAGE = 13 # Practice 4-2 begins after page ~
C_SINGLE_BLOCK1_PAGE = 14 # Single-task block 1 begins after page ~
C_SINGLE_BLOCK2_PAGE = 15 # Single-task block 2 begins after page ~
C_MIXED_PRACTICE_PAGE = 16 # Mixed-task practice begins after page ~
BLOCK5_PAGE = 17 # Block 5 begins after page ~
BLOCK6_PAGE = 20 # Block 6 begins after page ~
C_END_PAGE = 21 # Contextual tasks ends after page ~



# ---------- Joystick Control ----------

DZ_X = 0.5      # deadzone for x-axis ([0,1])
DZ_Y = 0.5      # deadzone for y-axis ([0,1])

JOY_MODE = 2    # number of discrete joystick directions
# JOY_MODE = 4


# ---------- Runtime State ----------
PID: str | None = None                  # participant ID
MAPPING: int | None = None              # task mapping (1 / 2)
DH: str | None = None                   # participant's dominant hand (left / right)
UH: str | None = None                   # hand used during task (left / right)
START_TIME: str | None = None           # task start time (ISO format)

_is_fullscreen: bool = True         # current fullscreen state
_input_source: str | None = None    # response input source (key = keyboard / joy = joystick)
_start_time: str | None = None      # block start time (ISO format)
_end_time: str | None = None        # block end time (ISO format)
key_response: str | None = None     # actual keyboard key pressed
joy_response: str | None = None     # actual joystick direction
