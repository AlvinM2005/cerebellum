"""
Centralized configuration constants and runtime state.
"""


# ---------- Default ----------
# MODE = "demo"       # quick testing
MODE = "full"     # real participant runs


# ---------- Pygame UI ----------

RED_RGB = (255, 72, 72)
BLUE_RGB = (72, 197, 255)
WHITE_RGB = (236, 236, 236)
COCO_RGB = (192, 192, 192)
BLACK_RGB = (0, 0, 0)
GRAY_RGB = (128, 128, 128)
YELLOW_RGB = (255, 255, 0)

SCREEN_W = 1280
SCREEN_H = 720

FONT_SMALL = 48
FONT_LARGE = 72
FONT_TOO_LATE = 60


# ---------- Instructions ----------

MIN_READING_TIME = 100 if MODE == "demo" else 1000

INSTRUCTION_TASK_ORDER = (
    "phonetic_task_practice",
    "phonetic_task_experimental",
    "orthographic_task_practice",
    "orthographic_task_experimental",
    "multi_task_practice",
    "multi_task_experimental_block_1",
    "multi_task_experimental_block_2",
)

# "start task right after X.png"
# Mappings 5-8 use identical instruction pages as 1-4 (block order is not
# mentioned in the multi-task instructions); the actual block order is
# controlled at the trial-series level in experiment_flow.py.
INSTRUCTION_TASK_AFTER_PNG_BY_MAPPING = {
    1: (8, 11, 20, 23, 34, 37, 40),
    2: (8, 11, 20, 23, 34, 37, 40),
    3: (20, 23, 8, 11, 34, 37, 40),
    4: (20, 23, 8, 11, 34, 37, 40),
    5: (8, 11, 20, 23, 34, 37, 40),  # phonetic first, blocks reversed
    6: (8, 11, 20, 23, 34, 37, 40),  # phonetic first, blocks reversed
    7: (20, 23, 8, 11, 34, 37, 40),  # orthographic first, blocks reversed
    8: (20, 23, 8, 11, 34, 37, 40),  # orthographic first, blocks reversed
}

# Block labels for the CSV output.
# b3 = first multi-task experimental block presented, b4 = second.
# MAPPING 1-2 & 5-6: phonetic first → p1/b1, then orthographic → p2/b2, then multi → p3/b3/b4
# MAPPING 3-4 & 7-8: orthographic first → p1/b1, then phonetic → p2/b2, then multi → p3/b3/b4
# (For mappings 5-8 the trial DATA for b3/b4 is swapped in experiment_flow.py.)
_MAPPING_PHONETIC_FIRST = {
    "phonetic_task_practice":           "p1",
    "phonetic_task_experimental":        "b1",
    "orthographic_task_practice":        "p2",
    "orthographic_task_experimental":    "b2",
    "multi_task_practice":               "p3",
    "multi_task_experimental_block_1":   "b3",
    "multi_task_experimental_block_2":   "b4",
}
_MAPPING_ORTHOGRAPHIC_FIRST = {
    "orthographic_task_practice":        "p1",
    "orthographic_task_experimental":    "b1",
    "phonetic_task_practice":            "p2",
    "phonetic_task_experimental":        "b2",
    "multi_task_practice":               "p3",
    "multi_task_experimental_block_1":   "b3",
    "multi_task_experimental_block_2":   "b4",
}
BLOCK_LABEL_BY_MAPPING = {
    1: _MAPPING_PHONETIC_FIRST,
    2: _MAPPING_PHONETIC_FIRST,
    3: _MAPPING_ORTHOGRAPHIC_FIRST,
    4: _MAPPING_ORTHOGRAPHIC_FIRST,
    5: _MAPPING_PHONETIC_FIRST,
    6: _MAPPING_PHONETIC_FIRST,
    7: _MAPPING_ORTHOGRAPHIC_FIRST,
    8: _MAPPING_ORTHOGRAPHIC_FIRST,
}


# ---------- Stimuli ----------

# Scale factor for stimulus images (1.0 = native size, 0.5 = half size).
# Change STIM_SCALE here to make stimuli larger or smaller.
STIM_SCALE = 0.75

if MODE == "demo":
    MAX_RESPONSE_TIME_SINGLE = 1000
    MAX_RESPONSE_TIME_MULTI  = 1000
    FIXATION_CROSS_TIME = 1000
else:
    MAX_RESPONSE_TIME_SINGLE = 4000
    MAX_RESPONSE_TIME_MULTI  = 5000
    FIXATION_CROSS_TIME = 1000


# ---------- Feedback ----------

FB_W = 100
FB_H = 100
FB_DURATION = 1000


# ---------- Joystick ----------

DZ_X = 0.5
DZ_Y = 0.5
JOY_MODE = 2


# ---------- Runtime State ----------

PID: str | None = None
LANGUAGE: str | None = None            # language (spanish / english)
GROUP: str | None = None               # group (pilot / control / cd / stroke / tumor / other)
SESSION: str | None = None             # session (s1-s9)
MAPPING: int | None = None              # 1 / 2 / 3 / 4
DH: str | None = None
UH: str | None = None

START_TIME: str | None = None
GLOBAL_END_TIME: str | None = None

_is_fullscreen: bool = True
_input_source: str | None = None        # key / joy
_start_time: str | None = None
_end_time: str | None = None
key_response: str | None = None
joy_response: str | None = None
