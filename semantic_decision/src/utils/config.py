# ./src/utils/config.py
"""
Application configuration module.

This module defines and centralizes all meta-parameters
used to control application behavior.
"""

# ---------- Runtime Condition Assignment ----------
PID: str | None = None           # participant ID
MAPPING: int | None = None       # MAPPIG
TYPE: str | None = None          # practice or experimental
MODE: str | None = None          # actual or demo
START_TIME: str | None = None    # global start time
END_TIME: str | None = None      # global end time
RESULTS_FILE: str | None = None  # participant file results 
DH: str | None = None                   # participant's dominant hand (left / right)
UH: str | None = None                   # hand used during task (left / right)

_is_fullscreen: bool = True             # fullscreen / window mode flag


# ---------- Pygame UI ----------

# color
RED_RGB = (255, 72, 72)     # FF4848
BLUE_RGB = (72, 197, 255)   # 48C5FF
COCO_RGB = "#C0C0C0"      # Text
BLACK_RGB = (0,0,0)         # 000000
GRAY_RGB = (128,128,128)    # 808080
YELLOW_RGB = (255,255,0)    # FFFF00
FONT = "resources\OpenSans.ttf"
# screen size
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

# font size
FONT_SIZE = 48
FONT_SMALL = 48

TASK: str = "SD"

# ---------- MODE Settings ----------

def initialize_mode_settings():
    """Initialize settings that depend on MODE."""
    global MIN_READING_TIME, FB_DURATION, STIMULI_COUNT_PRAC, STIMULI_COUNT_EXPERIMENTAL
    
    if MODE == "demo":  
        MIN_READING_TIME = 10
        FB_DURATION = 500
        STIMULI_COUNT_PRAC = 3
        STIMULI_COUNT_EXPERIMENTAL = 5
    else:
        MIN_READING_TIME = 1000
        FB_DURATION = 1000
        STIMULI_COUNT_PRAC = 9
        STIMULI_COUNT_EXPERIMENTAL = 45 # 15 for each condition


# ---------- Instructions ----------

INSTRUCTIONS_COUNT = 23

# ---------- Stimuli ----------

TARGET_WORD_DURATION = 4000
MAX_RESPONDE_TIME = TARGET_WORD_DURATION
FIXATION_CROSS = 500
WORD_PRESENTATION = 500


# ---------- Feedback ----------

FB_W = 200  # feedback image width
FB_H = 200  # feedback image height

BLOCK1_PG = 14 
BLOCK2_PG = 18 
LAST_PG = 23
# after practice start jpg 14, after speed block start jpg 18, after speed acc start jpg 23, after speed acc start jpg 28 DONE


# ---------- Joystick Control ----------

dz_x = 0.5  # deadzone for x-axis
dz_y = 0.75  # deadzone for y-axis

js_mode = 2 # how many options can the joystick maps to