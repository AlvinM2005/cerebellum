# ./src/utils/config.py
"""
Application configuration module.

This module defines and centralizes all meta-parameters
used to control application behavior.
"""


# ---------- Default ----------
# TODO: Select "test" mode for testing purposes, "actual" mode when implementing the test
MODE = "test"
# MODE = "actual"


# ---------- Pygame UI ----------

# color
RED_RGB = (255, 72, 72)     # FF4848
BLUE_RGB = (72, 197, 255)   # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0,0,0)         # 000000
GRAY_RGB = (128,128,128)    # 808080
YELLOW_RGB = (255,255,0)    # FFFF00

# screen size
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

# font size
FONT_SIZE = 48


# ---------- Instructions ----------

INSTRUCTIONS_COUNT = 5

if MODE == "test":
    MIN_READING_TIME = 100  # participants must spend at least ~ms on each instruction page before they can proceed to the next
else:   # MODE = "actual"
    MIN_READING_TIME = 100

# TODO: Add additional instructions configurations if necessary (i.e. MIN_READING_TIME)


# ---------- Stimuli ----------

STIMULI_COUNT = 5

if MODE == "test":
    MAX_RESPONDE_TIME = 1000    # participants have at most ~ms to responde
    FIXATION_CROSS = 500
else:   # MODE = "actual"
    MAX_RESPONDE_TIME = 3000
    FIXATION_CROSS = 500

# TODO: Add additional stimuli configurations if necessary (i.e. ITI)


# ---------- Feedback ----------

FB_W = 200  # feedback image width
FB_H = 200  # feedback image height

if MODE == "test":
    FB_DURATION = 500
else:   # MODE == "actual"
    FB_DURATION = 2000

# TODO: Add additional feedback configurations if necessary


# ---------- Joystick Control ----------

dz_x = 0.5  # deadzone for x-axis
dz_y = 0.5  # deadzon for y-axis

js_mode = 2 # how many options can the joystick maps to
# js_mode = 4

# TODO: Select one of the two js_modes

# ---------- Runtime Condition Assignment ----------
PID: str | None = None          # participant ID
START_TIME: str | None = None   # global start time

_is_fullscreen: bool = True             # fullscreen / window mode flag
dominant_hand: str | None = None        # "left" or "right"
less_affected_hand: str | None = None   # "left" or "right"
