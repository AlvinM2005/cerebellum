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

if MODE == "demo":
    MIN_READING_TIME = 100  # minimum time per instruction page before allowing next (ms)
else:   # MODE = "full"
    MIN_READING_TIME = 1000



# ---------- Stimuli ----------
if MODE == "demo":
    MAX_RESPONSE_TIME = 1000    # maximum response time (ms)
    FIXATION_CROSS = 500        # fixation cross duration (ms)

    COLOR_PRACTICE_COUNT = 5    # color practice number of trials
    STROOP_PRACTICE_COUNT = 5   # stroop practice number of trials、

    INTERVAL_MIN = 3000         # minimum time for an interval (ms)
    INTERVAL_MAX = 5000         # maximum time for an interval (ms)
    INTERVAL_PRACTICE_COUNT = 2 # interval practice number of intervals
    
    SPEED_PRACTICE_COUNT = 1            # speed practice number of intervals
    ACCURACY_PRACTICE_COUNT = 1         # accuracy practice number of intervals
    VARYING_PRACTICE_SPEED_COUNT = 1    # varying practice (speed) number of intervals
    VARYING_PRACTICE_ACCURACY_COUNT = 1 # varying practice (accuracy) number of intevals

    SPEED_TEST_COUNT = 1            # speed test number of intervals
    ACCURACY_TEST_COUNT = 1         # accuracy test number of intervals
    VARYING_TEST_SPEED_COUNT = 1    # varying test (speed) number of intervals
    VARYING_TEST_ACCURACY_COUNT = 1 # varying test (accuracy) number of intevals

else:   # MODE = "full"
    MAX_RESPONSE_TIME = 3000
    FIXATION_CROSS = 500

    COLOR_PRACTICE_COUNT = 60
    STROOP_PRACTICE_COUNT = 30

    INTERVAL_MIN = 8000
    INTERVAL_MAX = 10000
    INTERVAL_PRACTICE_COUNT = 4

    SPEED_PRACTICE_COUNT = 3
    ACCURACY_PRACTICE_COUNT = 3
    VARYING_PRACTICE_SPEED_COUNT = 2
    VARYING_PRACTICE_ACCURACY_COUNT = 2

    SPEED_TEST_COUNT = 3
    ACCURACY_TEST_COUNT = 3
    VARYING_TEST_SPEED_COUNT = 2
    VARYING_TEST_ACCURACY_COUNT = 2



# ---------- Feedback ----------

FB_W = 100  # feedback image width (px)
FB_H = 100  # feedback image height (px)

if MODE == "demo":
    FB_DURATION = 1000          # feedback duration (ms)
    FB_SCREEN_DURATION = 2000   # feedback screen display duration (ms) (for intervals)
else:   # MODE == "full"
    FB_DURATION = 1000
    FB_SCREEN_DURATION = 5000



# ---------- Joystick Control ----------

DZ_X = 0.6      # deadzone for x-axis ([0,1])
DZ_Y = 0.6      # deadzone for y-axis ([0,1])

# JOY_MODE = 2    # number of discrete joystick directions
JOY_MODE = 4



# ---------- Runtime State ----------
PID: str | None = None                  # participant ID
MAPPING: int | None = None              # task mapping (1 / 2)
DH: str | None = None                   # participant's dominant hand (left / right)
UH: str | None = None                   # hand used during task (left / right)
START_TIME: str | None = None           # task start time (ISO format)\nglobal_start_time: str | None = None  # whole-task start time (ISO)\nglobal_end_time: str | None = None    # whole-task end time (ISO)

_is_fullscreen: bool = True         # current fullscreen state
_input_source: str | None = None    # response input source (key = keyboard / joy = joystick)
_start_time: str | None = None      # block start time (ISO format)
_end_time: str | None = None        # block end time (ISO format)
key_response: str | None = None     # actual keyboard key pressed
joy_response: str | None = None     # actual joystick direction
version: int | None = None    # PID-derived version (0-15)

# ---------- Task Sequences ----------
# Each item is a 4-step goal sequence using codes:
#   S = Speed, A = Accuracy, V = Varying
TASK_SEQUENCES: list[tuple[str, str, str, str]] = [
    ("S","A","V","V"),
    ("S","V","A","V"),
    ("S","V","V","A"),
    ("A","S","V","V"),
    ("A","V","S","V"),
    ("A","V","V","S"),
    ("V","S","A","V"),
    ("V","S","V","A"),
    ("V","A","S","V"),
    ("V","A","V","S"),
    ("V","V","S","A"),
    ("V","V","A","S"),
]

# Selected sequence for current run (set after version is derived)
task_sequence: tuple[str, str, str, str] | None = None

# ---------- Color-to-Direction Mapping (JOY_MODE==4) ----------
# Normal mapping; MAPPING==2 flips left↔right and up↔down
COLOR_TO_DIR = {
    "BLUE": "up",
    "GREEN": "down",
    "RED": "left",
    "YELLOW": "right",
}

def expected_dir_for_color(color: str) -> str:
    d = COLOR_TO_DIR.get(color)
    if d is None:
        return "NA"
    if MAPPING == 2:
        flip = {"left": "right", "right": "left", "up": "down", "down": "up"}
        return flip.get(d, d)
    return d

