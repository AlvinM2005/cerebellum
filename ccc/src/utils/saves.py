"""
Per-trial CSV persistence for current CCC task.
"""


import csv
import datetime
from pathlib import Path

import utils.config as cfg
from utils.paths import RESULTS_DIR
from utils.logger import get_logger


logger = get_logger("./src/utils/saves")

TASK_NAME = "ccc"
NA_STR = "NA"
_current_results_path: Path | None = None

COLUMNS = [
    "task",
    "participant_id",
    "language",
    "group",
    "session",
    "dominant_hand",
    "hand_used",
    "mode",
    "mapping",
    "trial",
    "block",
    "trial_type",
    "condition",
    "key_correct",
    "key_response",
    "joy_correct",
    "joy_response",
    "correct",
    "reaction_time",
    "stimulus_path",
    "start_time",
    "end_time",
    "global_start_time",
    "global_end_time",
]


def _today_yyyymmdd() -> str:
    return datetime.datetime.now().strftime("%Y_%m_%d")


def _results_csv_path() -> tuple[Path, str]:
    date_str = _today_yyyymmdd()
    base_pid = cfg.PID or "unknown"
    stem = f"{base_pid}_{TASK_NAME}_results_{date_str}.csv"
    return RESULTS_DIR / stem, date_str


def _version_suffix(counter: int) -> str:
    if counter < 10:
        return f"v0{counter}"
    return f"v{counter}"


def create_save() -> None:
    global _current_results_path

    base_path, date_str = _results_csv_path()
    if not base_path.exists():
        csv_path = base_path
    else:
        base_pid = cfg.PID or "unknown"
        counter = 2
        while True:
            suffix = _version_suffix(counter)
            candidate = RESULTS_DIR / f"{base_pid}_{TASK_NAME}_results_{suffix}_{date_str}.csv"
            if not candidate.exists():
                csv_path = candidate
                break
            counter += 1

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)

    _current_results_path = csv_path
    logger.info(f"Results file created at {csv_path}")


def update_save(
    block_name: str,
    trial_type: str,
    condition: str,
    key_correct: str,
    key_response: str,
    joy_correct: str,
    joy_response: str,
    correct: int | None,
    reaction_time: int | None,
    stimulus_path: str,
) -> None:
    if _current_results_path is not None:
        csv_path = _current_results_path
    else:
        csv_path, _ = _results_csv_path()

    if not csv_path.exists():
        raise FileNotFoundError(f"Results file not found: {csv_path}. Call create_save() first.")

    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        rows = list(csv.reader(rf))
        has_header = bool(rows) and rows[0] == COLUMNS
        data_rows = rows[1:] if has_header else rows
        next_trial_index = len(data_rows) + 1

    src = cfg._input_source
    if src == "key":
        joy_correct = ""
        joy_response = ""
    elif src == "joy":
        if not joy_correct and key_correct:
            joy_correct = key_correct
        if not joy_response and key_response:
            joy_response = key_response
        key_correct = ""
        key_response = ""

    record = {
        "task": TASK_NAME,
        "participant_id": cfg.PID,
        "language": cfg.LANGUAGE or "",
        "group": cfg.GROUP or "",
        "session": cfg.SESSION or "",
        "dominant_hand": cfg.DH,
        "hand_used": cfg.UH,
        "mode": cfg.MODE,
        "mapping": cfg.MAPPING,
        "trial": next_trial_index,
        "block": block_name,
        "trial_type": trial_type,
        "condition": condition,
        "key_correct": key_correct,
        "key_response": key_response,
        "joy_correct": joy_correct,
        "joy_response": joy_response,
        "correct": correct,
        "reaction_time": reaction_time,
        "stimulus_path": stimulus_path,
        "start_time": cfg._start_time,
        "end_time": cfg._end_time,
        "global_start_time": cfg.START_TIME,
        "global_end_time": cfg.GLOBAL_END_TIME,
    }

    normalized = {}
    for key in COLUMNS:
        value = record.get(key, "")
        normalized[key] = NA_STR if value in ("", None) else value

    with csv_path.open("a", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        if not has_header:
            writer.writeheader()
        writer.writerow(normalized)


def finalize_save() -> None:
    if _current_results_path is not None:
        csv_path = _current_results_path
    else:
        csv_path, _ = _results_csv_path()

    if not csv_path.exists():
        return

    with csv_path.open("r", newline="", encoding="utf-8") as rf:
        rows = list(csv.DictReader(rf))

    for row in rows:
        row["global_start_time"] = cfg.START_TIME or NA_STR
        row["global_end_time"] = cfg.GLOBAL_END_TIME or NA_STR

    with csv_path.open("w", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
