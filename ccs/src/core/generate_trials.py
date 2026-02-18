import random

from core.stimuli import *
from utils.config import *


# Motor / Sensorimotor
def create_m_sm_trials(num_red, num_blue, num_nogo, phase):
    trials = []
    for _ in range(num_red):
        time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
        trials.append([time, M_RED, phase])
    for _ in range(num_blue):
        time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
        trials.append([time, M_BLUE, phase])
    for _ in range(num_nogo):
        time = random.randint(M_MIN_FIXATION_TIME, M_MAX_FIXATION_TIME)
        trials.append([time, M_NOGO, phase])
    random.shuffle(trials)
    return trials


# Motor
practice1_1_trials = create_m_sm_trials(0, PRACTICE1_1_NUM_BLUE, PRACTICE1_1_NUM_NOGO, "p1")
practice1_2_trials = create_m_sm_trials(0, PRACTICE1_2_NUM_BLUE, PRACTICE1_2_NUM_NOGO, "p1")
block1_trials = create_m_sm_trials(0, BLOCK1_NUM_BLUE, BLOCK1_NUM_NOGO, "b1")
practice2_1_trials = create_m_sm_trials(PRACTICE2_1_NUM_RED, 0, PRACTICE2_1_NUM_NOGO, "p2")
practice2_2_trials = create_m_sm_trials(PRACTICE2_2_NUM_RED, 0, PRACTICE2_2_NUM_NOGO, "p2")
block2 = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "b2")
block2_trials = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "b2")


# Sensorimotor
practice3_1_trials = create_m_sm_trials(PRACTICE3_1_NUM_RED, PRACTICE3_1_NUM_BLUE, PRACTICE3_1_NUM_NOGO, "p3")
practice3_2_trials = create_m_sm_trials(PRACTICE3_2_NUM_RED, PRACTICE3_2_NUM_BLUE, PRACTICE3_2_NUM_NOGO, "p3")
block3_trials = create_m_sm_trials(BLOCK3_NUM_RED, BLOCK3_NUM_BLUE, BLOCK3_NUM_NOGO, "b3")
block4_trials = create_m_sm_trials(BLOCK4_NUM_RED, BLOCK4_NUM_BLUE, BLOCK4_NUM_NOGO, "b4")
