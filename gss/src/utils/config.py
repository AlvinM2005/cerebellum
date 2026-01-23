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

# TEST mode (for testing only)
if MODE == "test":
    INTERVALS = [3000, 4000, 5000]                      # for each intervals, randomly choose a number ~ from INTERVALS and give the participant ~ms to respond (similar to phases in other tasks)

# ACTUAL mode
else:
    INTERVALS = [8000, 9000, 10000, 11000, 12000]

# ---------- Pygame UI settings ----------

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
INSTRUCTION_COUNT = 29

INSTRUCTIONS = []
for i in range(INSTRUCTION_COUNT):
    INSTRUCTIONS.append(RESOURCES_DIR / "instructions" / f"{i+1}.jpg")

ACCURACY_BLOCK_INS = RESOURCES_DIR / "instructions" / "Accuracy_Block.jpg"
SPEED_BLOCK_INS = RESOURCES_DIR / "instructions" / "Speed_Block.jpg"
VARYING_BLOCK_INS = RESOURCES_DIR / "instructions" / "Varying_block.jpg"

PRACTICE_INTERVAL_INS = RESOURCES_DIR / "instructions" / "Practice_Interval.jpg"
MAIN_INTERVAL = RESOURCES_DIR / "instructions" / "Main_Interval.jpg"

MAPPING_INS = 6                  # mapping_practice begins after page ~
STROOP_INS = 16             # stroop_practice begins after page ~
GSS_PRACTICE_INS = 22       # gss_practice begins after page ~
GSS_MAIN_SEC1_INS = 26      # gss_main section 1 begins after page ~
GSS_MAIN_SEC2_INS = 27      # gss_main section 2 begins after page ~
GSS_MAIN_SEC3_INS = 28      # gss_main section 2 begins after page ~

MAIN_INTERVAL_TEXT_POS = (383, 270)     # Feedback text on the main interval page ("You anwered [    ] trials correctly")

# TEST mode (for testing only)
if MODE == "test":
    MIN_READING_TIME = 100      # minimum reading time to spend on each instruction page

# ACTUAL mode (for actual task)
else:
    MIN_READING_TIME = 1000


# ---------- Stimulus settings ----------
# Mapping practice
MAPPING_STIM_DIR = RESOURCES_DIR / "stimuli" / "mapping_practice"

CIRCLE_BLUE = MAPPING_STIM_DIR / "circle_blue.jpg"
CIRCLE_GREEN = MAPPING_STIM_DIR / "circle_green.jpg"
CIRCLE_RED = MAPPING_STIM_DIR / "circle_red.jpg"
CIRCLE_YELLOW = MAPPING_STIM_DIR / "circle_yellow.jpg"

MAPPING_STIMULI = [CIRCLE_BLUE, CIRCLE_GREEN, CIRCLE_RED, CIRCLE_YELLOW]

# Stroop practice
STROOP_STIM_DIR = RESOURCES_DIR / "stimuli" / "stroop_practice"

BLUE_B = STROOP_STIM_DIR / "blue_b.png"     # a blue BLUE
BLUE_G = STROOP_STIM_DIR / "blue_g.png"     # a green BLUE
BLUE_R = STROOP_STIM_DIR / "blue_r.png"     # a red BLUE
BLUE_Y = STROOP_STIM_DIR / "blue_y.png"     # a yellow BLUE

GREEN_B = STROOP_STIM_DIR / "green_b.png"     # a blue GREEN
GREEN_G = STROOP_STIM_DIR / "green_g.png"     # a green GREEN
GREEN_R = STROOP_STIM_DIR / "green_r.png"     # a red GREEN
GREEN_Y = STROOP_STIM_DIR / "green_y.png"     # a yellow GREEN

RED_B = STROOP_STIM_DIR / "red_b.png"     # a blue RED
RED_G = STROOP_STIM_DIR / "red_g.png"     # a green RED
RED_R = STROOP_STIM_DIR / "red_r.png"     # a red RED
RED_Y = STROOP_STIM_DIR / "red_y.png"     # a yellow RED

YELLOW_B = STROOP_STIM_DIR / "yellow_b.png"     # a blue YELLOW
YELLOW_G = STROOP_STIM_DIR / "yellow_g.png"     # a green YELLOW
YELLOW_R = STROOP_STIM_DIR / "yellow_r.png"     # a red YELLOW
YELLOW_Y = STROOP_STIM_DIR / "yellow_y.png"     # a yellow YELLOW

STROOP_STIMULI = [
    [BLUE_B, "blue", "blue"],   # [path, color, text]
    [BLUE_G, "green", "blue"],
    [BLUE_R, "red", "blue"],
    [BLUE_Y, "yellow", "blue"],
    [GREEN_B, "blue", "green"],
    [GREEN_G, "green", "green"],
    [GREEN_R, "red", "green"],
    [GREEN_Y, "yellow", "green"],
    [RED_B, "blue", "red"],
    [RED_G, "green", "red"],
    [RED_R, "red", "red"],
    [RED_Y, "yellow", "red"],
    [YELLOW_B, "blue", "yellow"],
    [YELLOW_G, "green", "yellow"],
    [YELLOW_R, "red", "yellow"],
    [YELLOW_Y, "yellow", "yellow"],
]

