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

# Contextual
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


def _letter_type(letter):
    return "vowel" if letter in VOWELS else "consonant"


def _is_congruent(letter, case_type):
    # congruent: vowel+lower OR consonant+upper
    return (letter in VOWELS and case_type == "lower") or (
        letter in CONSONANTS and case_type == "upper"
    )


def _build_runs(total, run_count):
    lengths = [1] * run_count
    extra = total - run_count
    for _ in range(extra):
        lengths[random.randrange(run_count)] += 1
    random.shuffle(lengths)
    return lengths


def _build_strict_color_sequence(num_trials):
    if num_trials != 48:
        raise ValueError("Strict mixed contextual sequence currently expects 48 trials per block")

    start_color = random.choice(["pink", "yellow"])
    if start_color == "pink":
        pink_runs = 13
        yellow_runs = 12
    else:
        pink_runs = 12
        yellow_runs = 13

    pink_lengths = _build_runs(24, pink_runs)
    yellow_lengths = _build_runs(24, yellow_runs)

    colors = []
    p_i = 0
    y_i = 0
    current = start_color
    for _ in range(25):
        if current == "pink":
            colors.extend(["pink"] * pink_lengths[p_i])
            p_i += 1
            current = "yellow"
        else:
            colors.extend(["yellow"] * yellow_lengths[y_i])
            y_i += 1
            current = "pink"
    return colors


def _actual_lookup(version):
    contextual_stimuli = ContextualStimuli(version)
    result = {}
    for image, key_correct, trial_type in contextual_stimuli.CONTEXTUAL_STIMULI:
        if trial_type != "actual":
            continue
        letter, color, case_type = IMAGE_META[image]
        result[(letter, color, case_type)] = (image, key_correct)
    return result


def _make_trial(stimulus_image, key_correct, phase, fixation_time, meta):
    return [stimulus_image, key_correct, "actual", phase, fixation_time, meta]


def create_contextual_trials(num_actual, num_nogo, phase, version, color_mode="both", mixed_balanced_switch=False):
    if num_nogo != 0:
        raise ValueError("Contextual task no longer uses no-go trials")

    lookup = _actual_lookup(version)
    pool = []
    for (letter, color, case_type), (image, key_correct) in lookup.items():
        if color_mode in ("pink", "yellow") and color != color_mode:
            continue
        pool.append((letter, color, case_type, image, key_correct))

    trials = []
    for _ in range(num_actual):
        letter, color, case_type, image, key_correct = random.choice(pool)
        meta = {
            "letter": letter,
            "context_color": color,
            "case_type": case_type,
            "phonetic_type": _letter_type(letter),
            "congruency": "congruent" if _is_congruent(letter, case_type) else "incongruent",
            "switch_type": None,
        }
        trials.append(
            _make_trial(
                image,
                key_correct,
                phase,
                random.randint(C_MIN_FIXATION_TIME, C_MAX_FIXATION_TIME),
                meta,
            )
        )

    if mixed_balanced_switch:
        for i in range(len(trials)):
            if i == 0:
                trials[i][5]["switch_type"] = "no_switch"
            else:
                prev_color = trials[i - 1][5]["context_color"]
                curr_color = trials[i][5]["context_color"]
                trials[i][5]["switch_type"] = "switch" if curr_color != prev_color else "no_switch"

    return trials


