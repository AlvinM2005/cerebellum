# ./src/utils/config.py
from pathlib import Path


# ---------- Runtime condition assignment ----------
_is_fullscreen: bool = True         # full screen / window mode marker
PID: str | None = None              # participant id
VERSION: int | None = None          # task version (1/2)
START_TIME: str | None = None       # global start time

correct_ind: int | None = None      # correct answer for the current trial
correct_count: int | None = None    # temporary count of continuous correct answers
trial_count: int | None = None      # number of trials made for the current phase
force_quit: bool = False            # if true -> end the task


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
    pass

# ACTUAL mode
else:
    pass


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

# block size (for 4 blocks containing stimuli)
RECT_W = 300
RECT_H = 200
BORDER_PX = 10

# ---------- Instructions settings ----------
INSTRUCTION_COUNT = 28

INSTRUCTIONS = []
for i in range(INSTRUCTION_COUNT):
    INSTRUCTIONS.append(RESOURCES_DIR / "instructions" / f"{i+1}.jpg")

PRACTICE1 = 10
PRACTICE2 = 19
PHASES = 27

# TEST mode (for testing only)
if MODE == "test":
    MIN_READING_TIME = 100      # Minimum reading time to spend on each instruction page

# ACTUAL mode (for actual task)
else:
    MIN_READING_TIME = 1000     # Minimum reading time to spend on each instruction page

# ---------- Stimulus settings ----------
PHASE_COUNT = 9     # total number of phases

PRACTICE1_CORRECT = RESOURCES_DIR / "stimuli" / "ied_circle_big.png"        # correct stimulus for practice 1
PRACTICE1_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_circle_little.png"   # incorrect stimulus for practice 1

PRACTICE2_CORRECT = RESOURCES_DIR / "stimuli" / "ied_circle_little.png"     # correct stimulus for practice 2
PRACTICE2_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_circle_big.png"      # incorrect stimulus for practice 2

if VERSION == 1:
    P1_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"       # correct stimulus for phase 1
    P1_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"     # incorrect stimulus for phase 1

    P2_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"       # correct stimulus for phase 2
    P2_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"     # incorrect stimulus for phase 2

    P3_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"       # correct stimulus for phase 3
    P3_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"     # incorrect stimulus for phase 3
    P3_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l1.png"       # buffer stimulus for phase 3
    P3_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l2.png"       # buffer stimulus for phase 3

    P4_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"       # correct stimulus for phase 4
    P4_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"     # incorrect stimulus for phase 4
    P4_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l1.png"       # buffer stimulus for phase 4
    P4_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l2.png"       # buffer stimulus for phase 4

    P5_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"       # correct stimulus for phase 5
    P5_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"     # incorrect stimulus for phase 5
    P5_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l1.png"       # buffer stimulus for phase 5
    P5_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l2.png"       # buffer stimulus for phase 5

    P6_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s3.png"       # correct stimulus for phase 6
    P6_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s4.png"     # incorrect stimulus for phase 6
    P6_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l3.png"       # buffer stimulus for phase 6
    P6_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l4.png"       # buffer stimulus for phase 6

    P7_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s4.png"       # correct stimulus for phase 7
    P7_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s3.png"     # incorrect stimulus for phase 7
    P7_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l3.png"       # buffer stimulus for phase 7
    P7_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l4.png"       # buffer stimulus for phase 7

    P8_CORRECT = RESOURCES_DIR / "stimuli" / "ied_l5.png"       # correct stimulus for phase 8
    P8_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_l6.png"     # incorrect stimulus for phase 8
    P8_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_s5.png"       # buffer stimulus for phase 8
    P8_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_s6.png"       # buffer stimulus for phase 8

    P9_CORRECT = RESOURCES_DIR / "stimuli" / "ied_l6.png"       # correct stimulus for phase 9
    P9_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_l5.png"     # incorrect stimulus for phase 9
    P9_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_s5.png"       # buffer stimulus for phase 9
    P9_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_s6.png"       # buffer stimulus for phase 9

else:
    P1_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"       # correct stimulus for phase 1
    P1_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"     # incorrect stimulus for phase 1

    P2_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"       # correct stimulus for phase 2
    P2_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"     # incorrect stimulus for phase 2

    P3_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"       # correct stimulus for phase 3
    P3_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"     # incorrect stimulus for phase 3
    P3_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l1.png"       # buffer stimulus for phase 3
    P3_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l2.png"       # buffer stimulus for phase 3

    P4_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"       # correct stimulus for phase 4
    P4_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"     # incorrect stimulus for phase 4
    P4_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l1.png"       # buffer stimulus for phase 4
    P4_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l2.png"       # buffer stimulus for phase 4

    P5_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s1.png"       # correct stimulus for phase 5
    P5_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s2.png"     # incorrect stimulus for phase 5
    P5_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l1.png"       # buffer stimulus for phase 5
    P5_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l2.png"       # buffer stimulus for phase 5

    P6_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s4.png"       # correct stimulus for phase 6
    P6_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s3.png"     # incorrect stimulus for phase 6
    P6_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l3.png"       # buffer stimulus for phase 6
    P6_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l4.png"       # buffer stimulus for phase 6

    P7_CORRECT = RESOURCES_DIR / "stimuli" / "ied_s3.png"       # correct stimulus for phase 7
    P7_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_s4.png"     # incorrect stimulus for phase 7
    P7_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_l3.png"       # buffer stimulus for phase 7
    P7_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_l4.png"       # buffer stimulus for phase 7

    P8_CORRECT = RESOURCES_DIR / "stimuli" / "ied_l6.png"       # correct stimulus for phase 8
    P8_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_l5.png"     # incorrect stimulus for phase 8
    P8_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_s5.png"       # buffer stimulus for phase 8
    P8_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_s6.png"       # buffer stimulus for phase 8

    P9_CORRECT = RESOURCES_DIR / "stimuli" / "ied_l5.png"       # correct stimulus for phase 9
    P9_INCORRECT = RESOURCES_DIR / "stimuli" / "ied_l6.png"     # incorrect stimulus for phase 9
    P9_BUFFER1 = RESOURCES_DIR / "stimuli" / "ied_s5.png"       # buffer stimulus for phase 9
    P9_BUFFER2 = RESOURCES_DIR / "stimuli" / "ied_s6.png"       # buffer stimulus for phase 9

# TEST mode (for testing only)
if MODE == "test":
    ISI_MS = 500                    # inter-stimulus interval (ISI) (ms)
    PRACTICE_TRIAL_REQUIREMENT = 5  # need to complete ~ trials for each practice phase
    CORRECT_REQUIREMENT = 3         # answer ~ trials correct in a row to proceed to the next phase
    FORCE_QUIT_LIMIT = 10           # automatically end the task after ~ trials for one phase (avoid partipants stuck in loop)

# ACTUAL mode (for actual task)
else:
    ISI_MS = 1000
    PRACTICE_TRIAL_REQUIREMENT = 20
    CORRECT_REQUIREMENT = 6
    FORCE_QUIT_LIMIT = 50


# ---------- Feedback settings ----------
FB_CORRECT = RESOURCES_DIR / "feedback" / "feedback_correct.png"        # correct feedback image
FB_INCORRECT = RESOURCES_DIR / "feedback" / "feedback_incorrect.png"    # incorrect feedback image

# TEST mode (for testing only)
if MODE == "test":
    FB_DURATION = 500      # feedback duration
    FE_FB_DURATION = 500   # first-error feedback duration


# ACTUAL mode (for actual task)
else:
    FB_DURATION = 1500
    FE_FB_DURATION = 2000