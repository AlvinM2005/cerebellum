import csv
import os
import pygame
from meta_parameters import *

# def save_results_to_csv(filename, participant_id, all_results, global_start_time, global_end_time):
#     # Create save directory
#     actual_filename = f'{participant_id}_{filename}'
#
#     results_dir = "results"
#     if not os.path.exists(results_dir):
#         os.makedirs(results_dir)
#
#     output_path = os.path.join(results_dir, actual_filename)
#
#     # Define field names
#     fieldnames = [
#         "participant_id",
#         "trial_number",
#         "block",
#         "round",
#         "type",
#         "fixation_time",
#         "condition",
#         "version",
#         "difficulty",
#         "key_correct",
#         "hand",
#         "fixation_key_response",
#         "fixation_reaction_time_ms",
#         "stimulus_key_response",
#         "stimulus_reaction_time_ms",
#         "isi_key_response",
#         "isi_reaction_time_ms",
#         "correct",
#         "error_type",
#         "start_time",
#         "end_time"
#     ]
#
#     # Write to CSV
#     with open(output_path, mode="a", newline="") as file:
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#
#         for index, trial in enumerate(all_results):
#             if key_to_str(trial["key_correct"]) == "v":
#                 hand = "left"
#             elif key_to_str(trial["key_correct"]) == "m":
#                 hand = "right"
#             else:
#                 hand = None
#
#             writer.writerow({
#                 "participant_id": participant_id,
#                 "trial_number": index + 1,
#                 "block": trial["block"],
#                 "round": 0,
#                 "type": trial["type"],
#                 "fixation_time": trial["fixation_time"],
#                 "condition": trial["condition"],
#                 "version": VERSION,
#                 "difficulty": trial["difficulty"],
#                 "key_correct": key_to_str(trial["key_correct"]),
#                 "hand": hand,
#                 "fixation_key_response": key_to_str(trial["fixation_key_response"]),
#                 "fixation_reaction_time_ms": trial["fixation_reaction_time_ms"],
#                 "stimulus_key_response": key_to_str(trial["stimulus_key_response"]),
#                 "stimulus_reaction_time_ms": trial["stimulus_reaction_time_ms"],
#                 "isi_key_response": key_to_str(trial["isi_key_response"]),
#                 "isi_reaction_time_ms": trial["isi_reaction_time_ms"],
#                 "correct": str(trial["correct"]),
#                 "error_type": trial["error_type"],
#                 "start_time": global_start_time,
#                 "end_time": global_end_time
#             })
#
#     # Calculate Round
#     block_round_limits = {
#         "practice1_1": PRACTICE1_1_NUM_BLUE + PRACTICE1_1_NUM_NOGO,
#         "practice1_2": PRACTICE1_2_NUM_BLUE + PRACTICE1_2_NUM_NOGO,
#         "practice2_1": PRACTICE2_1_NUM_RED + PRACTICE2_1_NUM_NOGO,
#         "practice2_2": PRACTICE2_2_NUM_RED + PRACTICE2_2_NUM_NOGO,
#         "practice3_1": PRACTICE3_1_NUM_RED + PRACTICE3_1_NUM_BLUE + PRACTICE3_1_NUM_NOGO,
#         "practice3_2": PRACTICE3_2_NUM_RED + PRACTICE3_2_NUM_BLUE + PRACTICE3_2_NUM_NOGO,
#         "practice4_1": PRACTICE4_1_NUM_ACTUAL + PRACTICE4_1_NUM_NOGO,
#         "practice4_2": PRACTICE4_2_NUM_ACTUAL + PRACTICE4_2_NUM_NOGO
#     }
#
#     block_counters = {k: 0 for k in block_round_limits}
#     block_rounds = {k: 1 for k in block_round_limits}
#
#     with open(output_path, mode="r", newline="") as f:
#         reader = list(csv.DictReader(f))
#
#     # Determine if any row contains no-go errors
#     has_no_go_error = any(
#         row["error_type"] in ["no_go_error", "no_go_delay_error"]
#         and not row["block"].startswith("practice")
#         for row in reader
#     )
#
#     # Update rounds and assign "valid" field
#     for row in reader:
#         block = row["block"]
#         if block in block_round_limits:
#             block_counters[block] += 1
#             row["round"] = str(block_rounds[block])
#
#             if block_counters[block] == block_round_limits[block]:
#                 block_counters[block] = 0
#                 block_rounds[block] += 1
#         else:
#             row["round"] = None
#
#         row["valid"] = str(not has_no_go_error)
#
#     # Reorder fieldnames to insert "valid" after "error_type"
#     fieldnames = list(reader[0].keys())
#     if "valid" not in fieldnames:
#         error_type_index = fieldnames.index("error_type")
#         fieldnames.insert(error_type_index + 1, "valid")
#
#     with open(output_path, mode="w", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(reader)


