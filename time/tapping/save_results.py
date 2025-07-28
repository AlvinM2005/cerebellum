import csv
import os
from meta_parameters import *

# Save results
def save_results(all_results, participant_id):
    # Create save directory
    actual_filename = f"{participant_id}.csv"

    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    output_path = os.path.join(results_dir, actual_filename)

    # Define field names
    fieldnames = [
        "participant_id",
        "block",
        "trial_number",
        "type",
        "tap_number",
        "timestamp_ms",
        "ISI_ms",
        "interval",
        "trial_type",
        "hand",
        "group",
    ]

    # Write to CSV
    with open(output_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        tap_number = 0

        for result_w_info in all_results:
            types = []
            timestamps = []
            intervals = []
            block, trial_number, hand, group, trial_result = result_w_info
            
            for result in trial_result:
                type = result[0]
                types.append(type)
                timestamp_ms = result[1]
                timestamps.append(timestamp_ms)
            assert len(types) == len(timestamps)
            
            trial_type = "Successful"
            for i in range(len(timestamps) - 1):
                if types[i] != "synchronized":
                    # Self-paced intervals
                    interval = timestamps[i+1] - timestamps[i]
                    intervals.append(interval)
                    if interval < MINIMUM_SELF_PACED_INTERVAL or interval > MAXIMUM_SELF_PACED_INTERVAL:
                        trial_type = "Failed"
                else:
                    # Synchronized intervals - calculate interval between consecutive SPACE presses
                    interval = timestamps[i+1] - timestamps[i]
                    intervals.append(interval)
            intervals.append(None)  # Last timestamp has no interval
            print(timestamps)
            print(len(timestamps))
            print(intervals)
            print(len(intervals))
            assert len(timestamps) == len(intervals)

            for i in range(len(timestamps)):
                tap_number += 1
                writer.writerow({
                    "participant_id": participant_id,
                    "block": block,
                    "trial_number": trial_number,
                    "type": types[i],
                    "tap_number": tap_number,
                    "timestamp_ms": timestamps[i],
                    "ISI_ms": SYNCHRONIZED_INTERVAL,
                    "interval": intervals[i],
                    "trial_type": trial_type,
                    "hand": hand,
                    "group": group
                })
