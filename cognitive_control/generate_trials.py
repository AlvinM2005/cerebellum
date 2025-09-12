import random
from stimuli import *
from meta_parameters import *

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
practice1_1_trials = create_m_sm_trials(0, PRACTICE1_1_NUM_BLUE, PRACTICE1_1_NUM_NOGO, "practice1_1")
practice1_2_trials = create_m_sm_trials(0, PRACTICE1_2_NUM_BLUE, PRACTICE1_2_NUM_NOGO, "practice1_2")
block1_trials = create_m_sm_trials(0, BLOCK1_NUM_BLUE, BLOCK1_NUM_NOGO, "block1")
practice2_1_trials = create_m_sm_trials(PRACTICE2_1_NUM_RED, 0, PRACTICE2_1_NUM_NOGO, "practice2_1")
practice2_2_trials = create_m_sm_trials(PRACTICE2_2_NUM_RED, 0, PRACTICE2_2_NUM_NOGO, "practice2_2")
block2 = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "block2")
block2_trials = create_m_sm_trials(BLOCK2_NUM_RED, 0, BLOCK2_NUM_NOGO, "block2")

# Sensorimotor
practice3_1_trials = create_m_sm_trials(PRACTICE3_1_NUM_RED, PRACTICE3_1_NUM_BLUE, PRACTICE3_1_NUM_NOGO, "practice3_1")
practice3_2_trials = create_m_sm_trials(PRACTICE3_2_NUM_RED, PRACTICE3_2_NUM_BLUE, PRACTICE3_2_NUM_NOGO, "practice3_2")
block3_trials = create_m_sm_trials(BLOCK3_NUM_RED, BLOCK3_NUM_BLUE, BLOCK3_NUM_NOGO, "block3")
block4_trials = create_m_sm_trials(BLOCK4_NUM_RED, BLOCK4_NUM_BLUE, BLOCK4_NUM_NOGO, "block4")

# Contextual
def create_contextual_trials(num_actual, num_nogo, phase, version):
    CONTEXTUAL_STIMULI_ACTUAL = []
    CONTEXTUAL_STIMULI_NOGO = []
    contextual_stimuli = ContextualStimuli(version)
    CONTEXTUAL_STIMULI = contextual_stimuli.CONTEXTUAL_STIMULI

    for e in CONTEXTUAL_STIMULI:
        if e[2] == "actual":
            CONTEXTUAL_STIMULI_ACTUAL.append(e)
        elif e[2] == "no_go":
            CONTEXTUAL_STIMULI_NOGO.append(e)

    assert len(CONTEXTUAL_STIMULI_ACTUAL) >= num_actual
    assert len(CONTEXTUAL_STIMULI_NOGO) >= num_nogo
    picked_actual = random.sample(CONTEXTUAL_STIMULI_ACTUAL, num_actual)
    picked_nogo = random.sample(CONTEXTUAL_STIMULI_NOGO, num_nogo)
    trials = picked_actual + picked_nogo
    random.shuffle(trials)
    for e in trials:
        e.append(phase)
        time = random.randint(C_MIN_FIXATION_TIME, C_MAX_FIXATION_TIME)
        e.append(time)
    return trials
