# Mode
#MODE = "TEST" # For developing purposes
MODE = "ACTUAL" # For actual tasks

# Version
VERSION = 1
'''
[TBD]
'''
# VERSION = 2
'''
[TBD]
'''

# Screen settings
SCREEN_WIDTH = 1516
SCREEN_HEIGHT = 852

# Colors (RGB)
RED_RGB = (255, 72, 72) # FF4848
BLUE_RGB = (72, 197, 255) # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0, 0, 0) # 000000
GRAY_RGB = (128, 128, 128) # 808080
YELLOW_RGB = (255, 255, 0)

# General settings
if MODE == "TEST":
    READ_TIME = 100 # Minimum time spend on each instruction page
else:
    READ_TIME = 100 # Minimum time spend on each instruction page

# Trial settings
SYNCHRONIZED_INTERVAL = 550 # Interval between two stimuli (ms)
MIN_SELF_PACED_INTERVAL = 275 # Minimum interval between two self paced tappings to be considered "correct" (ms)
MAX_SELF_PACED_INTERVAL = 825 # Maximum interval between two self paced tappings to be considered "correct" (ms)
TREMOR_INTERVAL = 50 # Consequtive presses within this interval will be percieved as one (accidenal press due to tremor) (ms)

if MODE == "TEST":
    NUM_SYNCHRONIZED = 5 # Number of synchronized tappings
    NUM_SELF_PACE = 5 # Number of self pace tappings
else:
    NUM_SYNCHRONIZED = 12 # Number of synchronized tappings
    NUM_SELF_PACE = 31 # Number of self pace tappings

# Instruction settings
TOTAL_PAGE = 25 # ~ pages in total
PRACTICE_1 = 6 # practice 1 begins after page ~ [2 trial / v]
BLOCK_1 = 9 # block 1 begins after page ~ [3 trial / v]
BLOCK_2 = 12 # block 2 begins after page ~ [3 trial / v]
PRACTICE_2 = 18 # practice 2 begins after page ~ [2 trial / m]
BLOCK_3 = 21 # block 3 begins after page ~ [3 trial / m]
BLOCK_4 = 24 # block 4 begins after page ~ [3 trial / m]
