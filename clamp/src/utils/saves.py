# ./src/core/saves.py
"""
Centralized utilities for persisting per-trial experiment outcomes.
"""


import csv
import datetime
from pathlib import Path

import utils.config as cfg
from utils.paths import RESULTS_DIR
from utils.logger import get_logger


logger = get_logger("./src/utils/saves")    # create logger


TASK_NAME = "clamp"

_current_results_path: Path | None = None
_current_trajectories_path: Path | None = None

TRAJECTORY_COLUMNS = [
    "participant_id",       # same as in the results CSV
    "trial",                # same as trial in the results CSV
    "replay_index",         # same as replay_index in the results CSV (clamp_demo only, empty otherwise)
    "block",                # same as block in the results CSV
    "frame",                # frame counter within the trial, starts at 1
    "time_ms",              # ms since the start of the trial (start of the search phase)
    "trial_state",          # search / hold / target / reach / feedback
    "hand_angle",           # instantaneous hand direction of this frame (deg, 0-360, counter-clockwise from +x); empty if the hand is exactly at the start
    "hand_end_x",           # real hand (mouse-controlled) x relative to the start position (px)
    "hand_end_y",           # real hand (mouse-controlled) y relative to the start position (px, positive = up)
    "cursor_x",             # drawn cursor x relative to the start (px); empty if no cursor is drawn
    "cursor_y",             # drawn cursor y relative to the start (px, positive = up); empty if no cursor is drawn
]

NA_STR = "NA"


COLUMNS = [
    "task",                 # task name (abbreviation)
    "participant_id",       # participant ID (input at the start of task)
    "language",             # English / Espanol / NA (derived from first char of PID)
    "group",                # group (1..6)
    "session",              # session (1..6)
    "dominant_hand",        # participant's dominant hand (left / right)
    "hand_used",            # hand used during task (left / right)
    "mode",                 # task mode (demo / full)
    "mapping",              # task mapping (1 / 2)
    "mouse_type",           # Optical mouse / Trackpad mouse / Trackball mouse
    "trial",                # trial index
    "replay_index",         # clamp_demo only: 0 = first presentation, 1, 2, ... = replays after a wrong understanding check (empty otherwise)
    "block",                # block name
    "CN",                   # clamp task: cycle number within the block (empty for clamp_demo)
    "TN",                   # clamp task: trial number within the block
    "phase",                # clamp task: early / late window within the block (empty otherwise)
    "cursor_feedback",      # cursor feedback type (clamp task: veridical_fb / clamped_fb / no_fb)
    "condition",            # characteristic(s) specific to the task
    "target_angle",         # target angle (deg, counter-clockwise from +x)
    "clamp_offset",          # clamp rotation (deg; + = counter-clockwise, - = clockwise)
    "clamp_direction",      # CCW / CW (clamp_demo and clamp only, empty otherwise)
    "good_reach",           # 1 = neither too_slow nor too_far, else 0
    "too_slow",             # 1 = movement_time above TOO_SLOW_TIME, else 0
    "too_far",              # 1 = |error| at or above TOO_FAR_ERROR, else 0
    "search_time",          # start of search -> target onset, includes the hold (ms)
    "reaction_time",        # reaction time (ms)
    "movement_time",        # hand leaves start circle -> hand reaches target ring (ms)
    "hand_angle",           # circular mean of the hand direction over the move-phase frames within [R_MIN, R_MAX] x D (deg, 0-360, counter-clockwise from +x)
    "error",                # hand_angle - target_angle (deg, wrapped to [-180, 180); + = counter-clockwise, - = clockwise)
    "hand_x_end",           # hand x when it first reaches the target ring, relative to the start, px (positive = right)
    "hand_y_end",           # hand y when it first reaches the target ring, relative to the start, px (positive = up)
    "start_time",           # start time of the current block (ISO format)
    "end_time",             # end time of the current block (ISO format)

    # ---- clamp task (columns above are kept as in the template) ----
    # Mapping of shared columns in the clamp task:
    #   trial            -> trial number over the whole task (1..CLAMP_N_TRIALS; replayed demo trials keep their number, see replay_index)
    #   block            -> no_feedback_baseline / feedback_baseline / clamp_demo / clamp / after_effect
    #   CN / TN / phase  -> cycle number / trial number within the block, early / late window
    #   replay_index     -> clamp_demo only: 0 first presentation, 1, 2, ... replays
    #   cursor_feedback  -> veridical_fb / clamped_fb / no_fb
    #   condition        -> tgt{target angle}_rot{rotation}
    #   reaction_time    -> rt: target onset -> hand leaves the start circle (ms)
    #   start_time       -> start of the trial (ISO format)
    #   end_time         -> end of the trial (ISO format, ms precision)
    # Empty values are written as empty cells in the clamp task.
]


