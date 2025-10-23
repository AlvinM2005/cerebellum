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

# Column definitions for n-back task data output
# Each row represents one trial with comprehensive behavioral and timing data
COLUMNS = [
    "participant_id",      # unique participant identifier
    "trial_number",        # sequential trial number within session
    "block",              # block identifier (e.g., PRACTICE1, BLOCK1, etc.)
    "type",               # trial classification: practice, test, or null
    "stimuli_path",       # filename of stimulus image from stimuli directory
    "condition",          # match/nonmatch based on n-back rule comparison
    "key_correct",        # expected response: none for nonmatch, space for match
    "key_response",       # actual participant response: none or space
    "correct",            # response accuracy: correct or incorrect
    "signal_detection",   # signal detection classification: hit, miss, false_alarm, correct_rejection
    "RT",                 # response time from stimulus onset in milliseconds
    "trialDuration",      # fixed trial duration: stimulus (500ms) + ISI (2500ms) = 3000ms
    "start_time",         # session start timestamp
    "end_time",           # trial completion timestamp
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
    stimuli_path: str,
    condition: str,
    key_correct: str,
    key_response: str,
    correct: str,
    signal_detection: str,
    response_time_ms: Optional[int],
    trial_duration_ms: int,
    start_time: str,
    trial_position: int,
    n_back_level: int,
) -> None:
    """
    Record trial data with comprehensive n-back task variables for analysis.

    Args:
        participant_id: unique participant identifier
        block: block identifier (PRACTICE1, BLOCK1, etc.)
        stimuli_path: filename of presented stimulus
        condition: stimulus classification (match, nonmatch, or null)
        key_correct: expected response based on condition (none/space)
        key_response: actual participant response (none/space)
        correct: response accuracy evaluation (correct/incorrect)
        signal_detection: signal detection theory classification (hit/miss/false_alarm/correct_rejection)
        response_time_ms: latency from stimulus onset to response in ms
        trial_duration_ms: fixed trial duration (3000ms: 500ms stimulus + 2500ms ISI)
        start_time: session initiation timestamp
        trial_position: position within block (1-based indexing)
        n_back_level: current n-back difficulty level (1, 2, or 3)
    """
    csv_path = cfg.RESULTS_DIR / f"{participant_id}_NB_results.csv"

    # Initialize file with headers if not present
    if not csv_path.exists():
        create_save(participant_id)

    # Calculate sequential trial number across entire session
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_number = len(data_rows) + 1

    # Determine trial type based on block name and n-back evaluation criteria
    block_upper = block.upper()
    if "PRACTICE" in block_upper:
        trial_type = "practice"
    elif trial_position <= n_back_level:
        # Initial trials in each block cannot be evaluated due to insufficient history
        trial_type = "null"
    else:
        trial_type = "test"

    # Construct complete trial record with all behavioral and temporal variables
    record = {
        "participant_id": participant_id,
        "trial_number": next_trial_number,
        "block": block,
        "type": trial_type,
        "stimuli_path": stimuli_path,
        "condition": condition,
        "key_correct": key_correct,
        "key_response": key_response,
        "correct": correct,
        "signal_detection": signal_detection,
        "RT": response_time_ms if response_time_ms is not None else "",
        "trialDuration": trial_duration_ms,
        "start_time": start_time,
        "end_time": datetime.datetime.now().isoformat(),
    }

    # Append trial data maintaining consistent column structure
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in COLUMNS})
