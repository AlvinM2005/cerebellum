# ./src/utils/config.py
from pathlib import Path
import utils.config as cfg

# ---------- Instructions settings ----------
def load_instructions():
    if cfg.VERSION == 1:
        INSTRUCTION_DIR = cfg.RESOURCES_DIR / "instructions"
    else:
        INSTRUCTION_DIR = cfg.RESOURCES_DIR / "instructions_reversed"

    INSTRUCTIONS = []
    for i in range(cfg.INSTRUCTION_COUNT):
        INSTRUCTIONS.append(INSTRUCTION_DIR / f"{i+1}.jpg")

    ACCURACY_BLOCK_INS = INSTRUCTION_DIR / "Accuracy_Block.jpg"
    SPEED_BLOCK_INS = INSTRUCTION_DIR / "Speed_Block.jpg"
    VARYING_BLOCK_INS = INSTRUCTION_DIR / "Varying_block.jpg"

    PRACTICE_INTERVAL_INS = INSTRUCTION_DIR / "Practice_Interval.jpg"
    MAIN_INTERVAL = INSTRUCTION_DIR / "Main_Interval.jpg"

    return INSTRUCTIONS, ACCURACY_BLOCK_INS, SPEED_BLOCK_INS, VARYING_BLOCK_INS, PRACTICE_INTERVAL_INS, MAIN_INTERVAL


# ---------- Stimulus settings ----------
# Mapping practice
MAPPING_STIM_DIR = cfg.RESOURCES_DIR / "stimuli" / "mapping_practice"

CIRCLE_BLUE = MAPPING_STIM_DIR / "circle_blue.jpg"
CIRCLE_GREEN = MAPPING_STIM_DIR / "circle_green.jpg"
CIRCLE_RED = MAPPING_STIM_DIR / "circle_red.jpg"
CIRCLE_YELLOW = MAPPING_STIM_DIR / "circle_yellow.jpg"

MAPPING_STIMULI = [CIRCLE_BLUE, CIRCLE_GREEN, CIRCLE_RED, CIRCLE_YELLOW]

# Stroop practice
STROOP_STIM_DIR = cfg.RESOURCES_DIR / "stimuli" / "stroop_practice"

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
if cfg.MODE == "test":
    MAPPING_INTERVAL_COUNTS = 2                  # mapping practice contains ~ intervals
    MAPPING_III = 1000                           # ~ms between two consequtive mapping practice intervals
    STROOP_INTERVAL_COUNTS = 2              # stroop practice contains ~ intervals
    STROOP_III = 1000                       # ~ms between two consequtive stroop practice intervals
    GSS_PRACTICE_INTERVAL_COUNTS = 3        # gss practice contains ~ intervals (actually not used)
    GSS_PRACTICE_III = 1000                 # ~ms between two consequenive gss practice intervals
    GSS_MAIN_INTERVAL_COUNTS = 3            # gss main contains 3 sections, each section contains ~ intervals
    GSS_MAIN_III = 2000                     # ~ms between two consequetive gss main intervals (set longer for the participants to read the feedback)
    MAX_BLOCK_INFO_DISPLAY_DURATION = 3000  # display the block info (accuracy / speed / varying) for ~ms (if not pressed [SPACE])

# ACTUAL mode (for actual task)
else:
    MAPPING_INTERVAL_COUNTS = 3
    MAPPING_III = 3000
    STROOP_INTERVAL_COUNTS = 3
    STROOP_III = 3000
    GSS_PRACTICE_INTERVAL_COUNTS = 3
    GSS_PRACTICE_III = 3000
    GSS_MAIN_INTERVAL_COUNTS = 5
    GSS_MAIN_III = 5000
    MAX_BLOCK_INFO_DISPLAY_DURATION = 10000