def save_results_to_csv(filename, participant_id, all_results, global_start_time, global_end_time):
    # Create save directory
    actual_filename = f'{participant_id}_{filename}'

    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    print("final save, results_dir=", results_dir, " actual_filename=", actual_filename)
    output_path = os.path.join(results_dir, actual_filename)
    output_path = results_dir + "/" + actual_filename

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
    # with open(output_path, mode="a", newline="") as file:
    #     writer = csv.DictWriter(file, fieldnames=fieldnames)
    #     writer.writeheader()
    #
    #     for index, trial in enumerate(all_results):
    #         if key_to_str(trial["key_correct"]) == "v":
    #             hand = "left"
    #         elif key_to_str(trial["key_correct"]) == "m":
    #             hand = "right"
    #         else:
    #             hand = None
    #
    #         writer.writerow({
    #             "participant_id": participant_id,
    #             "trial_number": index + 1,
    #             "block": trial["block"],
    #             "round": 0,
    #             "type": trial["type"],
    #             "fixation_time": trial["fixation_time"],
    #             "condition": trial["condition"],
    #             "version": VERSION,
    #             "difficulty": trial["difficulty"],
    #             "key_correct": key_to_str(trial["key_correct"]),
    #             "hand": hand,
    #             "fixation_key_response": key_to_str(trial["fixation_key_response"]),
    #             "fixation_reaction_time_ms": trial["fixation_reaction_time_ms"],
    #             "stimulus_key_response": key_to_str(trial["stimulus_key_response"]),
    #             "stimulus_reaction_time_ms": trial["stimulus_reaction_time_ms"],
    #             "isi_key_response": key_to_str(trial["isi_key_response"]),
    #             "isi_reaction_time_ms": trial["isi_reaction_time_ms"],
    #             "correct": str(trial["correct"]),
    #             "error_type": trial["error_type"],
    #             "start_time": global_start_time,
    #             "end_time": global_end_time
    #         })

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

    # Determine if any row contains no-go errors
    has_no_go_error = any(
        row["error_type"] in ["no_go_error", "no_go_delay_error"]
        and not row["block"].startswith("practice")
        for row in reader
    )

    # Update rounds and assign "valid" field
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

        row["valid"] = str(not has_no_go_error)

    # Reorder fieldnames to insert "valid" after "error_type"
    fieldnames = list(reader[0].keys())
    if "valid" not in fieldnames:
        error_type_index = fieldnames.index("error_type")
        fieldnames.insert(error_type_index + 1, "valid")

    with open(output_path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)


def InitResultCSV(filename, participant_id):
    # No longer removes existing files - preserves previous data
    # This matches behavior of action_prediction and mental_rotation tasks
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    print(f"Results directory ready: {results_dir}")
    # SaveResultsToCsv will handle unique filename generation


index = 0
current_participant_file = None  # Track the current participant's file

