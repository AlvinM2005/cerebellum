# Mode settings
MODE = "TEST"
# MODE = "ACTUAL"

# Screen settings
SCREEN_WIDTH = 1516
SCREEN_HEIGHT = 852

# Colors (RGB)
RED_RGB = (255, 72, 72) # FF4848
BLUE_RGB = (72, 197, 255) # 48C5FF
WHITE_RGB = (236, 236, 236) # ECECEC
BLACK_RGB = (0, 0, 0) # 000000
GRAY_RGB = (128, 128, 128) # 808080

# General settings
if MODE == "TEST":
    READ_TIME = 100 # Minimum time spend on each instruction page
else:
    READ_TIME = 10000 # Minimum time spend on each instruction page
ACCURACY = 0.8 # Accuracy required to pass practices
MAX_REPEAT = 2 # Repeat practice trials for at most (~ + 1) times

# Trial settings [Motor]
M_MIN_FIXATION_TIME = 800 # Minimum fixation time [Motor]
M_MAX_FIXATION_TIME = 1200 # Maximum fixation time [Motor]
if MODE == "TEST":
    M_RESPONSE_TIME = 500 # Response time [Motor]
    M_ISI_TIME = 250 # ISI time [Motor]
else:
    M_RESPONSE_TIME = 2000 # Response time [Motor]
    M_ISI_TIME = 500 # ISI time [Motor]

# Trial settings [Sensorimotor]
SM_MIN_FIXATION_TIME = 800 # Minimum fixation time [Sensorimotor]
SM_MAX_FIXATION_TIME = 1200 # Maximum fixation time [Sensorimotor]
if MODE == "TEST":
    SM_RESPONSE_TIME = 500 # Response time [Sensorimotor]
    SM_ISI_TIME = 250 # ISI time [Sensorimotor]
else:
    SM_RESPONSE_TIME = 2000 # Response time [Sensorimotor]
    SM_ISI_TIME = 500 # ISI time [Sensorimotor]

# Trial settings [Contextual]
C_MIN_FIXATION_TIME = 800 # Minimum fixation time [Contextual]
C_MAX_FIXATION_TIME = 1200 # Maximum fixation time [Contextual]
if MODE == "TEST":
    C_RESPONSE_TIME = 500 # Response time [Contextual]
    C_ISI_TIME = 250 # ISI time [Contextual]
else:
    C_RESPONSE_TIME = 2000 # Response time [Contextual]
    C_ISI_TIME = 500 # ISI time [Contextual]

# Trial nums [Motor]
if MODE == "TEST":
    PRACTICE1_1_NUM_BLUE = 1 # Practice 1 first half (Blue / V)
    PRACTICE1_1_NUM_NOGO = 1 # Practice 1 first half (White / no-go)
    PRACTICE1_2_NUM_BLUE = 1 # Practice 1 second half (Blue / V)
    PRACTICE1_2_NUM_NOGO = 1 # Practice 1 second half (White / no-go)

    BLOCK1_NUM_BLUE = 1 # Block 1 (Blue / V)
    BLOCK1_NUM_NOGO = 1 # Block 1 (White / no-go)

    PRACTICE2_1_NUM_RED = 1 # Practice 2 first half (Red / V)
    PRACTICE2_1_NUM_NOGO = 1 # Practice 2 first half (White / no-go)
    PRACTICE2_2_NUM_RED = 1 # Practice 2 second half (Red / V)
    PRACTICE2_2_NUM_NOGO = 1 # Practice 2 second half (White / no-go)

    BLOCK2_NUM_RED = 1 # Block 2 (Red / V)
    BLOCK2_NUM_NOGO = 1 # Block 2 (White / no-go)
    
