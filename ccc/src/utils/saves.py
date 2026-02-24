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


TASK_NAME = "ccc"

_current_results_path: Path | None = None

NA_STR = "NA"


COLUMNS = [
    "task",                 # task name (abbreviation)
    "participant_id",       # participant ID (input at the start of task)
    "dominant_hand",        # participant's dominant hand (input at the start of task) (left / right)
    "hand_used",            # hand used during task (input at the start of task) (left / right)
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
    "global_start_time",    # experiment start time (ISO format)
    "global_end_time",      # experiment end time (ISO format)
    
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


def _version_suffix(counter: int) -> str:
    """
    Build version suffix:
    - 2..9  -> v02..v09
    - >=10  -> v10, v11, ...
    """
    if counter < 10:
        return f"v0{counter}"
    return f"v{counter}"


def create_save() -> None:
    """
    Create a new results CSV for the current participant, writing the header row.

    Filename format:
    - {PID}_{TASK_NAME}_results_YYYY_MM_DD.csv
    - If the file exists, increment with version suffix:
      {PID}_{TASK_NAME}_results_v02_YYYY_MM_DD.csv, v03, ..., v10, ...

    :return: None
    """
    global _current_results_path

    base_path, date_str = _results_csv_path()
    if not base_path.exists():
        csv_path = base_path
    else:
        base_pid = cfg.PID or "unknown"
        counter = 2
        while True:
            suffix = _version_suffix(counter)
            stem = f"{base_pid}_{TASK_NAME}_results_{suffix}_{date_str}.csv"
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
    record = {
        "task": TASK_NAME,
        "participant_id": cfg.PID,
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
        "global_start_time": cfg.START_TIME,
        "global_end_time": cfg.GLOBAL_END_TIME,
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


def finalize_save() -> None:
    """
    Backfill global start/end timestamps for all rows in the active results file.
    """
    if _current_results_path is not None:
        csv_path = _current_results_path
    else:
        csv_path, _ = _results_csv_path()

    if not csv_path.exists():
        return

    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.DictReader(rf)
        rows = list(reader)

    for row in rows:
        row["global_start_time"] = cfg.START_TIME or NA_STR
        row["global_end_time"] = cfg.GLOBAL_END_TIME or NA_STR

    with csv_path.open("w", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Results file finalized at {csv_path}")
