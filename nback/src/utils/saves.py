# ./src/core/saves.py
"""
Save and update participant results in CSV format.

- create_save(): initialize a CSV file with headers.
- update_save(): append a new trial record with auto-increment trial_number.
"""

from pathlib import Path
import csv
import datetime
from typing import Optional
from utils import config as cfg

# Fixed column order (must stay consistent between create_save and update_save)
COLUMNS = [
    "participant_id",
    "trial_number",
    "block",
    "type",
    "condition",
    "version",
    "difficulty",
    "correct",
    "response_time_ms",
    "error_type",
    "start_time",
    "end_time",
]


def create_save(participant_id: str) -> None:
    """
    Create a new results CSV for a participant with header row.

    Args:
        participant_id: unique participant identifier
    """
    csv_path = cfg.RESULTS_DIR / f"{participant_id}_NB_results.csv"

    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)


def update_save(
    participant_id: str,
    block: str,
    condition: str,
    correct: str,
    response_time_ms: Optional[int],
    error_type: str,
    start_time: str,
) -> None:
    """
    Append one trial result to the participant's CSV file.

    Args:
        participant_id: participant identifier
        block: current block name
        condition: n-back condition (e.g. "1back", "2back")
        correct: correctness label (e.g. "HIT", "MISS")
        response_time_ms: response latency in ms (None if no response)
        error_type: error category string
        start_time: datetime when trial started
    """
    csv_path = cfg.RESULTS_DIR / f"{participant_id}_NB_results.csv"

    # Ensure file exists with header
    if not csv_path.exists():
        create_save(participant_id)

    # Count existing trials (exclude header)
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_number = len(data_rows) + 1

    # Prepare one record
    record = {
        "participant_id": participant_id,
        "trial_number": next_trial_number,
        "block": block,
        "type": condition,          # aligned with condition
        "condition": condition,
        "version": cfg.VERSION,     # adjust if version constant exists
        "difficulty": condition,    # difficulty == condition
        "correct": correct,
        "response_time_ms": (
            int(response_time_ms) if response_time_ms is not None else ""
        ),
        "error_type": error_type,
        "start_time": start_time,
        "end_time": datetime.datetime.now().isoformat(),
    }

    # Write record in fixed column order
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in COLUMNS})
