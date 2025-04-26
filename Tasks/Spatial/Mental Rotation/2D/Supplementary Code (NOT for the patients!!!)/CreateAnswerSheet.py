import os
import csv
import shutil

def create_answer_sheet(input_folder):
    output_csv = f"{input_folder}_conditions.csv"
    output_txt = f"{input_folder}_answer.txt"
    output_folder = f"{input_folder}_images"

    if os.path.exists(output_csv):
        os.remove(output_csv)
    if os.path.exists(output_txt):
        os.remove(output_txt)
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    files = [f for f in os.listdir(input_folder) if f.endswith(".png")]

    rows = []

    for idx, file_name in enumerate(files, 1):
        name_parts = file_name[:-4].split("_")
        letter_name = name_parts[0]
        rotation_angle = int(name_parts[1])

        if len(name_parts) > 2 and name_parts[2] == "M":
            mirrored = 1
        else:
            mirrored = 0

        block = input_folder
        rows.append([idx, letter_name, rotation_angle, mirrored, block, file_name])

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item_number", "letter_name", "rotation_angle", "mirrored", "block", "file_name"])
        writer.writerows(rows)

    print(f"Saved CSV to {output_csv}")

    with open(output_txt, "w") as f:
        for row in rows:
            f.write(f"{row[3]}\n")

    print(f"Saved answers to {output_txt}")

    for idx, row in enumerate(rows, 1):
        file_name = row[5]
        src_path = os.path.join(input_folder, file_name)
        dst_file_name = f"{idx}.png"
        dst_path = os.path.join(output_folder, dst_file_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
        else:
            print(f"Warning: {file_name} not found in {input_folder}!")

    print(f"Done copying into {output_folder}")

create_answer_sheet("demo")
create_answer_sheet("test1")
create_answer_sheet("test2")
