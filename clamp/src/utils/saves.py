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
    "trial",                # trial index
    "block",                # block name
    "trial_type",           # trial type (practice / experimental)
    "condition",            # characteristic(s) specific to the task
    "key_correct",          # keyboard response expected (key name)
    "key_response",         # keyboard response recieved (key name)
    "joy_correct",          # joystick response expected (up / down / left / right)
    "joy_response",         # joystick response recieved (up / down / left / right)
    "correct",              # trial result (1 = correct / 0 = incorrect / None = timeout)
    "reaction_time",        # reaction time (ms)
    "stimulus_path",        # file path (name) to the stimulus
    "start_time",           # start time of the current block (ISO format)
    "end_time",             # end time of the current block (ISO format)

    # ---- clamp task (columns above are kept as in the template) ----
    # Mapping of shared columns in the clamp task:
    #   trial          -> trial number 1..284 (replayed demo trials keep 41..44, see replay_index)
    #   block          -> baseline / clamp_demo / clamp / post_test
    #   trial_type     -> clamped_fb / no_fb
    #   condition      -> tgt{target angle}_rot{rotation}
    #   reaction_time  -> rt: target onset -> hand leaves the start circle (ms)
    #   start_time     -> start of the trial (ISO format)
    #   end_time       -> end of the trial (ISO format, ms precision)
    #   key_*, joy_*, correct, stimulus_path -> NA (not used)
    "mouse_type",           # Optical mouse / Trackpad mouse / Trackball mouse
    "trial_sequence",       # trial file used (v0 .. v50)
    "replay_index",         # 0 = first presentation; 1, 2, ... = replayed demo trials (understanding check)
    "target_angle",         # target angle (deg, counter-clockwise from +x)
    "rotation",             # clamp rotation (deg)
    "hand_fb_angle",        # hand angle when the hand first exceeds distance D (deg, 0-360, absolute)
    "movement_time",        # hand leaves start circle -> hand reaches target ring (ms)
    "search_time",          # start of search -> target onset, includes the hold (ms)
    "reach_feedback",       # good_reach / too_slow
    "key_check",            # key-press attention checks: correct / total (participant level, filled at the end)
    "understanding_check",  # understanding check: correct / total attempts (participant level, filled at the end)
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


def create_save() -> None:
    """
    Create a new results CSV for the current participant, writing the header row.

    Filename format:
    - {PID}_{TASK_NAME}_results_YYYY_MM_DD.csv
    - If the file exists, increment with a two-digit counter:
      {PID}_{TASK_NAME}_results_02_YYYY_MM_DD.csv, 03, ...

    :return: None
    """
    global _current_results_path

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
    logger.info(f"Results file created at {csv_path}")


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
        "trial_type": trial_type,
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
        trial_number: int,
        trial_type: str,
        condition: str,
        reaction_time: float,
        trial_sequence: str,
        replay_index: int,
        target_angle: float,
        rotation: float,
        hand_fb_angle: float,
        movement_time: float,
        search_time: float,
        reach_feedback: str,
    ) -> None:
    """
    Append one clamp-task trial to the participant's results CSV.

    Unlike update_save, the trial number is passed in (replayed demo trials must keep
    their original number, so it cannot be derived by counting rows). Template columns that
    do not apply to the clamp task are written as NA. `start_time` / `end_time` are taken from
    cfg._start_time / cfg._end_time (set by the caller around each trial).

    :param block_name: baseline / clamp_demo / clamp / post_test
    :param trial_number: Trial number (1..284)
    :param trial_type: clamped_fb / no_fb
    :param condition: Task-specific condition label
    :param reaction_time: Target onset -> leaving the start circle (ms)
    :param trial_sequence: Trial file used (e.g. "v12")
    :param replay_index: 0 for the first presentation, 1.. for replayed demo trials
    :param target_angle: Target angle (deg)
    :param rotation: Clamp rotation (deg)
    :param hand_fb_angle: Hand angle at the target ring (deg, 0-360)
    :param movement_time: Leaving the start circle -> reaching the target ring (ms)
    :param search_time: Start of search -> target onset (ms)
    :param reach_feedback: good_reach / too_slow
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
        "trial_type": trial_type,
        "condition": condition,
        "reaction_time": round(reaction_time, 1),
        "start_time": cfg._start_time,
        "end_time": cfg._end_time,
        "mouse_type": cfg.MOUSE_TYPE,
        "trial_sequence": trial_sequence,
        "replay_index": replay_index,
        "target_angle": target_angle,
        "rotation": rotation,
        "hand_fb_angle": round(hand_fb_angle, 3),
        "movement_time": round(movement_time, 1),
        "search_time": round(search_time, 1),
        "reach_feedback": reach_feedback,
    }

    # Fill empty entries with "NA" for CSV consistency.
    normalized_record = {}
    for k in COLUMNS:
        v = record.get(k, "")
        normalized_record[k] = NA_STR if (v is None or v == "") else v

    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        csv.DictWriter(wf, fieldnames=COLUMNS).writerow(normalized_record)

    logger.info("Results file updated")


def finalize_save(key_check: str, understanding_check: str) -> None:
    """
    Write the participant-level checks into every row of the results CSV.

    key_check and understanding_check are only known at the end of the task, so
    update_save_clamp leaves them as NA and this function fills them in afterwards.

    :param key_check: Key-press attention checks, "correct/total" (e.g. "4/5")
    :param understanding_check: Understanding check, "correct/attempts" (e.g. "1/2")
    """
    csv_path = _current_results_path if _current_results_path is not None else _results_csv_path()[0]
    if not csv_path.exists():
        return

    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        rows = list(csv.DictReader(rf))

    for row in rows:
        row["key_check"] = key_check
        row["understanding_check"] = understanding_check

    tmp_path = csv_path.with_suffix(".csv.tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(csv_path)

    logger.info(f"Participant-level checks saved: key_check={key_check} | understanding_check={understanding_check}")
