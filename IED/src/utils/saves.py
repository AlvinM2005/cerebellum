# ./src/utils/saves.py
from pathlib import Path
import csv
import datetime

from utils import config as cfg
from utils.logger import get_logger


logger = get_logger("./src/utils/saves")    # create logger


COLUMNS = [
    "participant_id",       # participant id (input at the start of task)
    "version",              # task version determined by participant id
    "trial_number",         # number of trials (starting from 1)
    "phase",        # index of phase representing different shifts (1-9)
    "condition",            # names of specific types of shifts
    "difficulty",           # same as "condition"
    "correct",              # 1 = correct / 0 = incorrect
    "correct_count",        # number of correct repsonses made consecutively
    "trial_count",          # number of total trials made in the block
    "start_time",           # global start time
    "end_time",             # global end time
]


phase_to_name = {
    1: "Simple Discrimination (SD)",
    2: "Simple Reversal (SR)",
    3: "Compound Discrimination (CD)",
    4: "Compound Reversal (CDR)",
    5: "Intra-Dimensional Shift (IDS)",
    6: "Intra-Dimensional Reversal (DR)",
    7: "Extra-Dimensional Shift (EDS)",
    8: "Extra-Dimensional Reversal (EDR)",
    9: "Simple Relearning (SRL)",
}


def create_save() -> None:
    """Create a new results CSV for a participant with header row."""
    csv_path = cfg.RESULTS_DIR / f"{cfg.PID}_IED_results.csv"

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
    
    logger.info(f"Results file created at {csv_path}")


def update_save(phase: int, correct: int) -> None:
    """Append one trial result to the participant's CSV file."""
    csv_path = cfg.RESULTS_DIR / f"{cfg.PID}_IED_results.csv"

    # Ensure file exists with header
    if not csv_path.exists():
        create_save(cfg.PID)

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
        "condition": phase_to_name[phase],
        "difficulty": phase_to_name[phase],
        "correct": correct,
        "correct_count": cfg.correct_count,
        "trial_count": cfg.trial_count,
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
