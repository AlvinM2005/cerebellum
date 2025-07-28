import csv
import os
import pygame
from meta_parameters import *

def save_results_to_csv(filename, participant_id, all_results, global_start_time, global_end_time):
    # Create save directory
    actual_filename = f'{participant_id}_{filename}'

    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    output_path = os.path.join(results_dir, actual_filename)

    # Define field names
    fieldnames = [
        "participant_id",
        "trial_number",
        "block",
        "round",
        "type",
        "fixation_time",
        "condition",
        "version",
        "difficulty",
        "key_correct",
        "hand",
        "fixation_key_response",
        "fixation_reaction_time_ms",
        "stimulus_key_response",
        "stimulus_reaction_time_ms",
        "isi_key_response",
        "isi_reaction_time_ms",
        "correct",
        "error_type",
        "start_time",
        "end_time"
    ]

    # Write to CSV
    with open(output_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for index, trial in enumerate(all_results):
            writer.writerow({
                "participant_id": participant_id,
                "trial_number": index + 1,
                "block": trial["block"],
                "round": 0,
                "type": trial["type"],
                "fixation_time": trial["fixation_time"],
                "condition": trial["condition"],
                "version": VERSION,
                "difficulty": trial["difficulty"],
                "key_correct": key_to_str(trial["key_correct"]),
                "hand": "left" if key_to_str(trial["key_correct"]) == "v" else "right",
                "fixation_key_response": key_to_str(trial["fixation_key_response"]),
                "fixation_reaction_time_ms": trial["fixation_reaction_time_ms"],
                "stimulus_key_response": key_to_str(trial["stimulus_key_response"]),
                "stimulus_reaction_time_ms": trial["stimulus_reaction_time_ms"],
                "isi_key_response": key_to_str(trial["isi_key_response"]),
                "isi_reaction_time_ms": trial["isi_reaction_time_ms"],
                "correct": str(trial["correct"]),
                "error_type": trial["error_type"],
                "start_time": global_start_time,
                "end_time": global_end_time
            })
    
    # Calculate Round
    block_round_limits = {
        "practice1_1": PRACTICE1_1_NUM_BLUE + PRACTICE1_1_NUM_NOGO,
        "practice1_2": PRACTICE1_2_NUM_BLUE + PRACTICE1_2_NUM_NOGO,
        "practice2_1": PRACTICE2_1_NUM_RED + PRACTICE2_1_NUM_NOGO,
        "practice2_2": PRACTICE2_2_NUM_RED + PRACTICE2_2_NUM_NOGO,
        "practice3_1": PRACTICE3_1_NUM_RED + PRACTICE3_1_NUM_BLUE + PRACTICE3_1_NUM_NOGO,
        "practice3_2": PRACTICE3_2_NUM_RED + PRACTICE3_2_NUM_BLUE + PRACTICE3_2_NUM_NOGO,
        "practice4_1": PRACTICE4_1_NUM_ACTUAL + PRACTICE4_1_NUM_NOGO,
        "practice4_2": PRACTICE4_2_NUM_ACTUAL + PRACTICE4_2_NUM_NOGO
    }

    block_counters = {k: 0 for k in block_round_limits}
    block_rounds = {k: 1 for k in block_round_limits}

    with open(output_path, mode="r", newline="") as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    for row in reader:
        block = row["block"]
        if block in block_round_limits:
            block_counters[block] += 1
            row["round"] = str(block_rounds[block])

            if block_counters[block] == block_round_limits[block]:
                block_counters[block] = 0
                block_rounds[block] += 1
        else:
            row["round"] = None
    
    with open(output_path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

# Convert key input to string
def key_to_str(key):
    if key is None:
        return None
    elif key == pygame.K_v:
        return "v"
    elif key == pygame.K_m:
        return "m"
    else:
        return str(key)
