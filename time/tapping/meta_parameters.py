import os

# Mode
#MODE = "TEST" # For developing purposes
MODE = "ACTUAL" # For actual tasks

# Screen Settings
SCREEN_WIDTH = 1516
SCREEN_HEIGHT = 852

# Colors (RGB)
RED_RGB = (255, 72, 72) # FF4848
BLUE_RGB = (72, 197, 255) # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0, 0, 0) # 000000
GRAY_RGB = (128, 128, 128) # 808080
YELLOW_RGB = (255, 255, 0)

# Audio Settings
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "tapping_task_tone_900Hz_50ms_0.25amp.wav")  # Stimuli file path

# Trial Settings
SYNCHRONIZED_INTERVAL = 600 # Interval between two stimuli (ms)
MINIMUM_SELF_PACED_INTERVAL = 275 # Minimum interval between two self paced tappings to be considered "correct" (ms)
MAXIMUM_SELF_PACED_INTERVAL = 825 # Maximum interval between two self paced tappings to be considered "correct" (ms)

if MODE == "TEST":
    NUM_SYNCHRONIZED_TAPS = 5 # Number of synchronized tappings per trial
    NUM_SELF_PACED_TAPS = 5 # Number of self paced tappings per trial
else:
    NUM_SYNCHRONIZED_TAPS = 12 # Number of synchronized tappings per trial
    NUM_SELF_PACED_TAPS = 31 # Number of self paced tappings per trial
