# ./src/core/saves.py
"""
Utilities for saving trial-level experiment results to CSV files.

This module handles creation of participant-specific result files and appends one row per completed trial using a fixed column schema.
"""


from pathlib import Path
import csv
import datetime

import utils.config as cfg
from utils.paths import RESULTS_DIR
from utils.logger import get_logger


logger = get_logger("./src/utils/saves")    # create logger


COLUMNS = [
    "task",                 # task name (always "nBack")
    "participant_id",       # participant id (input at the start of task)
    "dominant_hand",       # participant's dominant hand
    "used_hand",   # hand used by participant to respond
    "mode",                 # "actual" or "demo" based on cfg.MODE
    "version",              # task version (always 1)
    "trial",                # number of trials (starting from 1)
    "block",                # block identifier (p1, p2... for practice; b1, b2... for test)
    "type",                 # "practice" / "experimental"
    "condition",            # "1_back" / "2_back" / "3_back"
    "key_correct",          # correct response
    "key_response",         # participant's response
    "joy_correct",          # joystick correct response (placeholder, always NA)
    "joy_response",         # joystick response (placeholder, always NA)
    "correct",              # 1 if correct, 0 if incorrect
    "reaction_time",        # reaction time
    "start_time",           # global start time
    "end_time",             # global end time
    "signal_detection",     # "hit" / "miss" / "false_alarm" / "correct_rejection"
    "letter_presented",     # letter presented (stimulus file name)
]


def create_save() -> None:
    """
    Create a new results CSV for the current participant, writing the header row if the file does not exist.

    File path rules:
    - Output directory: RESULTS_DIR
    - File name pattern: "{cfg.PID}_nBack_results_YYYY_MM_DD.csv"
    - If file exists, creates a versioned file: "{cfg.PID}_v2_nBack_results_YYYY_MM_DD.csv", "_v3", etc.

    Side effects:
    - Creates a CSV file if missing.
    - Writes a single header row using COLUMNS.
    - Updates cfg.PID if a version suffix is added (e.g., "amanda023" -> "amanda023_v2")

    :return: None
    """
    base_pid = cfg.PID
    # Get current date for filename
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
    csv_path = RESULTS_DIR / f"{base_pid}_nBack_results_{date_str}.csv"

    # If base file exists, find the next available version
    if csv_path.exists():
        version = 2
        while True:
            versioned_pid = f"{base_pid}_v{version}"
            csv_path = RESULTS_DIR / f"{versioned_pid}_nBack_results_{date_str}.csv"
            if not csv_path.exists():
                # Update PID to include version suffix
                cfg.PID = versioned_pid
                logger.info(f"File already exists for {base_pid}. Using versioned ID: {cfg.PID}")
                break
            version += 1

    # Create the file with header
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
    
    logger.info(f"Results file created at {csv_path}")


def update_save(condition: str, difficulty: str, response: str, correct_response: str, result: str, signal_detection: str, reaction_time: int, stimulus_path: str, block_label: str = None) -> None:
    """
    Append one trial result to the participant's results CSV.

    Behavior:
    - Ensures the CSV exists (calls create_save() if missing).
    - Computes the next trial_number by counting existing data rows (excluding header if present).
    - Appends a single row using the fixed column order defined in COLUMNS.

    Field mapping:
    - participant_id: cfg.PID
    - version: cfg.VERSION
    - trial_number: auto-incremented starting from 1
    - start_time: cfg.START_TIME
    - end_time: current timestamp (ISO format)

    :param phase: Trial phase label (e.g., "practice" or "test")
    :type phase: str

    :param condition: Condition label (template may use "NA")
    :type condition: str

    :param difficulty: Difficulty label (template may use "NA")
    :type difficulty: str

    :param trial_type: Trial type: "practice", "test", or "null" (cannot be evaluated)
    :type trial_type: str

    :param response: Participant's response
    :type response: str

    :param correct_response: Correct (expected) response
    :type correct_response: str

    :param result: Whether the response is correct or incorrect
    :type result: str

    :param signal_detection: Signal detection classification: "hit", "miss", "false_alarm", "correct_rejection"
    :type signal_detection: str

    :param reaction_time: Reaction time for this trial (unit determined by caller; typically ms)
    :type reaction_time: int

    :param stimulus_path: Path (name) to the stimulus file presented on this trial
    :type stimulus_path: str

    :return: None
    """    
    # Get current date for filename (same as used in create_save)
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
    csv_path = RESULTS_DIR / f"{cfg.PID}_nBack_results_{date_str}.csv"

    # Ensure file exists with header
    if not csv_path.exists():
        create_save()

    # Count existing trials (exclude header)
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_number = len(data_rows) + 1

    # Prepare one record
    record = {
        "task": "nBack",
        "participant_id": cfg.PID,
        "dominant_hand": cfg.dominant_hand,
        "used_hand": cfg.used_hand,
        "mode": "actual" if cfg.MODE == "actual" else "demo",
        "version": 1,
        "trial": next_trial_number,
        "block": block_label if block_label else cfg.current_block_label,
        "type": "practice" if condition == "practice" else "experimental",
        "condition": difficulty.replace("back", "_back"),
        "key_correct": correct_response,
        "key_response": response,
        "joy_correct": "NA",
        "joy_response": "NA",
        "correct": 1 if result == "correct" else 0,
        "reaction_time": reaction_time,
        "signal_detection": signal_detection,
        "letter_presented": stimulus_path,
        "start_time": cfg.START_TIME,
        "end_time": datetime.datetime.now().isoformat(),
    }

    # Write record in fixed column order
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in COLUMNS})
    
    logger.info(f"Results file updated")
