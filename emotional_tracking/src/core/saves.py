# ./src/core/saves.py
"""
Utilities for saving trial-level experiment results to CSV files.

This module handles creation of participant-specific result files and appends one row per completed trial using a fixed column schema.
"""


from pathlib import Path
import csv
import datetime
import json

import utils.config as cfg
from utils.paths import RESULTS_DIR
from utils.logger import get_logger


logger = get_logger("./src/core/saves")    # create logger


COLUMNS = [
    "task",
    "participant_id",       # participant id (input at the start of task)
    "dominant_hand",        # participant's dominant hand
    "hand_used",            # participant's less affected hand
    "mode",
    "mapping",
    "trial",                # number of trials (starting from 1)
    "block",                # "practice" or "test"
    "block_type",
    "condition",            # baseline or contextual
    "key_correct",
    "key_response", 
    "joy_correct",
    "joy_response",
    "correct",              # "correct" / "incorrect" / "timeout"
    "stimulus_path",        # file path (name) to the stimulus
    "start_time",           # global start time
    "end_time",             # global end time
    "time",
    "x_pos",
    "y_pos",
]

def create_save() -> None:
    """
    Create a new results CSV for the current participant, writing the header row if the file does not exist.

    File path rules:
    - Output directory: RESULTS_DIR
    - File name pattern: "cfg.{cfg.PID}_template_results.csv" (TODO: replace "template" with actual project name)

    Side effects:
    - Creates a CSV file if missing.
    - Writes a single header row using COLUMNS.

    :return: None
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    filename = f"{cfg.PID}_ET_results_{datetime.datetime.now().strftime('%Y_%m_%d')}.csv"
    csv_path = RESULTS_DIR / filename

    version = 1
    while csv_path.exists():
        version += 1
        filename = f"{cfg.PID}_ET_results_{datetime.datetime.now().strftime('%Y_%m_%d')}_v{version:02d}.csv"
        csv_path = RESULTS_DIR / filename
    
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
    
    logger.info(f"Results file created at {csv_path}")
    cfg.RESULTS_FILE = filename


def _list_cell(values, decimals: int | None = None) -> str:
    """Serialise a sequence of numbers as a JSON list (e.g. "[0.1, 0.25]") so it fits in one CSV cell."""
    if decimals is None:
        return json.dumps([int(v) for v in values])
    return json.dumps([round(float(v), decimals) for v in values])


# TODO: Modify saved items based on needs

def update_save(        
        correct: bool,
        stimulus_path: str,
        starttime: datetime,
        endtime: datetime,
        type: str,
        block: str,
        time: list,
        x_pos: list,
        y_pos: list,
        key_corr: str,
        key_resp: str,
        joy_corr: str,
        joy_resp: str,) -> None:
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
        "dominant_hand": cfg.DH,
        "hand_used": cfg.UH,
        "mode": cfg.MODE,
        "mapping": cfg.stimulus_set,
        "trial": next_trial_number,
        "block": block,
        "block_type": type,
        "condition": "baseline",
        "key_correct": key_corr,
        "key_response": key_resp, 
        "joy_correct": joy_corr,
        "joy_response": joy_resp,
        "correct": correct,
        "stimulus_path": stimulus_path,
        "start_time": starttime,
        "end_time": endtime,
        "time": _list_cell(time),
        "x_pos": _list_cell(x_pos, decimals=4),
        "y_pos": _list_cell(y_pos, decimals=4),
    }

    # Write record in fixed column order
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in COLUMNS})
    
    logger.info(f"Results file updated")