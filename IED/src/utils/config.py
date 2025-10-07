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
INSTRUCTION_COUNT = None


# ---------- Stimulus settings ----------
PHASE_COUNT = 9                                                     # total number of phases

P1_CORRECT = RESOURCES_DIR / "stimuli" / "p1" / "correct.png"       # correct stimulus for phase 1
P1_INCORRECT = RESOURCES_DIR / "stimuli" / "p1" / "incorrect.png"   # incorrect stimulus for phase 1
P2_CORRECT = RESOURCES_DIR / "stimuli" / "p2" / "correct.png"       # correct stimulus for phase 2
P2_INCORRECT = RESOURCES_DIR / "stimuli" / "p2" / "incorrect.png"   # incorrect stimulus for phase 2
P3_CORRECT = RESOURCES_DIR / "stimuli" / "p3" / "correct.png"       # correct stimulus for phase 3
P3_INCORRECT = RESOURCES_DIR / "stimuli" / "p3" / "incorrect.png"   # incorrect stimulus for phase 3
P4_CORRECT = RESOURCES_DIR / "stimuli" / "p4" / "correct.png"       # correct stimulus for phase 4
P4_INCORRECT = RESOURCES_DIR / "stimuli" / "p4" / "incorrect.png"   # incorrect stimulus for phase 4
P5_CORRECT = RESOURCES_DIR / "stimuli" / "p5" / "correct.png"       # correct stimulus for phase 5
P5_INCORRECT = RESOURCES_DIR / "stimuli" / "p5" / "incorrect.png"   # incorrect stimulus for phase 5
P6_CORRECT = RESOURCES_DIR / "stimuli" / "p6" / "correct.png"       # correct stimulus for phase 6
P6_INCORRECT = RESOURCES_DIR / "stimuli" / "p6" / "incorrect.png"   # incorrect stimulus for phase 6
P7_CORRECT = RESOURCES_DIR / "stimuli" / "p7" / "correct.png"       # correct stimulus for phase 7
P7_INCORRECT = RESOURCES_DIR / "stimuli" / "p7" / "incorrect.png"   # incorrect stimulus for phase 7
P8_CORRECT = RESOURCES_DIR / "stimuli" / "p8" / "correct.png"       # correct stimulus for phase 8
P8_INCORRECT = RESOURCES_DIR / "stimuli" / "p8" / "incorrect.png"   # incorrect stimulus for phase 8
P9_CORRECT = RESOURCES_DIR / "stimuli" / "p9" / "correct.png"       # correct stimulus for phase 9
P9_INCORRECT = RESOURCES_DIR / "stimuli" / "p9" / "incorrect.png"   # incorrect stimulus for phase 9

# TEST mode (for testing only)
if MODE == "test":
    ISI_MS = 500                # inter-stimulus interval (ISI) (ms)
    CORRECT_REQUIREMENT = 3     # continuously answer ~ correct -> proceed to the next section
    FORCE_QUIT_LIMIT = 10       # automatically end the task after ~ trials for one phase (avoid partipants stuck in loop)

# ACTUAL mode (for testing only)
else:
    ISI_MS = 1000
    CORRECT_REQUIREMENT = 6
    FORCE_QUIT_LIMIT = 50



# ---------- Feedback settings ----------
FB_CORRECT = RESOURCES_DIR / "feedback" / "feedback_correct.png"        # correct feedback image
FB_INCORRECT = RESOURCES_DIR / "feedback" / "feedback_incorrect.png"    # incorrect feedback image
FB_DURATION = 1500


# ---------- Runtime condition assignment ----------
_is_fullscreen: bool = True         # full screen / window mode marker
PID: str | None = None              # participant id
VERSION: int | None = None          # task version (1/2)
START_TIME: str | None = None       # global start time

correct_ind: int | None = None      # correct answer for the current trial
correct_count: int | None = None    # temporary count of continuous correct answers
trial_count: int | None = None      # number of trials made for the current phase
force_quit: bool = False            # if true -> end the task
