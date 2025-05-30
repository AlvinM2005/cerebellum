import os
import csv
import shutil

# Paths
stimuli_folder = "stimuli"
images_root = "images"
test1_folder = os.path.join(images_root, "test1_images")
test2_folder = os.path.join(images_root, "test2_images")
conditions_folder = "conditions"
test1_csv = os.path.join(conditions_folder, "test1.csv")
test2_csv = os.path.join(conditions_folder, "test2.csv")

# Recreate folders
if os.path.exists(images_root):
    shutil.rmtree(images_root)
os.makedirs(test1_folder, exist_ok=True)
os.makedirs(test2_folder, exist_ok=True)

if os.path.exists(conditions_folder):
    shutil.rmtree(conditions_folder)
os.makedirs(conditions_folder, exist_ok=True)

# Load original file list (DO NOT SORT)
image_files = [f for f in os.listdir(stimuli_folder) if f.endswith(".jpg")]

if len(image_files) != 384:
    raise ValueError(f"❌ Expected 384 images, found {len(image_files)}.")

# Split and copy
first_half = image_files[:192]
second_half = image_files[192:]

for filename in first_half:
    shutil.copy(os.path.join(stimuli_folder, filename), os.path.join(test1_folder, filename))

for filename in second_half:
    shutil.copy(os.path.join(stimuli_folder, filename), os.path.join(test2_folder, filename))

# CSV generator
def generate_conditions_csv(image_folder, output_csv, expected_count):
    files = [f for f in os.listdir(image_folder) if f.endswith(".jpg")]
    rows = []
    id = 1

    for file_name in files:
        name_parts = file_name[:-4].split("_")
        object_id = int(name_parts[0])
        rotation_angle = int(name_parts[1])
        reversed_flag = len(name_parts) == 3 and name_parts[2] == "R"
        condition = "reversed" if reversed_flag else "normal"
        difficulty = rotation_angle
        key_correct = "m" if reversed_flag else "v"
        stimuli_path = f"./stimuli/{image_folder}/{id}.jpg".replace("\\", "/")
        id += 1

        rows.append([
            object_id,
            rotation_angle,
            reversed_flag,
            condition,
            difficulty,
            stimuli_path,
            key_correct
        ])

    if len(rows) != expected_count:
        raise ValueError(f"❌ {output_csv} has {len(rows)} rows (expected {expected_count}).")

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "object_id",
            "rotation_angle",
            "reversed",
            "condition",
            "difficulty",
            "stimuli_path",
            "key_correct"
        ])
        writer.writerows(rows)

    print(f"✅ {output_csv} written with {expected_count} rows.")

# Generate test1.csv and test2.csv
generate_conditions_csv(test1_folder, test1_csv, 192)
generate_conditions_csv(test2_folder, test2_csv, 192)
print("🎉 test1.csv and test2.csv created.")

# Short sets
short_test1_folder = os.path.join(images_root, "short_test1_images")
short_test2_folder = os.path.join(images_root, "short_test2_images")
short_test1_csv = os.path.join(conditions_folder, "test1_short.csv")
short_test2_csv = os.path.join(conditions_folder, "test2_short.csv")

os.makedirs(short_test1_folder, exist_ok=True)
os.makedirs(short_test2_folder, exist_ok=True)

test1_images = [f for f in os.listdir(test1_folder) if f.endswith(".jpg")][:10]
test2_images = [f for f in os.listdir(test2_folder) if f.endswith(".jpg")][:10]

for filename in test1_images:
    shutil.copy(os.path.join(test1_folder, filename), os.path.join(short_test1_folder, filename))

for filename in test2_images:
    shutil.copy(os.path.join(test2_folder, filename), os.path.join(short_test2_folder, filename))

generate_conditions_csv(short_test1_folder, short_test1_csv, 10)
generate_conditions_csv(short_test2_folder, short_test2_csv, 10)
print("📦 Short sets completed.")

# Demo set (from original stimuli folder only)
demo_folder = os.path.join(images_root, "demo_images")
demo_csv = os.path.join(conditions_folder, "demo.csv")
os.makedirs(demo_folder, exist_ok=True)

# Get last 5 images from original image list (no sort)
demo_images = image_files[-5:]

for filename in demo_images:
    src = os.path.join(stimuli_folder, filename)
    dst = os.path.join(demo_folder, filename)
    shutil.copy(src, dst)

generate_conditions_csv(demo_folder, demo_csv, 5)
print("🚀 Demo set completed from original stimuli.")

# Flip key_correct column and save to new csv
def generate_flipped_csv(original_csv_path, flipped_csv_path):
    with open(original_csv_path, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Flip key_correct column (last column)
    flipped_rows = []
    for row in rows:
        flipped_key = "m" if row[-1] == "v" else "v"
        flipped_row = row[:-1] + [flipped_key]
        flipped_rows.append(flipped_row)

    with open(flipped_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(flipped_rows)

    print(f"🔁 Flipped version written: {flipped_csv_path}")

# Define original and flipped csv pairs
csv_pairs = [
    ("test1.csv", "test1_flipped.csv"),
    ("test2.csv", "test2_flipped.csv"),
    ("test1_short.csv", "test1_short_flipped.csv"),
    ("test2_short.csv", "test2_short_flipped.csv"),
    ("demo.csv", "demo_flipped.csv"),
]

# Generate all flipped csvs
for original_name, flipped_name in csv_pairs:
    original_path = os.path.join(conditions_folder, original_name)
    flipped_path = os.path.join(conditions_folder, flipped_name)
    generate_flipped_csv(original_path, flipped_path)

import os

# Rename images in folder
def rename_images_in_folder(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
    for i, old_name in enumerate(image_files, 1):
        old_path = os.path.join(folder_path, old_name)
        new_name = f"{i}.jpg"
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
    print(f"🔢 Renamed images in {folder_path} to sequential numbers.")

image_folders_to_rename = [
    "./images/test1_images",
    "./images/test2_images",
    "./images/short_test1_images",
    "./images/short_test2_images",
    "./images/demo_images"
]

for folder in image_folders_to_rename:
    rename_images_in_folder(folder)
