import pandas as pd
import os
import shutil

# Define input log and output folders
source_folder = "action_observation"
test1_csv = "test1_log.csv"
test2_csv = "test2_log.csv"
test1_video_folder = os.path.join("videos", "test1_videos")
test2_video_folder = os.path.join("videos", "test2_videos")

# Create output folders if not exist
os.makedirs(test1_video_folder, exist_ok=True)
os.makedirs(test2_video_folder, exist_ok=True)

# Function to process one test set
def process_test_set(csv_file, video_folder, answer_txt_name):
    # Read and shuffle the log file
    df = pd.read_csv(csv_file)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save the answer column (left_right) to .txt
    df_shuffled["left_right"].to_csv(answer_txt_name, index=False, header=False)

    # Copy and rename videos
    missing = []
    for i, video_name in enumerate(df_shuffled["video_name"], start=1):
        src = os.path.join(source_folder, f"{video_name}.mp4")
        dst = os.path.join(video_folder, f"{i}.mp4")
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"✅ Copied: {video_name}.mp4 → {i}.mp4")
        else:
            print(f"❌ Missing: {video_name}.mp4")
            missing.append(video_name)

    return len(df_shuffled), len(missing), missing

# Process test1
print("\n📁 Processing test1...")
count1, missing1_count, missing1 = process_test_set(test1_csv, test1_video_folder, "test1_answer.txt")

# Process test2
print("\n📁 Processing test2...")
count2, missing2_count, missing2 = process_test_set(test2_csv, test2_video_folder, "test2_answer.txt")

# Final report
print(f"\n✅ Done! Total: {count1 + count2} videos processed.")
if missing1 or missing2:
    print("The following files are missing:")
    for f in missing1 + missing2:
        print(f"  - {f}")
