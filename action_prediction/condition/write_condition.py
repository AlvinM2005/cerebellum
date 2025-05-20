import pandas as pd
import os
import shutil

# Directory settings
CONDITIONS_FOLDER = "conditions"
VIDEOS_FOLDER = "videos"
ACTION_OBSERVATION_FOLDER = "action_observation"
SUBFOLDERS = {
    "demo.csv": "demo_videos",
    "test1.csv": "test1_videos",
    "test1_short.csv": "short_test1_videos",
    "test2.csv": "test2_videos",
    "test2_short.csv": "short_test2_videos"
}

# Remove the entire conditions and videos folders if they exist
for folder in [CONDITIONS_FOLDER, VIDEOS_FOLDER]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"Old {folder} folder deleted.")

# Create fresh conditions and videos folders
os.makedirs(CONDITIONS_FOLDER)
os.makedirs(VIDEOS_FOLDER)
for subfolder in SUBFOLDERS.values():
    os.makedirs(os.path.join(VIDEOS_FOLDER, subfolder))

# File paths
INPUT_FILE = "action_observation_logs.csv"
FILES = ["test1.csv", "test2.csv", "test1_short.csv", "test2_short.csv", "demo.csv"]

# Load the original action observation logs
df = pd.read_csv(INPUT_FILE)

# Select the relevant columns and add 'condition' and 'difficulty' columns
df_selected = df[['video_name', 'player_name', 'miss_goal', 'left_right']].copy()
df_selected['condition'] = df_selected['left_right'].apply(lambda x: 0 if x == 'left' else 1)
df_selected['difficulty'] = df_selected['miss_goal'].apply(lambda x: 0 if x == 'miss' else 1)

# Filter the first 31 rows for each player and each (condition, difficulty) pair
players = ['DC', 'EW', 'FI']
conditions = [(0, 0), (0, 1), (1, 0), (1, 1)]
test1_rows = []
test2_rows = []
test1_short_rows = []
test2_short_rows = []
demo_rows = []

for player in players:
    for condition, difficulty in conditions:
        # Filter rows matching the current player and (condition, difficulty) pair
        subset = df_selected[
            (df_selected['player_name'] == player) &
            (df_selected['condition'] == condition) &
            (df_selected['difficulty'] == difficulty)
        ]

        # Ensure there are at least 31 rows
        if len(subset) < 31:
            raise ValueError(f"Not enough rows for player {player}, condition {condition}, difficulty {difficulty}. Found {len(subset)} rows.")
        
        # Take exactly the first 31 rows
        subset = subset.head(31)

        # Select the first 15 for test1, the next 15 for test2
        test1_rows.append(subset.head(15))
        test2_rows.append(subset.iloc[15:30])
        
        # Select the first row for short versions
        test1_short_rows.append(subset.head(1))
        test2_short_rows.append(subset.iloc[15:16])

        # Select the 31st row for demo
        demo_rows.append(subset.iloc[30:31])

# Combine all the selected rows into separate dataframes
file_data = {
    "test1.csv": pd.concat(test1_rows, ignore_index=True),
    "test2.csv": pd.concat(test2_rows, ignore_index=True),
    "test1_short.csv": pd.concat(test1_short_rows, ignore_index=True),
    "test2_short.csv": pd.concat(test2_short_rows, ignore_index=True),
    "demo.csv": pd.concat(demo_rows, ignore_index=True),
}

# Add "key_correct" and "stimuli_path" columns, and remove "video_name"
for file_name, df in file_data.items():
    # Add "key_correct" column
    df["key_correct"] = df["condition"].apply(lambda x: 'v' if x == 0 else 'm')

    # Determine the correct video folder
    video_folder = os.path.join(VIDEOS_FOLDER, SUBFOLDERS[file_name])
    stimuli_base_path = f"./stimuli/videos/{SUBFOLDERS[file_name]}"

    # Copy videos one by one with index-only names
    for index, row in df.iterrows():
        video_name = row["video_name"]
        source_video = os.path.join(ACTION_OBSERVATION_FOLDER, f"{video_name}.mp4")
        destination_video = os.path.join(video_folder, f"{index + 1}.mp4")
        stimuli_path = f"{stimuli_base_path}/{index + 1}.mp4"
        
        if not os.path.exists(source_video):
            raise FileNotFoundError(f"Video file {source_video} not found.")
        
        # Copy the video with index as the new file name
        shutil.copy(source_video, destination_video)

        # Add the stimuli path to the dataframe
        df.at[index, "stimuli_path"] = stimuli_path

    # Remove the "video_name" column
    df.drop(columns=["video_name"], inplace=True)

    # Save the original file
    output_path = os.path.join(CONDITIONS_FOLDER, file_name)
    df.to_csv(output_path, index=False)

    # Create the flipped version
    df_flipped = df.copy()
    df_flipped["key_correct"] = df_flipped["key_correct"].apply(lambda x: 'm' if x == 'v' else 'v')
    flipped_file_name = file_name.replace(".csv", "_flipped.csv")
    flipped_output_path = os.path.join(CONDITIONS_FOLDER, flipped_file_name)
    df_flipped.to_csv(flipped_output_path, index=False)

    print(f"Generated {output_path} and {flipped_output_path} successfully.")

print("All files generated successfully in the 'conditions' and 'videos' folders.")
