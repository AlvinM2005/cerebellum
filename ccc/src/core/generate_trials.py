from core.stimuli import *
from utils.config import C_AVG_FIXATION_TIME


VOWELS = ("A", "E", "I", "U")
CONSONANTS = ("B", "G", "P", "R")
LETTERS = VOWELS + CONSONANTS

IMAGE_META = {
    A_UPPER_PINK: ("A", "pink", "upper"),
    A_LOWER_PINK: ("A", "pink", "lower"),
    E_UPPER_PINK: ("E", "pink", "upper"),
    E_LOWER_PINK: ("E", "pink", "lower"),
    I_UPPER_PINK: ("I", "pink", "upper"),
    I_LOWER_PINK: ("I", "pink", "lower"),
    U_UPPER_PINK: ("U", "pink", "upper"),
    U_LOWER_PINK: ("U", "pink", "lower"),
    B_UPPER_PINK: ("B", "pink", "upper"),
    B_LOWER_PINK: ("B", "pink", "lower"),
    G_UPPER_PINK: ("G", "pink", "upper"),
    G_LOWER_PINK: ("G", "pink", "lower"),
    P_UPPER_PINK: ("P", "pink", "upper"),
    P_LOWER_PINK: ("P", "pink", "lower"),
    R_UPPER_PINK: ("R", "pink", "upper"),
    R_LOWER_PINK: ("R", "pink", "lower"),
    A_UPPER_YELLOW: ("A", "yellow", "upper"),
    A_LOWER_YELLOW: ("A", "yellow", "lower"),
    E_UPPER_YELLOW: ("E", "yellow", "upper"),
    E_LOWER_YELLOW: ("E", "yellow", "lower"),
    I_UPPER_YELLOW: ("I", "yellow", "upper"),
    I_LOWER_YELLOW: ("I", "yellow", "lower"),
    U_UPPER_YELLOW: ("U", "yellow", "upper"),
    U_LOWER_YELLOW: ("U", "yellow", "lower"),
    B_UPPER_YELLOW: ("B", "yellow", "upper"),
    B_LOWER_YELLOW: ("B", "yellow", "lower"),
    G_UPPER_YELLOW: ("G", "yellow", "upper"),
    G_LOWER_YELLOW: ("G", "yellow", "lower"),
    P_UPPER_YELLOW: ("P", "yellow", "upper"),
    P_LOWER_YELLOW: ("P", "yellow", "lower"),
    R_UPPER_YELLOW: ("R", "yellow", "upper"),
    R_LOWER_YELLOW: ("R", "yellow", "lower"),
}


B1_ORDER = [
    ("I", "upper", "yellow"),
    ("A", "lower", "yellow"),
    ("U", "upper", "pink"),
    ("E", "lower", "pink"),
    ("R", "upper", "pink"),
    ("I", "upper", "pink"),
    ("G", "upper", "pink"),
    ("P", "lower", "yellow"),
    ("P", "upper", "yellow"),
    ("A", "lower", "yellow"),
    ("U", "lower", "yellow"),
    ("R", "lower", "yellow"),
    ("B", "upper", "pink"),
    ("E", "lower", "yellow"),
    ("G", "lower", "yellow"),
    ("B", "upper", "yellow"),
    ("R", "lower", "yellow"),
    ("E", "lower", "pink"),
    ("E", "upper", "pink"),
    ("A", "upper", "pink"),
    ("I", "lower", "yellow"),
    ("U", "upper", "yellow"),
    ("I", "lower", "pink"),
    ("A", "upper", "yellow"),
    ("U", "upper", "pink"),
    ("E", "upper", "yellow"),
    ("A", "lower", "pink"),
    ("U", "lower", "pink"),
    ("I", "lower", "pink"),
    ("P", "upper", "yellow"),
    ("U", "upper", "yellow"),
    ("R", "upper", "pink"),
    ("R", "upper", "yellow"),
    ("B", "upper", "yellow"),
    ("P", "upper", "pink"),
    ("B", "upper", "pink"),
    ("G", "upper", "yellow"),
    ("B", "lower", "pink"),
    ("I", "upper", "yellow"),
    ("G", "lower", "pink"),
    ("G", "lower", "pink"),
    ("E", "lower", "yellow"),
    ("P", "lower", "pink"),
    ("G", "lower", "yellow"),
    ("A", "upper", "pink"),
    ("R", "lower", "pink"),
    ("P", "lower", "pink"),
    ("B", "lower", "yellow"),
]


