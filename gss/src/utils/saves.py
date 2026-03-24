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


TASK_NAME = "gss"

_current_results_path: Path | None = None

NA_STR = "NA"


COLUMNS = [
    "task",                 # task name (abbreviation)
    "participant_id",       # participant ID (input at the start of task)
    "language",             # English / Espanol / NA (derived from PID[0])
    "group",                # group (1-6) from cfg.GROUP
    "session",              # session (1-6) from cfg.SESSION
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
    "global_start_time",    # whole task start time (ISO)
    "global_end_time",      # whole task end time (ISO)
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

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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

    # Unify correct fields to keep key_correct and joy_correct consistent
    # If one is empty, copy from the other; if both present but different, prefer key_correct.
    if (key_correct is None or key_correct == "") and (joy_correct not in (None, "")):
        key_correct = joy_correct
    if (joy_correct is None or joy_correct == "") and (key_correct not in (None, "")):
        joy_correct = key_correct
    if (key_correct not in (None, "")) and (joy_correct not in (None, "")) and (key_correct != joy_correct):
        joy_correct = key_correct

    # Prepare one record
    record = {
        "task": TASK_NAME,
        "participant_id": cfg.PID,
        "language": _derive_language_from_pid(cfg.PID),
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
        "global_start_time": getattr(cfg, "global_start_time", None),
        "global_end_time": getattr(cfg, "global_end_time", None),
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
    
    logger.debug(f"Results file updated")


def _csv_now_iso() -> str:
    return datetime.datetime.now().isoformat()


def finalize_block_end_time() -> None:
    """Fill all NA end_time entries with the current time for the active CSV."""
    global _current_results_path
    csv_path = _current_results_path or _results_csv_path()[0]
    if not csv_path.exists():
        return
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.DictReader(rf)
        rows = list(reader)
        fieldnames = reader.fieldnames or COLUMNS
    changed = False
    now_iso = _csv_now_iso()
    for row in rows:
        if row.get("end_time", "") in ("", NA_STR):
            row["end_time"] = now_iso
            changed = True
    if changed:
        with csv_path.open("w", newline="", encoding="utf-8") as wf:
            writer = csv.DictWriter(wf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def finalize_global_end_time() -> None:
    """Set global_end_time for all rows to the current time for the active CSV."""
    global _current_results_path
    csv_path = _current_results_path or _results_csv_path()[0]
    if not csv_path.exists():
        return
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.DictReader(rf)
        rows = list(reader)
        fieldnames = reader.fieldnames or COLUMNS
    now_iso = _csv_now_iso()
    for row in rows:
        row["global_end_time"] = now_iso
    with csv_path.open("w", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def _derive_language_from_pid(pid: str | None) -> str:
    if not pid or len(str(pid)) == 0:
        return NA_STR
    first = str(pid)[0]
    if first == 'U' or first == 'u':
        return 'English'
    if first == 'M' or first == 'm':
        return 'Espanol'
    return NA_STR