def _today_yyyymmdd() -> str:
    """
    Get today's local date string in YYYY_MM_DD format.

    :return: Date string (YYYY_MM_DD)
    :rtype: str
    """
    return datetime.datetime.now().strftime("%Y_%m_%d")


def _results_csv_path() -> tuple[Path, str]:
    """
    Build the results path for the current participant.

    :return: (csv_path, date_str)
    :rtype: tuple[Path, str]
    """
    date_str = _today_yyyymmdd()

    base_pid = cfg.PID or "unknown"
    stem = f"{base_pid}_{TASK_NAME}_results_{date_str}.csv"
    csv_path = RESULTS_DIR / stem
    return csv_path, date_str


def _trajectories_path_for(results_path: Path) -> Path:
    """Trajectory file path matching a results file ({PID}_clamp_trajectories_[NN_]YYYY_MM_DD.csv)."""
    return results_path.with_name(
        results_path.name.replace(f"_{TASK_NAME}_results_", f"_{TASK_NAME}_trajectories_", 1)
    )


def create_save() -> None:
    """
    Create a new results CSV for the current participant, writing the header row.

    Filename format:
    - {PID}_{TASK_NAME}_results_YYYY_MM_DD.csv
    - If the file exists, increment with a two-digit counter:
      {PID}_{TASK_NAME}_results_02_YYYY_MM_DD.csv, 03, ...

    :return: None
    """
    global _current_results_path, _current_trajectories_path

    # Ensure results directory exists
    RESULTS_DIR.mkdir(exist_ok=True)

    base_path, date_str = _results_csv_path()
    if not base_path.exists():
        csv_path = base_path
    else:
        base_pid = cfg.PID or "unknown"
        counter = 2
        while True:
            stem = f"{base_pid}_{TASK_NAME}_results_{counter:02d}_{date_str}.csv"
            candidate = RESULTS_DIR / stem
            if not candidate.exists():
                csv_path = candidate
                break
            counter += 1

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)

    _current_results_path = csv_path

    # Trajectory file: same name with "results" -> "trajectories" (same counter and date)
    _current_trajectories_path = _trajectories_path_for(csv_path)
    with _current_trajectories_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(TRAJECTORY_COLUMNS)

    logger.info(f"Results file created at {csv_path}")
    logger.info(f"Trajectory file created at {_current_trajectories_path}")