B2_ORDER = [
    ("B", "lower", "pink"),
    ("I", "upper", "yellow"),
    ("G", "lower", "pink"),
    ("I", "lower", "pink"),
    ("G", "upper", "pink"),
    ("E", "lower", "pink"),
    ("A", "upper", "yellow"),
    ("A", "upper", "pink"),
    ("R", "upper", "pink"),
    ("A", "lower", "pink"),
    ("B", "lower", "yellow"),
    ("P", "lower", "pink"),
    ("E", "upper", "yellow"),
    ("R", "lower", "yellow"),
    ("G", "upper", "pink"),
    ("U", "upper", "pink"),
    ("I", "upper", "pink"),
    ("P", "upper", "pink"),
    ("P", "lower", "yellow"),
    ("A", "upper", "yellow"),
    ("P", "lower", "yellow"),
    ("R", "upper", "yellow"),
    ("E", "upper", "pink"),
    ("E", "upper", "pink"),
    ("U", "lower", "yellow"),
    ("U", "lower", "pink"),
    ("R", "lower", "pink"),
    ("G", "upper", "yellow"),
    ("P", "upper", "pink"),
    ("B", "upper", "yellow"),
    ("U", "upper", "yellow"),
    ("E", "lower", "yellow"),
    ("P", "upper", "yellow"),
    ("U", "lower", "yellow"),
    ("R", "lower", "pink"),
    ("I", "lower", "yellow"),
    ("B", "upper", "pink"),
    ("R", "upper", "yellow"),
    ("I", "upper", "pink"),
    ("G", "lower", "yellow"),
    ("U", "lower", "pink"),
    ("I", "lower", "yellow"),
    ("G", "upper", "yellow"),
    ("E", "upper", "yellow"),
    ("A", "lower", "yellow"),
    ("B", "lower", "yellow"),
    ("A", "lower", "pink"),
    ("B", "lower", "pink"),
]


def _letter_type(letter):
    return "vowel" if letter in VOWELS else "consonant"


def _is_congruent(letter, case_type):
    return (letter in VOWELS and case_type == "lower") or (
        letter in CONSONANTS and case_type == "upper"
    )


def _actual_lookup(version):
    contextual_stimuli = ContextualStimuli(version)
    result = {}
    for image, key_correct, trial_type in contextual_stimuli.CONTEXTUAL_STIMULI:
        if trial_type != "actual":
            continue
        letter, color, case_type = IMAGE_META[image]
        result[(letter, color, case_type)] = (image, key_correct)
    return result


def _build_trial(stimulus_image, key_correct, phase, letter, color, case_type, switch_type):
    return [
        stimulus_image,
        key_correct,
        "actual",
        phase,
        C_AVG_FIXATION_TIME,
        {
            "letter": letter,
            "context_color": color,
            "case_type": case_type,
            "phonetic_type": _letter_type(letter),
            "congruency": "congruent" if _is_congruent(letter, case_type) else "incongruent",
            "switch_type": switch_type,
        },
    ]


def create_contextual_practice_trials(phase, version, color):
    trials = []
    prev_color = None
    for image, key_correct, trial_type in ContextualStimuli(version).CONTEXTUAL_STIMULI:
        if trial_type != "actual":
            continue
        letter, c, case_type = IMAGE_META[image]
        if c != color:
            continue
        switch_type = "no_switch" if prev_color is None else ("switch" if c != prev_color else "no_switch")
        prev_color = c
        trials.append(_build_trial(image, key_correct, phase, letter, c, case_type, switch_type))
    return trials


def _create_contextual_block_trials_from_order(phase, version, order):
    lookup = _actual_lookup(version)
    trials = []
    prev_color = None
    for letter, case_type, color in order:
        stimulus_image, key_correct = lookup[(letter, color, case_type)]
        switch_type = "no_switch" if prev_color is None else ("switch" if color != prev_color else "no_switch")
        prev_color = color
        trials.append(_build_trial(stimulus_image, key_correct, phase, letter, color, case_type, switch_type))
    return trials


def create_contextual_block1_trials(version):
    return _create_contextual_block_trials_from_order("b1", version, B1_ORDER)


def create_contextual_block2_trials(version):
    return _create_contextual_block_trials_from_order("b2", version, B2_ORDER)
