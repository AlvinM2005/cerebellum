import random
from stimuli import *
from meta_parameters import *

# Motor / Sensorimotor
def create_m_sm_trials(num_red, num_blue, num_nogo, phase):
    trials = []
    for _ in range(num_red):
        time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
        trials.append([time, RED, phase])
    for _ in range(num_blue):
        time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
        trials.append([time, BLUE, phase])
    for _ in range(num_nogo):
        time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
        trials.append([time, NOGO, phase])
    random.shuffle(trials)
    return trials

# Motor
def generate_motor_trials():
    practice1_1 = create_m_sm_trials(0, PRACTICE1_1_NUM_BLUE, PRACTICE1_1_NUM_NOGO, "practice1_1")
    practice1_2 = create_m_sm_trials(0, PRACTICE1_2_NUM_BLUE, PRACTICE1_2_NUM_NOGO, "practice1_2")
    block1 = create_m_sm_trials(0, BLOCK1_NUM_BLUE, BLOCK1_NUM_NOGO, "block1")

    practice2_1 = create_m_sm_trials(PRACTICE2_1_NUM_RED, 0, PRACTICE2_1_NUM_NOGO, "practice2_1")
    practice2_2 = create_m_sm_trials(PRACTICE2_2_NUM_RED, 0, PRACTICE2_2_NUM_NOGO, "practice2_2")
    block2 = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "block2")

    return practice1_1, practice1_2, block1, practice2_1, practice2_2, block2

practice1_1_trials, practice1_2_trials, block1_trials, practice2_1_trials, practice2_2_trials, block2_trials = generate_motor_trials()

# Sensorimotor
def generate_sensorimotor_trials():
    practice3_1 = create_m_sm_trials(PRACTICE3_1_NUM_RED, PRACTICE3_1_NUM_BLUE, PRACTICE3_1_NUM_NOGO, "practice3_1")
    practice3_2 = create_m_sm_trials(PRACTICE3_2_NUM_RED, PRACTICE3_2_NUM_BLUE, PRACTICE3_2_NUM_NOGO, "practice3_2")

    block3 = create_m_sm_trials(BLOCK3_NUM_RED, BLOCK3_NUM_BLUE, BLOCK3_NUM_NOGO, "block3")

    return practice3_1, practice3_2, block3


practice3_1_trials, practice3_2_trials, block3_trials = generate_sensorimotor_trials()

# Contextual
# ??????