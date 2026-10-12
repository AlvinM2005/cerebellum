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
WINDOW_W = 1280 # windowed-mode width (px)
WINDOW_H = 720  # windowed-mode height (px)
TEXT_INPUT_ON = True  # False after PID entry: disables IME so letter keys are not swallowed

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

STIMULI_COUNT = 5

if MODE == "demo":
    MAX_RESPONSE_TIME = 1000    # maximum response time (ms)
    FIXATION_CROSS = 500        # fixation cross duration (ms)
    ISI = 500                   # inter stimulus interval (ms)
else:   # MODE = "full"
    MAX_RESPONSE_TIME = 3000
    FIXATION_CROSS = 500
    ISI = 500



# ---------- Feedback ----------

FB_W = 200  # feedback image width (px)
FB_H = 200  # feedback image height (px)

if MODE == "demo":
    FB_DURATION = 500   # feedback duration (ms)
else:   # MODE == "full"
    FB_DURATION = 2000



# ---------- Joystick Control ----------

DZ_X = 0.5      # deadzone for x-axis ([0,1])
DZ_Y = 0.5      # deadzone for y-axis ([0,1])

JOY_MODE = 2    # number of discrete joystick directions
# JOY_MODE = 4


# ---------- Clamp Task ----------
# Source: Clamp_Task_Procedure.pdf (Section 8, Table 7). Sizes are relative to the
# screen height H, so the layout scales with the display.

CLAMP_FILE_N_TRIALS = 284       # trials in every trial file (Elizabeth's v0..v50)

if MODE == "demo":
    # Minimal run that still shows every feature (15 trials, ~3 min):
    #   baseline (no feedback)  -> picks of original trials 1, 2, 3 + 40 (40 carries the "After trial 40" message)
    #   clamp demonstration     -> original trials 41-44 (the 4 demo reaches; 44 carries the understanding check)
    #   clamp feedback          -> original trials 45, 46, 47 + 244 (244 carries the "After trial 244" message)
    #   post-test (no feedback) -> original trials 245, 246, 247
    # The picked trials are renumbered 1..15; the trial counter and the saved "trial" column use the new numbers.
    CLAMP_DEMO_PICK = (1, 2, 3, 40, 41, 42, 43, 44, 45, 46, 47, 244, 245, 246, 247)
    CLAMP_N_TRIALS = len(CLAMP_DEMO_PICK)
    CLAMP_BLOCKS = (
        (1, 4, "baseline"),
        (5, 8, "clamp_demo"),
        (9, 12, "clamp"),
        (13, 15, "post_test"),
    )
    N_KEY_CHECKS = 2
    KEY_CHECK_FIXED = (2, 10)       # key-press checks after demo trials 2 (baseline) and 10 (clamp)
    KEY_CHECK_RANGE = (1, 15)
    KEY_CHECK_EXCLUDE = (4, 8)
else:   # MODE == "full"
    CLAMP_DEMO_PICK = None
    CLAMP_N_TRIALS = 284            # 40 baseline + 4 demo + 200 clamp + 40 post-test
    CLAMP_BLOCKS = (                # (first trial, last trial, block name), 1-indexed, inclusive
        (1, 40, "baseline"),
        (41, 44, "clamp_demo"),
        (45, 244, "clamp"),
        (245, 284, "post_test"),
    )
    N_KEY_CHECKS = 5                # number of key-press attention checks (meta parameter)
    KEY_CHECK_FIXED = None
    KEY_CHECK_RANGE = (20, 50)      # key checks are placed after a trial in this range (inclusive) ...
    KEY_CHECK_EXCLUDE = (40, 44)    # ... excluding this range (break message + demo trials)

CLAMP_TARGET_DIST_FRAC = 0.371  # target distance D = 0.371 * H
CLAMP_RADIUS_RATIO = 3.33 / 80  # start / target / cursor radius = D * 3.33 / 80
CLAMP_VIS_RADIUS_FRAC = 0.5     # cursor drawn during search only within 0.5 * D of the start
CLAMP_START_STROKE = 2          # start circle outline width (px)

HOLD_TIME = 500                 # hold inside the start circle before target onset (ms)
TOO_SLOW_TIME = 300             # movement time above this is a too-slow reach (ms); Tsay et al. (2021) used 500
TOO_SLOW_FB_TIME = 750          # feedback period of a too-slow reach (ms)
SEARCH_HINT_DELAY = 3000        # show the "find your cursor" hint after this long in Search (ms)
RESET_DELAY = 300               # blank interval before the next trial (ms)
# Feedback duration (delayed_duration) is read per trial from the trial file (50 ms).

ATTENTION_MESSAGE_DURATION = 2000   # "Pay attention!" duration (ms)

CLAMP_MAX_FPS = 240             # frame-rate cap of the trial loop (vsync normally limits it first)

PURE_WHITE_RGB = (255, 255, 255)    # cursor / start circle / task text (the template WHITE_RGB is off-white)


# ---------- Runtime State ----------
PID: str | None = None                  # participant ID
MAPPING: int | None = None              # task mapping (1 / 2)
DH: str | None = None                   # participant's dominant hand (left / right)
UH: str | None = None                   # hand used during task (left / right)
GROUP: int | None = None                # group index (1..6)
SESSION: int | None = None              # session index (1..6)
MOUSE_TYPE: str | None = None           # mouse type (Optical mouse / Trackpad mouse / Trackball mouse)
START_TIME: str | None = None           # task start time (ISO format)

_is_fullscreen: bool = True         # current fullscreen state
_input_source: str | None = None    # response input source (key = keyboard / joy = joystick)
_start_time: str | None = None      # block start time (ISO format)
_end_time: str | None = None        # block end time (ISO format)
key_response: str | None = None     # actual keyboard key pressed
joy_response: str | None = None     # actual joystick direction
