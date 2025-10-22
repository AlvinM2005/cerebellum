from __future__ import annotations
from pathlib import Path
import csv
import datetime
import utils.config as cfg

def create_save(participant_id: str) -> Path:
    """
    Create or load a save file for a participant.
    If it already exists, return the existing file path.
    Otherwise, create a new CSV with header row.
    """
    save_path = cfg.RESULTS_DIR / f"{participant_id}_NB_results.csv"
    if not save_path.exists():
        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant_id", "trial_number", "block", "type", "condition",
                "version", "difficulty", "key_correct", "hand",
                "key_response", "correct", "error_type",
                "start_time", "end_time"
            ])
    return save_path


def update_save(
    participant_id: str,
    block: str,
    condition: str,
    difficulty: str,
    key_correct: str | None,
    key_response: str | None,
    start_time: datetime.datetime,
) -> None:
    """
    Append one trial result to the participant's CSV file.
    - participant_id: current participant
    - block: e.g. "practice1", "block3"
    - condition: "0back" / "1back" / "2back"
    - version: VERSION
    - difficulty: same as condition for now
    - key_correct: "d"/"k" or None (for no_go)
    - key_response: "d"/"k" or None (if no response)
    - start_time: trial start time (datetime)
    """
    save_path = cfg.RESULTS_DIR / f"{participant_id}_NB_results.csv"

    # determine next trial_number
    trial_number = 1
    if save_path.exists():
        with open(save_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) > 1:  # header + at least one line
                last_line = lines[-1].strip().split(",")
                trial_number = int(last_line[1]) + 1

    # type
    row_type = "no_go" if key_correct is None else "actual"

    # hand
    if key_correct == "d":
        hand = "left"
    elif key_correct == "k":
        hand = "right"
    else:
        hand = ""

    # correct
    if key_correct == key_response:
        correct_flag = 1
        error_type = ""
    elif key_correct == "nogo":
        correct_flag = 0
        error_type = "no_go_error"
    else:
        correct_flag = 0
        error_type = "response_error"
    
    if cfg.VERSION == 1:
        # key_correct recording
        if key_correct == "different":
            key_correct_record = "d"
        elif key_correct == "same":
            key_correct_record = "k"
        else:
            key_correct_record = ""
        # key_response recording
        if key_response == "different":
            key_response_record = "d"
        elif key_correct == "same":
            key_response_record = "k"
        else:
            key_response_record = ""
    elif cfg.VERSION == 2:
        # key_correct recording
        if key_correct == "same":
            key_correct_record = "d"
        elif key_correct == "different":
            key_correct_record = "k"
        else:
            key_correct_record = ""
        # key_response recording
        if key_response == "same":
            key_response_record = "d"
        elif key_correct == "different":
            key_response_record = "k"
        else:
            key_response_record = ""

    # time stamps
    end_time = datetime.datetime.now().isoformat()

    # append row
    with open(save_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            participant_id,
            trial_number,
            block,
            row_type,
            condition,
            cfg.VERSION,
            difficulty,
            key_correct_record,
            hand,
            key_response_record,
            correct_flag,
            error_type,
            start_time,
            end_time,
        ])