def SaveResultsToCsv(filename, participant_id, all_results, global_start_time, global_end_time):
    print("start to save result\n", all_results)
    # Create save directory
    global index, current_participant_file

    # Get the directory where this script is located to ensure results are saved in the right place
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "results")
    
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    print(f"=== SAVING TO DIRECTORY: {results_dir} ===")

    # Use global file tracking to ensure all trials from same participant go to same file
    if current_participant_file is None or not current_participant_file.startswith(participant_id):
        # This is a new participant or session, determine the filename
        base_filename = f'{participant_id}_CC_{filename}'
        actual_filename = base_filename
        output_path = os.path.join(results_dir, actual_filename)
        
        # If file already exists, create versioned filename
        counter = 2
        while os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            name_part = base_filename.rsplit('.', 1)[0]  # Remove .csv
            ext_part = base_filename.rsplit('.', 1)[1] if '.' in base_filename else 'csv'
            actual_filename = f"{name_part}_{counter}.{ext_part}"
            output_path = os.path.join(results_dir, actual_filename)
            counter += 1
        
        # Remember this filename for subsequent trials
        current_participant_file = actual_filename
    else:
        # Use the same file as previous trials for this participant
        actual_filename = current_participant_file
        output_path = os.path.join(results_dir, actual_filename)
    
    print("participate_id=", participant_id, " actual_filename=", actual_filename)
    print(f"=== FULL PATH: {output_path} ===")

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

    with open(output_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if os.path.getsize(output_path) == 0:
            writer.writeheader()

        hand = None
        if key_to_str(all_results["key_correct"]) == "v":
            hand = "left"
        elif key_to_str(all_results["key_correct"]) == "m":
            hand = "right"
        elif key_to_str(all_results["key_correct"]) == "d":
            hand = "left"  # Assuming D is left hand
        elif key_to_str(all_results["key_correct"]) == "k":
            hand = "right"  # Assuming K is right hand

        writer.writerow({
            "participant_id": participant_id,
            "trial_number": index + 1,
            "block": all_results["block"],
            "round": 0,
            "type": all_results["type"],
            "fixation_time": all_results["fixation_time"],
            "condition": all_results["condition"],
            "version": VERSION,
            "difficulty": all_results["difficulty"],
            "key_correct": key_to_str(all_results["key_correct"]),
            "hand": hand,
            "fixation_key_response": key_to_str(all_results["fixation_key_response"]),
            "fixation_reaction_time_ms": all_results["fixation_reaction_time_ms"],
            "stimulus_key_response": key_to_str(all_results["stimulus_key_response"]),
            "stimulus_reaction_time_ms": all_results["stimulus_reaction_time_ms"],
            "isi_key_response": key_to_str(all_results["isi_key_response"]),
            "isi_reaction_time_ms": all_results["isi_reaction_time_ms"],
            "correct": str(1 if all_results["correct"] else 0),
            "error_type": all_results["error_type"],
            "start_time": global_start_time,
            "end_time": global_end_time
        })

    index = index + 1
    
    print(f"=== FILE SAVED SUCCESSFULLY TO: {output_path} ===")
    print(f"=== FILE SIZE: {os.path.getsize(output_path)} bytes ===")


    # # Calculate Round
    # block_round_limits = {
    #     "practice1_1": PRACTICE1_1_NUM_BLUE + PRACTICE1_1_NUM_NOGO,
    #     "practice1_2": PRACTICE1_2_NUM_BLUE + PRACTICE1_2_NUM_NOGO,
    #     "practice2_1": PRACTICE2_1_NUM_RED + PRACTICE2_1_NUM_NOGO,
    #     "practice2_2": PRACTICE2_2_NUM_RED + PRACTICE2_2_NUM_NOGO,
    #     "practice3_1": PRACTICE3_1_NUM_RED + PRACTICE3_1_NUM_BLUE + PRACTICE3_1_NUM_NOGO,
    #     "practice3_2": PRACTICE3_2_NUM_RED + PRACTICE3_2_NUM_BLUE + PRACTICE3_2_NUM_NOGO,
    #     "practice4_1": PRACTICE4_1_NUM_ACTUAL + PRACTICE4_1_NUM_NOGO,
    #     "practice4_2": PRACTICE4_2_NUM_ACTUAL + PRACTICE4_2_NUM_NOGO
    # }
    #
    # block_counters = {k: 0 for k in block_round_limits}
    # block_rounds = {k: 1 for k in block_round_limits}
    #
    # with open(output_path, mode="r", newline="") as f:
    #     reader = list(csv.DictReader(f))
    #
    # # Determine if any row contains no-go errors
    # has_no_go_error = any(
    #     row["error_type"] in ["no_go_error", "no_go_delay_error"]
    #     and not row["block"].startswith("practice")
    #     for row in reader
    # )
    #
    # # Update rounds and assign "valid" field
    # for row in reader:
    #     block = row["block"]
    #     if block in block_round_limits:
    #         block_counters[block] += 1
    #         row["round"] = str(block_rounds[block])
    #
    #         if block_counters[block] == block_round_limits[block]:
    #             block_counters[block] = 0
    #             block_rounds[block] += 1
    #     else:
    #         row["round"] = None
    #
    #     row["valid"] = str(not has_no_go_error)
    #
    # # Reorder fieldnames to insert "valid" after "error_type"
    # fieldnames = list(reader[0].keys())
    # if "valid" not in fieldnames:
    #     error_type_index = fieldnames.index("error_type")
    #     fieldnames.insert(error_type_index + 1, "valid")
    #
    # with open(output_path, mode="w", newline="") as f:
    #     writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(reader)

# Convert key input to string
def key_to_str(key):
    if key is None:
        return None
    elif key == pygame.K_v:
        return "v"
    elif key == pygame.K_m:
        return "m"
    elif key == pygame.K_d:
        return "d"
    elif key == pygame.K_k:
        return "k"
    else:
        return str(key)