def create_contextual_mixed_blocks_strict(version):
    lookup = _actual_lookup(version)

    # Global quota across both mixed blocks:
    # each letter appears exactly 3 times for each color x case combination.
    letter_quota = {}
    for letter in LETTERS:
        for color in ("pink", "yellow"):
            for case_type in ("upper", "lower"):
                letter_quota[(letter, color, case_type)] = 3

    def case_from_combo(phonetic, congruency):
        if (phonetic, congruency) in (("vowel", "congruent"), ("consonant", "incongruent")):
            return "lower"
        return "upper"

    def fill_block(phase):
        colors = _build_strict_color_sequence(48)
        switch_types = []
        for i, color in enumerate(colors):
            if i == 0:
                switch_types.append("no_switch")
            else:
                switch_types.append("switch" if color != colors[i - 1] else "no_switch")

        slots = {(color, switch_t): [] for color in ("pink", "yellow") for switch_t in ("switch", "no_switch")}
        for idx, (color, switch_t) in enumerate(zip(colors, switch_types)):
            slots[(color, switch_t)].append(idx)

        # For each color, assign 4 combos x 3 positions for switch and no_switch.
        combo_per_slot = [None] * 48
        for color in ("pink", "yellow"):
            for switch_t in ("switch", "no_switch"):
                indices = slots[(color, switch_t)]
                labels = []
                for phonetic in ("vowel", "consonant"):
                    for congruency in ("congruent", "incongruent"):
                        labels.extend([(color, phonetic, congruency)] * 3)
                random.shuffle(labels)
                for idx, label in zip(indices, labels):
                    combo_per_slot[idx] = label

        trials = []
        for i in range(48):
            color, phonetic, congruency = combo_per_slot[i]
            case_type = case_from_combo(phonetic, congruency)

            if phonetic == "vowel":
                candidates = [l for l in VOWELS if letter_quota[(l, color, case_type)] > 0]
            else:
                candidates = [l for l in CONSONANTS if letter_quota[(l, color, case_type)] > 0]
            if not candidates:
                raise RuntimeError("Unable to satisfy strict mixed-letter balancing constraints")

            letter = random.choice(candidates)
            letter_quota[(letter, color, case_type)] -= 1
            stimulus_image, key_correct = lookup[(letter, color, case_type)]

            meta = {
                "letter": letter,
                "context_color": color,
                "case_type": case_type,
                "phonetic_type": phonetic,
                "congruency": congruency,
                "switch_type": switch_types[i],
            }
            trials.append(
                _make_trial(
                    stimulus_image,
                    key_correct,
                    phase,
                    random.randint(C_MIN_FIXATION_TIME, C_MAX_FIXATION_TIME),
                    meta,
                )
            )

        # Validate per-block constraints.
        assert len(trials) == 48
        assert sum(1 for t in trials if t[5]["context_color"] == "pink") == 24
        assert sum(1 for t in trials if t[5]["context_color"] == "yellow") == 24
        assert sum(1 for t in trials if t[5]["switch_type"] == "switch") == 24
        assert sum(1 for t in trials if t[5]["switch_type"] == "no_switch") == 24
        assert sum(1 for t in trials if t[5]["congruency"] == "congruent") == 24
        assert sum(1 for t in trials if t[5]["congruency"] == "incongruent") == 24
        for color in ("pink", "yellow"):
            assert sum(1 for t in trials if t[5]["context_color"] == color and t[5]["phonetic_type"] == "vowel") == 12
            assert sum(1 for t in trials if t[5]["context_color"] == color and t[5]["phonetic_type"] == "consonant") == 12
            assert sum(1 for t in trials if t[5]["context_color"] == color and t[5]["case_type"] == "upper") == 12
            assert sum(1 for t in trials if t[5]["context_color"] == color and t[5]["case_type"] == "lower") == 12
            for phonetic in ("vowel", "consonant"):
                for congruency in ("congruent", "incongruent"):
                    subset = [
                        t for t in trials
                        if t[5]["context_color"] == color
                        and t[5]["phonetic_type"] == phonetic
                        and t[5]["congruency"] == congruency
                    ]
                    assert len(subset) == 6
                    assert sum(1 for t in subset if t[5]["switch_type"] == "switch") == 3
                    assert sum(1 for t in subset if t[5]["switch_type"] == "no_switch") == 3
        return trials

    block_a = fill_block("b5")
    block_b = fill_block("b6")

    # Validate cross-block letter exposure quota.
    for letter in LETTERS:
        for color in ("pink", "yellow"):
            for case_type in ("upper", "lower"):
                assert letter_quota[(letter, color, case_type)] == 0

    return block_a, block_b