def update_save(
        block_name: str,
        trial_type: str,
        condition: str,
        key_correct: str,
        key_response: str,
        joy_correct: str,
        joy_response: str,
        correct: int | None,
        reaction_time: int | None,
        stimulus_path: str
    ) -> None:
    """
    Append one trial result to the participant's results CSV.

    :param block_name: Bloc name
    :type block_name: str

    :param trrial_type: Trial type (practice / test)
    :type type: str

    :param condition: Characteristic(s) specific to the task
    :type condition: str

    :param key_correct: Keyboard response expected (key name)
    :type key_correct: str

    :param key_response: Keyboard response recieved (key name)
    :type key_response: str

    :param joy_correct: Joystick response expected (up / down / left / right)
    :type joy_correct: str

    :param joy_response: Joystick response recieved (up / down / left / right)
    :type joy_response: str

    :param correct: Trial result (1 = correct / 0 = incorrect / None = timeout)
    :type correct: int

    :param reaction_time: Reaction time (ms)
    :type reaction_time: int

    :param stimulus_path: File path (name) to the stimulus
    :type stimulus_path: str
    """
    if _current_results_path is not None:
        csv_path = _current_results_path
    else:
        csv_path, _ = _results_csv_path()

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Results file not found: {csv_path}. Call create_save() first."
        )

    # Count existing trials (exclude header)
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_index = len(data_rows) + 1

    # Route response fields based on detected input source.
    # Rule: per trial, record either key_* or joy_*, and leave the other pair empty.
    src = cfg._input_source

    if src == "key":
        joy_correct = ""
        joy_response = ""

    elif src == "joy":
        # Prefer explicitly provided joy_*; if empty but key_* is provided, fall back to key_*
        if (joy_correct == "" or joy_correct is None) and (key_correct != "" and key_correct is not None):
            joy_correct = key_correct
        if (joy_response == "" or joy_response is None) and (key_response != "" and key_response is not None):
            joy_response = key_response

        key_correct = ""
        key_response = ""


    # Prepare one record
    # Language: based on first character of PID
    pid_str = str(cfg.PID) if cfg.PID is not None else ""
    first_char = pid_str[:1]
    if first_char in ("U", "u"):
        language = "English"
    elif first_char in ("M", "m"):
        language = "Espanol"
    else:
        language = NA_STR

    record = {
        "task": TASK_NAME,
        "participant_id": cfg.PID,
        "language": language,
        "group": cfg.GROUP,
        "session": cfg.SESSION,
        "dominant_hand": cfg.DH,
        "hand_used": cfg.UH,
        "mode": cfg.MODE,
        "mapping": cfg.MAPPING,
        "trial": next_trial_index,
        "block": block_name,
        "cursor_feedback": trial_type,
        "condition": condition,
        "key_correct": key_correct,
        "key_response": key_response,
        "joy_correct": joy_correct,
        "joy_response": joy_response,
        "correct": correct,
        "reaction_time": reaction_time,
        "stimulus_path": stimulus_path,
        "start_time": cfg._start_time,
        "end_time": cfg._end_time,
    }


    # Fill empty entries with "NA" for CSV consistency.
    normalized_record = {}
    for k in COLUMNS:
        v = record.get(k, "")
        if v is None or v == "":
            normalized_record[k] = NA_STR
        else:
            normalized_record[k] = v

    # Write record in fixed column order
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(normalized_record)
    
    logger.info(f"Results file updated")


# ---------- Clamp task ----------

def _language_from_pid() -> str:
    """
    Derive the language label from the first character of the PID (same rule as update_save).

    :return: English / Espanol / NA
    :rtype: str
    """
    first_char = (str(cfg.PID) if cfg.PID is not None else "")[:1]
    if first_char in ("U", "u"):
        return "English"
    if first_char in ("M", "m"):
        return "Espanol"
    return NA_STR


