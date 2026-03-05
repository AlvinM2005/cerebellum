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
practice1_trials = create_m_sm_trials(0, 10, 2, "p1")  # 10 blue + 2 catch = 12 trials
block1_trials = create_m_sm_trials(0, BLOCK1_NUM_BLUE, BLOCK1_NUM_NOGO, "b1")
practice2_trials = create_m_sm_trials(10, 0, 2, "p2")  # 10 red + 2 catch = 12 trials
block2 = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "b2")
block2_trials = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "b2")


# Sensorimotor trials are generated within the Sensorimotor class using instance method
