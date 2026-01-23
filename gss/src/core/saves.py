# ./src/core/saves.py
from pathlib import Path
import csv
import datetime

from utils import config as cfg
from utils.logger import get_logger


logger = get_logger("./src/core/saves")    # create logger


COLUMNS = [
    "participant_id",       # participant id (input at the start of task)
    "version",              # task version determined by participant id
    "trial_number",         # number of trials (starting from 1)
    "phase",                # "mapping practice" / "stroop practice" / "gss practice" / "gss main"
    "condition",            # "mapping practice" / "stroop practice" / "gss practice" / "gss main"
    "difficulty",           # "mapping practice" / "stroop practice": "practice"; "gss practice" / "gss main": "accuracy", "speed", "varying"
    "correct",              # True = correct / False = incorrect
    "reaction time",        # reaction time
    "stimulus_path",        # file path to the stimulus
    "start_time",           # global start time
    "end_time",             # global end time
]


def create_save() -> None:
    """Create a new results CSV for a participant with header row."""
    csv_path = cfg.RESULTS_DIR / f"{cfg.PID}_GSS_results.csv"

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
    
    logger.info(f"Results file created at {csv_path}")


def update_save(phase: str, condition: str, difficulty: str, correct: bool, reaction_time: int, stimulus_path: Path) -> None:
    """Append one trial result to the participant's CSV file."""
    csv_path = cfg.RESULTS_DIR / f"{cfg.PID}_GSS_results.csv"

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
