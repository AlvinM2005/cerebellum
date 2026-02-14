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
from ui.pygame_render import _compute_version_from_pid


logger = get_logger("./src/core/saves")    # create logger


COLUMNS = [
    "task",
    "participant_id",       # participant id (input at the start of task)
    "dominant_hand",        # participant's dominant hand
    "used_hand",            # participant's used hand for task
    "mode",                 # actual or demo
    "version",              # 1 or 2
    "trial",                # number of trials (starting from 1)
    "block",                # "practice" or "test"
    "type",                 # practice or experimental
    "condition",            # switching, meaningless, meaningful
    "key_correct",          # Correct answer: d or k
    "key_response",         # User's answer: d or k
    "joy_correct",          # Correct answer: left or right
    "joy_response",         # User's answer: left or right
    "correct",              # 1 = user correct,  0 = user wrong
    "reaction_time",     # reaction time
    "start_time",           # global start time
    "end_time",             # global end time
# Unique variables for task
    "cloze_probability",
    "meaningful",
]

def create_save() -> None:
    """
    Create a new results CSV for the current participant, writing the header row if the file does not exist.

    File path rules:
    - Output directory: RESULTS_DIR
    - File name pattern: "cfg.{cfg.PID}_semantic_decision_results.csv" (TODO: replace "template" with actual project name)

    Side effects:
    - Creates a CSV file if missing.
    - Writes a single header row using COLUMNS.

    :return: None
    """

    filename = f"{cfg.PID}_SD_results_{datetime.datetime.now().strftime('%Y_%m_%d')}.csv"
    csv_path = RESULTS_DIR / filename

    version = 1
    while csv_path.exists():
        version += 1
        filename = f"{cfg.PID}_v{version}_SD_results_{datetime.datetime.now().strftime('%Y_%m_%d')}.csv"
        csv_path = RESULTS_DIR / filename
    
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
    
    logger.info(f"Results file created at {csv_path}")
    cfg.RESULTS_FILE = filename


# TODO: Modify saved items based on needs

def update_save(
        cloze_probability: float,
        correct: bool,
        reaction_time: int,
        starttime: datetime,
        meaningful: bool,
        type: str,
        block: str,
        condition: str,
        key_corr: str,
        key_resp: str,
        joy_corr: str,
        joy_resp: str,
    ) -> None:
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

    :param correct: Whether the response is correct, incorrect, or timeout
    :type correct: str

    :param reaction_time: Reaction time for this trial (unit determined by caller; typically ms)
    :type reaction_time: int

    :param stimulus_path: Path (name) to the stimulus file presented on this trial
    :type stimulus_path: str

    :return: None
    """

    csv_path = RESULTS_DIR / cfg.RESULTS_FILE

    # Count existing trials (exclude header)
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_number = len(data_rows) + 1

    # Prepare one record
    record = {
        "task": cfg.TASK,
        "participant_id": cfg.PID,
        "dominant_hand": cfg.dominant_hand,
        "used_hand": cfg.used_hand,
        "mode": cfg.MODE,
        "version": cfg.VERSION,
        "trial": next_trial_number,
        "block": block,
        "type": type,
        "condition": condition,
        "key_correct": key_corr,
        "key_response": key_resp, 
        "joy_correct": joy_corr,
        "joy_response": joy_resp,
        "correct": correct,
        "reaction_time": reaction_time,
        "start_time": starttime,
        "end_time": datetime.datetime.now().isoformat(),
        "cloze_probability": cloze_probability,
        "meaningful": meaningful,
    }

    # Write record in fixed column order
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in COLUMNS})
    
    logger.info(f"Results file updated")
