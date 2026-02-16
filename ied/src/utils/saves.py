# ./src/utils/saves.py
"""
Utilities for saving trial-level experiment results to CSV files.
"""

from __future__ import annotations

import csv
import datetime
from pathlib import Path

import utils.config as cfg
from utils.paths import RESULTS_DIR
from utils.logger import get_logger


logger = get_logger("./src/utils/saves")


COLUMNS = [
    "task",
    "participant_id",
    "dominant_hand",
    "hand_used",
    "mode",
    "version",
    "trial",
    "block",
    "type",
    "condition",
    "key_correct",
    "key_response",
    "joy_correct",
    "joy_response",
    "correct",
    "start_time",
    "end_time",
    "global_start_time",
    "global_end_time",
    "correct_count",
    "trial_count",
]


phase_to_condition = {
    "PRACTICE1": "Choose the big circle",
    "PRACTICE2": "Choose the little circle",
    "P1": "Simple Discrimination (SD)",
    "P2": "Simple Reversal (SR)",
    "P3": "Compound Discrimination (CD)",
    "P4": "Compound Reversal (CDR)",
    "P5": "Intra-Dimensional Shift (IDS)",
    "P6": "Intra-Dimensional Reversal (IDR)",
    "P7": "Extra-Dimensional Shift (EDS)",
    "P8": "Extra-Dimensional Reversal (EDR)",
    "P9": "Simple Relearning (SRL)",
}

phase_to_difficulty = {
    "PRACTICE1": "Choose the big circle",
    "PRACTICE2": "Choose the little circle",
    "P1": "SD",
    "P2": "SR",
    "P3": "CD",
    "P4": "CDR",
    "P5": "IDS",
    "P6": "IDR",
    "P7": "EDS",
    "P8": "EDR",
    "P9": "SRL",
}


def _results_path() -> Path:
    if cfg.RESULTS_FILENAME:
        return RESULTS_DIR / cfg.RESULTS_FILENAME
    date_str = cfg.RESULTS_DATE or datetime.datetime.now().strftime("%Y_%m_%d")
    return RESULTS_DIR / f"{cfg.PID}_ied_results_{date_str}.csv"


def _pick_available_filename() -> str:
    date_str = cfg.RESULTS_DATE or datetime.datetime.now().strftime("%Y_%m_%d")
    base_name = f"{cfg.PID}_ied_results_{date_str}.csv"
    base_path = RESULTS_DIR / base_name

    if not base_path.exists():
        return base_name

    index = 2
    while True:
        suffix = f"_{index:02d}.csv"
        candidate = f"{cfg.PID}_ied_results_{date_str}{suffix}"
        if not (RESULTS_DIR / candidate).exists():
            return candidate
        index += 1


def create_save() -> None:
    """Create a new results CSV for a participant with header row."""
    filename = _pick_available_filename()
    cfg.RESULTS_FILENAME = filename
    csv_path = RESULTS_DIR / filename

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)

    logger.info("Results file created at %s", csv_path)


def _phase_to_block(phase: str) -> str:
    if phase == "PRACTICE1":
        return "p1"
    if phase == "PRACTICE2":
        return "p2"
    if phase.startswith("P") and phase[1:].isdigit():
        return f"b{phase[1:]}"
    return phase.lower()


def _block_to_type(block: str) -> str:
    if block in ("p1", "p2"):
        return "practice"
    if block.startswith("b"):
        return "test"
    return "test"


def _normalize_condition(condition: str | None) -> str | None:
    if condition == "Choose the big circle":
        return "big"
    if condition == "Choose the little circle":
        return "small"
    return condition


def update_save(
    phase: str,
    correct: int,
    correct_dir: str | None,
    response_dir: str | None,
    input_source: str | None,
) -> None:
    """Append one trial result to the participant's CSV file."""
    csv_path = _results_path()

    if not csv_path.exists():
        raise FileNotFoundError(f"Results file not found: {csv_path}")

    # Count existing trials (exclude header)
    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_number = len(data_rows) + 1

    # Prepare one record
    block = _phase_to_block(phase)
    condition = _normalize_condition(phase_to_difficulty.get(phase))
    row_type = _block_to_type(block)

    key_correct = None
    key_response = None
    joy_correct = None
    joy_response = None

    if input_source == "keyboard":
        key_correct = correct_dir
        key_response = response_dir
    elif input_source == "joystick":
        joy_correct = correct_dir
        joy_response = response_dir

    record = {
        "task": "ied",
        "participant_id": cfg.PID,
        "dominant_hand": cfg.dominant_hand,
        "hand_used": cfg.hand_used,
        "mode": cfg.MODE,
        "version": cfg.VERSION,
        "trial": next_trial_number,
        "block": block,
        "type": row_type,
        "condition": condition,
        "key_correct": key_correct,
        "key_response": key_response,
        "joy_correct": joy_correct,
        "joy_response": joy_response,
        "correct": correct,
        "start_time": cfg.PHASE_START_TIME,
        "end_time": cfg.PHASE_END_TIME,
        "global_start_time": cfg.START_TIME,
        "global_end_time": cfg.GLOBAL_END_TIME,
        "correct_count": cfg.correct_count,
        "trial_count": cfg.trial_count,
    }

    # Write record in fixed column order
    write_header = not has_header
    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in COLUMNS})

    logger.info("Results file updated")


def finalize_phase(phase: str, phase_end_time: str) -> None:
    """
    Update all rows for the given phase (block) with the final end time.
    """
    csv_path = _results_path()
    if not csv_path.exists():
        return

    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)

    if not rows:
        return

    has_header = rows[0] == COLUMNS
    data_rows = rows[1:] if has_header else rows

    target_block = _phase_to_block(phase)
    updated = []
    for row in data_rows:
        record = dict(zip(COLUMNS, row))
        if record.get("block") == target_block:
            record["end_time"] = phase_end_time
        updated.append([record.get(col, "") for col in COLUMNS])

    with csv_path.open("w", newline="", encoding="utf-8") as wf:
        writer = csv.writer(wf)
        if has_header:
            writer.writerow(COLUMNS)
        writer.writerows(updated)


def finalize_experiment(global_end_time: str) -> None:
    """
    Update all rows with the final global end time.
    """
    csv_path = _results_path()
    if not csv_path.exists():
        return

    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        rows = list(reader)

    if not rows:
        return

    has_header = rows[0] == COLUMNS
    data_rows = rows[1:] if has_header else rows

    updated = []
    for row in data_rows:
        record = dict(zip(COLUMNS, row))
        record["global_end_time"] = global_end_time
        updated.append([record.get(col, "") for col in COLUMNS])

    with csv_path.open("w", newline="", encoding="utf-8") as wf:
        writer = csv.writer(wf)
        if has_header:
            writer.writerow(COLUMNS)
        writer.writerows(updated)
