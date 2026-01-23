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


logger = get_logger("./src/core/saves")    # create logger


COLUMNS = [
    "participant_id",       # participant id (input at the start of task)
    "version",              # task version determined by participant id
    "trial_number",         # number of trials (starting from 1)
    # TODO: Replace with proper phase configuration
    "phase",                # "practice" or "test"
    # TODO: Replace with proper condition configuration
    "condition",            # None for this template
    "difficulty",           # None for this template
    "correct",              # "correct" / "incorrect" / "timeout"
    "reaction time",        # reaction time
    "stimulus_path",        # file path (name) to the stimulus
    "start_time",           # global start time
    "end_time",             # global end time
    # TODO: Add additional items if necessary
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
    # TODO: Replace [template] with the actual project name
    csv_path = RESULTS_DIR / f"{cfg.PID}_template_results.csv"

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
    
    logger.info(f"Results file created at {csv_path}")


# TODO: Add additional items if necessary (modify input of update_save)
def update_save(phase: str, condition: str, difficulty: str, correct: str, reaction_time: int, stimulus_path: str) -> None:
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
    # TODO: Replace [template] with the actual project name
    csv_path = RESULTS_DIR / f"{cfg.PID}_template_results.csv"

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
        "participant_id": cfg.PID,
        "version": cfg.VERSION,
        "trial_number": next_trial_number,
        "phase": phase,
        "condition": condition,
        "difficulty": difficulty,
        "correct": correct,
        "reaction time": reaction_time,
        "stimulus_path": stimulus_path,
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