# GSS practice (using the same stimulus as [Stroop Practice]; put into a separate list to differentiate)
GSS_PRACTICE_STIMULI = [
    [BLUE_B, "blue", "blue"],   # [path, color, text]
    [BLUE_G, "green", "blue"],
    [BLUE_R, "red", "blue"],
    [BLUE_Y, "yellow", "blue"],
    [GREEN_B, "blue", "green"],
    [GREEN_G, "green", "green"],
    [GREEN_R, "red", "green"],
    [GREEN_Y, "yellow", "green"],
    [RED_B, "blue", "red"],
    [RED_G, "green", "red"],
    [RED_R, "red", "red"],
    [RED_Y, "yellow", "red"],
    [YELLOW_B, "blue", "yellow"],
    [YELLOW_G, "green", "yellow"],
    [YELLOW_R, "red", "yellow"],
    [YELLOW_Y, "yellow", "yellow"],
]

# GSS main (using the same stimulus as [Stroop Practice]; put into a separate list to differentiate)
GSS_PRACTICE_STIMULI = [
    [BLUE_B, "blue", "blue"],   # [path, color, text]
    [BLUE_G, "green", "blue"],
    [BLUE_R, "red", "blue"],
    [BLUE_Y, "yellow", "blue"],
    [GREEN_B, "blue", "green"],
    [GREEN_G, "green", "green"],
    [GREEN_R, "red", "green"],
    [GREEN_Y, "yellow", "green"],
    [RED_B, "blue", "red"],
    [RED_G, "green", "red"],
    [RED_R, "red", "red"],
    [RED_Y, "yellow", "red"],
    [YELLOW_B, "blue", "yellow"],
    [YELLOW_G, "green", "yellow"],
    [YELLOW_R, "red", "yellow"],
    [YELLOW_Y, "yellow", "yellow"],
]

# TEST mode (for testing only)
if MODE == "test":
    MAPPING_TRIAL_COUNT = 2                 # mapping practice contains ~ trials
    MAPPING_ITI = 1000                      # ~ms between two consequtive mapping practice trials
    STROOP_TRIAL_COUNTS = 2                 # stroop practice contains ~ trials
    STROOP_ITI = 1000                       # ~ms between two consequtive stroop practice trials
    GSS_PRACTICE_TRIAL_COUNTS = 3           # gss practice contains ~ trials per interval
    GSS_PRACTICE_ITI = 1000                 # ~ms between two consequenive gss practice trials
    GSS_MAIN_INTERVAL_COUNTS = 5            # gss main contains ~ intervals
    GSS_MAIN_TRIAL_COUNTS = 2               # gss main contains ~ trials per interval
    GSS_MAIN_ITI = 1000                     # ~ms between two consequetive gss main trials (set LONGER for the participants to read the feedback in ACTUAL mode)
    MAX_BLOCK_INFO_DISPLAY_DURATION = 3000  # display the block info (accuracy / speed / varying) for ~ms (if not pressed [SPACE])
    MARKER_DISPLAY_DURATION = 1000          # display the marker (accuracy / speed) for ~ms

# ACTUAL mode (for actual task)
else:
    MAPPING_TRIAL_COUNT = 3
    MAPPING_ITI = 3000
    STROOP_TRIAL_COUNTS = 3
    STROOP_ITI = 3000
    GSS_PRACTICE_TRIAL_COUNTS = 3
    GSS_PRACTICE_ITI = 3000
    GSS_MAIN_INTERVAL_COUNTS = 5
    GSS_MAIN_TRIAL_COUNTS = 5
    GSS_MAIN_ITI = 5000
    MAX_BLOCK_INFO_DISPLAY_DURATION = 10000
    MARKER_DISPLAY_DURATION = 1500


# ---------- Marker settings ----------
ACCURACY_MARKER = RESOURCES_DIR / "marker" / "gss_accuracy.png"
SPEED_MARKER = RESOURCES_DIR / "marker" / "gss_speed.png"

MARKER_W = 200
MARKER_H = 200

# TEST mode (for testing only)
if MODE == "test":
    CONSEQUTIVE_TRIALS = 2     # set an upper bound to the variability: the goal remains the same in groups of ~ (have at least [CONSEQUTIVE_TRIALS] consequtive trials with the same goal)
    CONSEQUTIVE_GROUPS = 2      # set a lower bound to the variability: have at most ~ groups of the same goal (have at most [CONSEQUTIVE_TRIALS * CONSEQUTIVE_GROUPS] trials with the same goal)


# ACTUAL mode (for actual task)
else:
    CONSEQUTIVE_TRIALS = 3
    CONSEQUTIVE_GROUPS = 2


# ---------- Feedback settings ----------
FB_CORRECT = RESOURCES_DIR / "feedback" / "feedback_correct.png"        # correct feedback image
FB_INCORRECT = RESOURCES_DIR / "feedback" / "feedback_incorrect.png"    # incorrect feedback image

FB_W = 100
FB_H = 100

# TEST mode (for testing only)
if MODE == "test":
    FB_DURATION = 500      # feedback duration


# ACTUAL mode (for actual task)
else:
    FB_DURATION = 1500


# ---------- Runtime condition assignment ----------
_is_fullscreen: bool = True         # full screen / window mode marker
PID: str | None = None              # participant id
VERSION: int | None = None          # task version (1/2)
START_TIME: str | None = None       # global start time

correct_ind: int | None = None      # correct answer for the current trial
correct_count: int | None = None    # temporary count of continuous correct answers
trial_count: int | None = None      # number of trials made for the current phase