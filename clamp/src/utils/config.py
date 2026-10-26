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

# Task design (cycle-based; no trial files). One cycle = the three target angles once each, in random order.
#   no_feedback_baseline -> no cursor (no_fb), rotation 0; currently DISABLED (0 cycles; set 10 full / 2 demo to restore)
#   feedback_baseline -> cursor follows the hand (veridical_fb), rotation 0
#   clamp_demo        -> 4 fixed demonstration reaches (clamped_fb, special rotations), no cycles
#   clamp             -> clamped_fb, rotation = +/-ROTATION depending on the mapping
#   after_effect      -> no feedback, rotation 0

ROTATION = 15                   # clamp size (deg); mapping 1 -> +ROTATION (CCW), mapping 2 -> -ROTATION (CW)
CLAMP_TARGET_ANGLES = (0, 120, 240)                           # deg, counter-clockwise from +x
CLAMP_DEMO_REACHES = ((270, 180), (270, 135), (270, -135), (270, 180))  # (target angle, rotation) of clamp_demo

# A block with 0 cycles is skipped (no_feedback_baseline is switched off this way).
if MODE == "demo":
    CLAMP_CYCLES = {"no_feedback_baseline": 0, "feedback_baseline": 2, "clamp": 4, "after_effect": 2}      # cycles per block
    CLAMP_PHASE_TRIALS = {"no_feedback_baseline": 2, "feedback_baseline": 2, "clamp": 3, "after_effect": 2}    # trials in the early / late window
else:   # MODE == "full"
    CLAMP_CYCLES = {"no_feedback_baseline": 0, "feedback_baseline": 10, "clamp": 30, "after_effect": 5}
    CLAMP_PHASE_TRIALS = {"no_feedback_baseline": 10, "feedback_baseline": 10, "clamp": 30, "after_effect": 5}

CLAMP_N_TRIALS = len(CLAMP_TARGET_ANGLES) * sum(CLAMP_CYCLES.values()) + len(CLAMP_DEMO_REACHES)

# Hand variables computed at the end of the task (see saves.finalize_hand_variables)
if MODE == "demo":
    HAND_MA_WINDOW = 2          # moving average of hand_flip: this many cycles, starting at the current cycle
else:   # MODE == "full"
    HAND_MA_WINDOW = 5
HAND_OUTLIER_SD = 3             # hand_out_rm drops trials whose |hand_res| exceeds this many SDs of hand_res

CLAMP_TARGET_DIST_FRAC = 0.371  # target distance D = 0.371 * H
CLAMP_RADIUS_RATIO = 3.33 / 80  # start / target / cursor radius = D * 3.33 / 80
CLAMP_VIS_RADIUS_FRAC = 0.5     # cursor drawn during search only within 0.5 * D of the start
CLAMP_START_STROKE = 2          # start circle outline width (px)

HOLD_TIME = 500                 # hold inside the start circle before target onset (ms)
TOO_SLOW_TIME = 500             # movement time above this is flagged too_slow = 1 (ms)
TOO_SLOW_MSG_TIME = 750         # the message below is shown only when movement time exceeds this (ms)
TOO_SLOW_FB_TIME = 750          # duration of the too-slow message (ms)
TOO_FAR_ERROR = 90              # |error| at or above this (deg) is a too-far reach (recorded only, no feedback shown)
CLAMP_FEEDBACK_MS = 50          # duration of the endpoint cursor feedback (ms)
SEARCH_HINT_DELAY = 3000        # show the "find your cursor" hint after this long in Search (ms)
if MODE == "demo":
    CLAMP_PAUSE_S = 3           # mandatory pause between the clamp and the after_effect block (s)
else:   # MODE == "full"
    CLAMP_PAUSE_S = 60
KNOCK_FREQ = 160               # "knock" sound played when the hand crosses the target distance fast enough (Hz)
KNOCK_MS = 90                   # knock duration (ms)
KNOCK_VOLUME = 0.8              # 0-1
RESET_DELAY = 300               # blank interval before the next trial (ms)

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