def update_save_clamp(
        *,
        block_name: str,
        cycle_number: int | None,
        block_trial_number: int,
        phase: str | None,
        trial_number: int,
        cursor_feedback: str,
        condition: str,
        reaction_time: float,
        replay_index: int,
        target_angle: float,
        clamp_offset: float,
        clamp_direction: str | None,
        hand_angle: float,
        hand_x_end: float,
        hand_y_end: float,
        error: float,
        movement_time: float,
        search_time: float,
        good_reach: int,
        too_slow: int,
        too_far: int,
    ) -> None:
    """
    Append one clamp-task trial to the participant's results CSV.

    Unlike update_save, the trial number is passed in (replayed demo trials must keep
    their original number, so it cannot be derived by counting rows). Values that
    do not apply (e.g. CN in clamp_demo) are left empty. `start_time` / `end_time` are taken from
    cfg._start_time / cfg._end_time (set by the caller around each trial).

    :param block_name: no_feedback_baseline / feedback_baseline / clamp_demo / clamp / after_effect
    :param cycle_number: Cycle number within the block (None for clamp_demo)
    :param block_trial_number: Trial number within the block (TN)
    :param phase: early / late / None
    :param trial_number: Trial number over the whole task
    :param cursor_feedback: veridical_fb / clamped_fb / no_fb
    :param condition: Task-specific condition label
    :param reaction_time: Target onset -> leaving the start circle (ms)
    :param replay_index: 0 for the first presentation, 1.. for replayed demo trials
    :param target_angle: Target angle (deg)
    :param clamp_offset: Clamp offset relative to the target (deg, + = CCW)
    :param clamp_direction: CCW / CW for clamp_demo and clamp, None otherwise
    :param hand_angle: Hand angle (deg, 0-360): circular mean over the move-phase distance window
    :param hand_x_end: Hand x when it first reaches the target ring, relative to the start (px, positive = right)
    :param hand_y_end: Hand y when it first reaches the target ring, relative to the start (px, positive = up)
    :param error: hand - target angle (deg, wrapped to +/-180, + = CCW)
    :param movement_time: Leaving the start circle -> reaching the target ring (ms)
    :param search_time: Start of search -> target onset (ms)
    :param good_reach: 1 if neither too_slow nor too_far, else 0
    :param too_slow: 1 if the reach was too slow, else 0
    :param too_far: 1 if the reach was too far, else 0
    """
    csv_path = _current_results_path if _current_results_path is not None else _results_csv_path()[0]

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Results file not found: {csv_path}. Call create_save() first."
        )

    record = {
        "task": TASK_NAME,
        "participant_id": cfg.PID,
        "language": _language_from_pid(),
        "group": cfg.GROUP,
        "session": cfg.SESSION,
        "dominant_hand": cfg.DH,
        "hand_used": cfg.UH,
        "mode": cfg.MODE,
        "mapping": cfg.MAPPING,
        "trial": trial_number,
        "block": block_name,
        "CN": cycle_number,
        "TN": block_trial_number,
        "phase": phase,
        "cursor_feedback": cursor_feedback,
        "condition": condition,
        "reaction_time": round(reaction_time, 1),
        "start_time": cfg._start_time,
        "end_time": cfg._end_time,
        "mouse_type": cfg.MOUSE_TYPE,
        "replay_index": replay_index,
        "target_angle": target_angle,
        "clamp_offset": clamp_offset,
        "clamp_direction": clamp_direction,
        "hand_angle": round(hand_angle, 3),
        "hand_x_end": round(hand_x_end, 2),
        "hand_y_end": round(hand_y_end, 2),
        "error": round(error, 3),
        "movement_time": round(movement_time, 1),
        "search_time": round(search_time, 1),
        "good_reach": good_reach,
        "too_slow": too_slow,
        "too_far": too_far,
    }

    # Empty entries stay empty cells in the clamp task.
    normalized_record = {}
    for k in COLUMNS:
        v = record.get(k, "")
        normalized_record[k] = "" if v is None else v      # empty cell, not the string "NA"

    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        csv.DictWriter(wf, fieldnames=COLUMNS).writerow(normalized_record)

    logger.info("Results file updated")


def save_trajectory(
        *,
        block_name: str,
        trial_number: int,
        replay_index: int | None,
        frames: list,
    ) -> None:
    """
    Append the frame-by-frame trajectory of one trial to the participant's trajectory CSV.

    :param block_name: Block of the trial (same as in the results CSV)
    :param trial_number: Trial number over the whole task
    :param replay_index: clamp_demo replay index (None = empty cell)
    :param frames: One tuple per frame: (frame, time_ms, trial_state, hand_x, hand_y, hand_angle, cursor)
        with positions relative to the start (y positive = up), hand_angle in deg (or None) and cursor = (x, y) or None
    """
    if _current_trajectories_path is not None:
        path = _current_trajectories_path
    else:
        path = _trajectories_path_for(_results_csv_path()[0])
    if not path.exists():
        raise FileNotFoundError(f"Trajectory file not found: {path}. Call create_save() first.")

    rows = []
    for frame, time_ms, state, hx, hy, ang, cur in frames:
        rows.append([
            cfg.PID, trial_number, "" if replay_index is None else replay_index, block_name,
            frame, round(time_ms, 1), state,
            "" if ang is None else round(ang, 3), round(hx, 2), round(hy, 2),
            "" if cur is None else round(cur[0], 2),
            "" if cur is None else round(cur[1], 2),
        ])
    with path.open("a", newline="", encoding="utf-8") as wf:
        csv.writer(wf).writerows(rows)
