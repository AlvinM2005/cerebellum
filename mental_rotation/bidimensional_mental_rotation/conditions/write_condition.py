import os
import csv
import shutil

input_folder = "stimuli"
conditions_folder = "conditions"
images_folder = "images"
output_csv_1 = os.path.join(conditions_folder, "test.csv")
output_csv_2 = os.path.join(conditions_folder, "test_flipped.csv")
output_folder = os.path.join(images_folder, "test_images")
short_folder = os.path.join(images_folder, "short_test_images")
demo_folder = os.path.join(images_folder, "demo_images")

if os.path.exists(conditions_folder):
    shutil.rmtree(conditions_folder)
os.makedirs(conditions_folder, exist_ok=True)

if os.path.exists(images_folder):
    shutil.rmtree(images_folder)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(short_folder, exist_ok=True)
os.makedirs(demo_folder, exist_ok=True)

files = [f for f in os.listdir(input_folder) if f.endswith(".png")]

rows = []

for idx, file_name in enumerate(files, 1):
    name_parts = file_name[:-4].split("_")
    letter_name = name_parts[0]
    rotation_angle = int(name_parts[1])

    if len(name_parts) > 2 and name_parts[2] == "M":
        key_correct = "k"
    else:
        key_correct = "d"

    condition = "mirrored" if key_correct == "m" else "normal"
    difficulty = abs(rotation_angle)
    mirrored = key_correct == "m"
    stimuli_path = f"./stimuli/images/test_images/{idx}.png"

    rows.append([
        letter_name,
        rotation_angle,
        mirrored,
        condition,
        difficulty,
        stimuli_path,
        key_correct
    ])

with open(output_csv_1, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "letter_name",
        "rotation_angle",
        "mirrored",
        "condition",
        "difficulty",
        "stimuli_path",
        "key_correct"
    ])
    writer.writerows(rows)

with open(output_csv_2, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "letter_name",
        "rotation_angle",
        "mirrored",
        "condition",
        "difficulty",
        "stimuli_path",
        "key_correct"
    ])
    flipped_rows = [
        row[:-1] + [("d" if row[-1] == "k" else "k")]
        for row in rows
    ]
    writer.writerows(flipped_rows)

short_rows = rows[:10]
short_flipped_rows = [
    row[:-1] + [("d" if row[-1] == "k" else "k")]
    for row in short_rows
]

for i, row in enumerate(short_rows):
    row[5] = f"./stimuli/images/short_test_images/{i+1}.png"
for i, row in enumerate(short_flipped_rows):
    row[5] = f"./stimuli/images/short_test_images/{i+1}.png"

with open(os.path.join(conditions_folder, "test_short.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "letter_name",
        "rotation_angle",
        "mirrored",
        "condition",
        "difficulty",
        "stimuli_path",
        "key_correct"
    ])
    writer.writerows(short_rows)

with open(os.path.join(conditions_folder, "test_short_flipped.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "letter_name",
        "rotation_angle",
        "mirrored",
        "condition",
        "difficulty",
        "stimuli_path",
        "key_correct"
    ])
    writer.writerows(short_flipped_rows)

demo_rows = rows[-5:]
demo_flipped_rows = [
    row[:-1] + [("v" if row[-1] == "m" else "m")]
    for row in demo_rows
]

for i, row in enumerate(demo_rows):
    row[5] = f"./stimuli/images/demo_images/{i+1}.png"
for i, row in enumerate(demo_flipped_rows):
    row[5] = f"./stimuli/images/demo_images/{i+1}.png"

with open(os.path.join(conditions_folder, "demo.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "letter_name",
        "rotation_angle",
        "mirrored",
        "condition",
        "difficulty",
        "stimuli_path",
        "key_correct"
    ])
    writer.writerows(demo_rows)

with open(os.path.join(conditions_folder, "demo_flipped.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "letter_name",
        "rotation_angle",
        "mirrored",
        "condition",
        "difficulty",
        "stimuli_path",
        "key_correct"
    ])
    writer.writerows(demo_flipped_rows)

for idx, file_name in enumerate(files, 1):
    src_path = os.path.join(input_folder, file_name)
    dst_file_name = f"{idx:02d}_{file_name}"
    dst_path = os.path.join(output_folder, dst_file_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dst_path)

short_files = sorted(os.listdir(output_folder))[:10]
for i, file_name in enumerate(short_files, 1):
    src = os.path.join(output_folder, file_name)
    dst = os.path.join(short_folder, f"{i}.png")
    shutil.copy(src, dst)

demo_files = sorted(os.listdir(output_folder))[-5:]
for i, file_name in enumerate(demo_files, 1):
    src = os.path.join(output_folder, file_name)
    dst = os.path.join(demo_folder, f"{i}.png")
    shutil.copy(src, dst)

print("All CSVs and image folders generated.")
