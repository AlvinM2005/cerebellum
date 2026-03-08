"""
Centralized configuration constants and runtime state.
"""


# ---------- Default ----------
MODE = "demo"       # quick testing
# MODE = "full"     # real participant runs


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
INSTRUCTION_TASK_AFTER_PNG_BY_MAPPING = {
    1: (8, 11, 20, 23, 34, 37, 40),
    2: (8, 11, 20, 23, 34, 37, 40),
    3: (20, 23, 8, 11, 34, 37, 40),
    4: (20, 23, 8, 11, 34, 37, 40),
}


# ---------- Stimuli ----------

if MODE == "demo":
    MAX_RESPONSE_TIME = 1000
    FIXATION_CROSS_TIME = 1000
else:
    MAX_RESPONSE_TIME = 2000
    FIXATION_CROSS_TIME = 1000


# ---------- Feedback ----------

FB_W = 200
FB_H = 200
FB_DURATION = 1000


# ---------- Joystick ----------

DZ_X = 0.5
DZ_Y = 0.5
JOY_MODE = 2


# ---------- Runtime State ----------

PID: str | None = None
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
