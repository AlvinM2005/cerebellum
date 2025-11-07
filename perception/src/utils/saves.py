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
    save_path = cfg.RESULTS_DIR / f"{participant_id}_TIM_results.csv"
    final_save_path = cfg.RESULTS_DIR / f"{participant_id}_TIM_final_results.csv"
    if not save_path.exists():
        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant_id", "trial_number", "block", "condition",
                "version", "key_correct",
                "key_response", "correct", "error_type",
                "PSE", "comparison", "T_U", "T_I", "Acuity (Sigma)", "accuracy", "response_time", "start_time", "end_time"
            ])
    if not final_save_path.exists():
        with open(final_save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant_id", "block", "condition",
                "version", "PSE", "comparison", "T_U", "T_I", "Acuity (Sigma)", "final_accuracy", "response_time", "start_time", "end_time"
            ])
    return save_path, final_save_path


def update_save(
    participant_id: str,
    block: str,
    condition: str,
    key_correct: str | None,
    key_response: str | None,
    pse: str,
    comp: str,
    t_u: str,
    t_i: str,
    acuity: str,
    accuracy: str,
    response_time: str,
    start_time: datetime.datetime,
) -> None:
    """
    Append one trial result to the participant's CSV file.
    - participant_id: current participant
    - block: e.g. "practice1", "block3"
    - condition: "duration / loudness"
    - version: VERSION
    - difficulty: harder, easier, same
    - key_correct: "d"/"k"
    - key_response: "d"/"k"
    - start_time: trial start time (datetime)
    """
    save_path = cfg.RESULTS_DIR / f"{participant_id}_TIM_results.csv"
    final_save_path = cfg.RESULTS_DIR / f"{participant_id}_TIM_final_results.csv"

    # determine next trial_number
    trial_number = 1
    if save_path.exists():
        with open(save_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) > 1:  # header + at least one line
                last_line = lines[-1].strip().split(",")
                trial_number = int(last_line[1]) + 1

    # correct
    if key_correct == key_response:
        correct_flag = 1
        error_type = ""
    else:
        correct_flag = 0
        error_type = "response_error"
    
    if cfg.VERSION == 1:
        # key_correct recording
        if key_correct == "shorter / quieter":
            key_correct_record = "d"
        elif key_correct == "longer / louder":
            key_correct_record = "k"
        else:
            key_correct_record = ""
        # key_response recording
        if key_response == "shorter / quieter":
            key_response_record = "d"
        elif key_response == "longer / louder":
            key_response_record = "k"
        else:
            key_response_record = ""
    elif cfg.VERSION == 2:
        # key_correct recording
        if key_correct == "longer / louder":
            key_correct_record = "d"
        elif key_correct == "shorter / quieter":
            key_correct_record = "k"
        else:
            key_correct_record = ""
        # key_response recording
        if key_response == "longer / louder":
            key_response_record = "d"
        elif key_response == "shorter / quieter":
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
            condition,
            cfg.VERSION,
            key_correct_record,
            key_response_record,
            correct_flag,
            error_type,
            pse,
            comp,
            t_u,
            t_i,
            acuity,
            accuracy,
            response_time,
            start_time,
            end_time,
        ])
    if (trial_number == 60) | (trial_number == 120):
        with open(final_save_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                participant_id,
                block,
                condition,
                cfg.VERSION,
                pse,
                comp,
                t_u,
                t_i,
                acuity,
                accuracy,
                response_time,
                start_time,
                end_time,
            ])