else:
    PRACTICE1_1_NUM_BLUE = 5 # Practice 1 first half (Blue / V)
    PRACTICE1_1_NUM_NOGO = 1 # Practice 1 first half (White / no-go)
    PRACTICE1_2_NUM_BLUE = 5 # Practice 1 second half (Blue / V)
    PRACTICE1_2_NUM_NOGO = 1 # Practice 1 second half (White / no-go)

    BLOCK1_NUM_BLUE = 27 # Block 1 (Blue / V)
    BLOCK1_NUM_NOGO = 3 # Block 1 (White / no-go)

    PRACTICE2_1_NUM_RED = 5 # Practice 2 first half (Red / V)
    PRACTICE2_1_NUM_NOGO = 1 # Practice 2 first half (White / no-go)
    PRACTICE2_2_NUM_RED = 5 # Practice 2 second half (Red / V)
    PRACTICE2_2_NUM_NOGO = 1 # Practice 2 second half (White / no-go)

    BLOCK2_NUM_RED = 27 # Block 2 (Red / V)
    BLOCK2_NUM_NOGO = 3 # Block 2 (White / no-go)

# Trial nums [Sensorimotor]
if MODE == "TEST":
    PRACTICE3_1_NUM_RED = 1 # Practice 3 first half (Red / M)
    PRACTICE3_1_NUM_BLUE = 1 # Practice 3 first half (Blue / V)
    PRACTICE3_1_NUM_NOGO = 1 # Practice 3 first half (White / no-go)

    PRACTICE3_2_NUM_RED = 1 # Practice 3 second half (Red / M)
    PRACTICE3_2_NUM_BLUE = 1 # Practice 3 second half (Blue / V)
    PRACTICE3_2_NUM_NOGO = 1 # Practice 3 second half (White / no-go)

    BLOCK3_NUM_RED = 1 # Block 3 (Red / M)
    BLOCK3_NUM_BLUE = 1 # Block 3 (Blue / V)
    BLOCK3_NUM_NOGO = 1 # Block 3 (White / no-go)

else:
    PRACTICE3_1_NUM_RED = 3 # Practice 3 first half (Red / M)
    PRACTICE3_1_NUM_BLUE = 3 # Practice 3 first half (Blue / V)
    PRACTICE3_1_NUM_NOGO = 1 # Practice 3 first half (White / no-go)

    PRACTICE3_2_NUM_RED = 3 # Practice 3 second half (Red / M)
    PRACTICE3_2_NUM_BLUE = 3 # Practice 3 second half (Blue / V)
    PRACTICE3_2_NUM_NOGO = 1 # Practice 3 second half (White / no-go)

    BLOCK3_NUM_RED = 14 # Block 3 (Red / M)
    BLOCK3_NUM_BLUE = 14 # Block 3 (Blue / V)
    BLOCK3_NUM_NOGO = 2 # Block 3 (White / no-go)

# Trial numbers [Contextual]
# ??????

# Instruction pages [Motor]
PRACTICE1_1_PAGE = 4 # Practice 1-1 begins after page 4
PRACTICE1_2_PAGE = 6 # Practice 1-2 begins after page 6
BLOCK1_PAGE = 8 # Block 1 begins after page 8
PRACTICE2_1_PAGE = 12 # Practice 2-1 begins after page 12
PRACTICE2_2_PAGE = 14 # Practice 2-2 begins after page 14
BLOCK2_PAGE = 16 # Block 2 begins after page 16
M_END_PAGE = 17 # Motor tasks ends after page 17

# Instruction pages [Sensorimotor]
PRACTICE3_1_PAGE = 4 # Practice 3-1 begins after page 4
PRACTICE3_2_PAGE = 6 # Practice 3-2 begins after page 6
BLOCK3_PAGE = 8 # Block 3 begins after page 8
SM_END_PAGE = 9 # Sensorimotor tasks ends after page 9

# Instruction pages [Contextual]
PRACTICE4_1_PAGE = 12 # Practice 4-1 begins after page 12
PRACTICE4_2_PAGE = 14 # Practice 4-2 begins after page 14
BLOCK4_PAGE = 17 # Block 4 begins after page 17
C_END_PAGE = 18 # Contextual tasks ends after page 18