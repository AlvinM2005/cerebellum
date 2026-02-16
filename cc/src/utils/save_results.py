import csv
import os
from pathlib import Path

import pygame

import utils.config as cfg
from utils.config import VERSION

BASE_DIR = Path(__file__).resolve().parents[2]
RESULTS_DIR = str(BASE_DIR / "results")

index = 0
current_participant_file = None


def InitResultCSV(filename, participant_id):
    results_dir = RESULTS_DIR
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    print(f"Results directory ready: {results_dir}")


def SaveResultsToCsv(filename, participant_id, all_results, global_start_time, global_end_time):
    global index, current_participant_file

    results_dir = RESULTS_DIR
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    if current_participant_file is None or not current_participant_file.startswith(participant_id):
        base_filename = f"{participant_id}_CC_{filename}"
        actual_filename = base_filename
        output_path = os.path.join(results_dir, actual_filename)
        counter = 2
        while os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            name_part = base_filename.rsplit(".", 1)[0]
            ext_part = base_filename.rsplit(".", 1)[1] if "." in base_filename else "csv"
            actual_filename = f"{name_part}_{counter}.{ext_part}"
            output_path = os.path.join(results_dir, actual_filename)
            counter += 1
        current_participant_file = actual_filename
    else:
        actual_filename = current_participant_file
        output_path = os.path.join(results_dir, actual_filename)

    fieldnames = [
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
        "fixation_key_response",
        "stimulus_key_response",
        "isi_key_response",
        "joy_correct",
        "joy_response",
        "fixation_joy_response",
        "stimulus_joy_response",
        "isi_joy_response",
        "correct",
        "reaction_time",
        "start_time",
        "end_time",
        "global_start_time",
        "global_end_time",
        "error_type",
    ]

    fixation_key = key_to_str(all_results.get("fixation_key_response"))
    stimulus_key = key_to_str(all_results.get("stimulus_key_response"))
    isi_key = key_to_str(all_results.get("isi_key_response"))
    fixation_joy = all_results.get("fixation_joy_response") or ""
    stimulus_joy = all_results.get("stimulus_joy_response") or ""
    isi_joy = all_results.get("isi_joy_response") or ""

    key_response = stimulus_key or fixation_key or isi_key or ""
    joy_response = stimulus_joy or fixation_joy or isi_joy or ""

    input_source = all_results.get("input_source") or cfg._input_source

    if input_source == "key" or key_response:
        fixation_joy = ""
        stimulus_joy = ""
        isi_joy = ""
        joy_response = ""
        joy_correct = ""
        key_correct = key_to_str(all_results.get("key_correct")) or ""
    elif input_source == "joy" or joy_response:
        fixation_key = ""
        stimulus_key = ""
        isi_key = ""
        key_response = ""
        key_correct = ""
        joy_correct = all_results.get("joy_correct") or ""
    else:
        key_correct = key_to_str(all_results.get("key_correct")) or ""
        joy_correct = all_results.get("joy_correct") or ""

    block = all_results["block"]
    trial_type = "practice" if str(block).startswith("p") else "experimental"
    is_catch = bool(all_results.get("is_catch"))
    condition_task = all_results["condition"]
    condition = f"{condition_task}-{'catch' if is_catch else 'actual'}"
    task = "ccc" if condition_task == "contextual" else "ccs"
    mode = "actual" if cfg.MODE == "actual" else "demo"

    trial_value = all_results.get("trial_number", index + 1)

    row = {
        "task": task,
        "participant_id": participant_id,
        "dominant_hand": cfg.DH or "",
        "hand_used": cfg.UH or "",
        "mode": mode,
        "version": cfg.VERSION if cfg.VERSION is not None else VERSION,
        "trial": trial_value,
        "block": block,
        "type": trial_type,
        "condition": condition,
        "key_correct": key_correct,
        "key_response": key_response,
        "fixation_key_response": fixation_key or "",
        "stimulus_key_response": stimulus_key or "",
        "isi_key_response": isi_key or "",
        "joy_correct": joy_correct,
        "joy_response": joy_response,
        "fixation_joy_response": fixation_joy,
        "stimulus_joy_response": stimulus_joy,
        "isi_joy_response": isi_joy,
        "correct": 1 if all_results.get("correct") else 0,
        "reaction_time": int(all_results.get("reaction_time_ms", 0) or 0),
        "start_time": all_results.get("block_start_time", ""),
        "end_time": all_results.get("block_end_time", ""),
        "global_start_time": cfg.START_TIME or global_start_time or "",
        "global_end_time": cfg._end_time or global_end_time or "",
        "error_type": all_results.get("error_type") or "",
    }

    with open(output_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if os.path.getsize(output_path) == 0:
            writer.writeheader()
        writer.writerow(row)

    index += 1


def key_to_str(key):
    if key is None:
        return None
    if key == pygame.K_v:
        return "v"
    if key == pygame.K_m:
        return "m"
    if key == pygame.K_d:
        return "d"
    if key == pygame.K_k:
        return "k"
    return str(key)
