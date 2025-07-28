# Import
import pandas as pd

# Read the original CSV file
df = pd.read_csv("action_observation_logs.csv")

# Make a copy containing only desired columns ("video_name", "player_name", "miss_goal", "left_right")
columns_to_keep = ["video_name", "player_name", "miss_goal", "left_right"]
df = df[columns_to_keep]

# Convert miss/goal and left/right into binary values
df["miss_goal"] = df["miss_goal"].replace({"miss": 0, "goal": 1})
df["left_right"] = df["left_right"].replace({"left": 0, "right": 1})
df["player_name"] = df["player_name"].str.lower()  # Ensure lowercase matching

# Initialize result containers
test1_parts = []
test2_parts = []

# Iterate through each player group
for player in ["dc", "fi", "ew"]:
    group_df = df[df["player_name"] == player].sort_values("video_name").reset_index(drop=True)
    targets = [(0, 0), (1, 1), (0, 1), (1, 0)]

    for target in targets:
        subset = group_df[
            (group_df["miss_goal"] == target[0]) &
            (group_df["left_right"] == target[1])
        ].reset_index(drop=True)

        # Select first 30
        trimmed = subset.head(30)

        # Split into two halves: 15 for test1, 15 for test2
        test1_parts.append(trimmed.iloc[:15])
        test2_parts.append(trimmed.iloc[15:30])

# Combine test logs in fixed order (no shuffling!)
df_test1 = pd.concat(test1_parts, ignore_index=True)
df_test2 = pd.concat(test2_parts, ignore_index=True)

# Save output files
df_test1.to_csv("test1_log.csv", index=False)
df_test2.to_csv("test2_log.csv", index=False)

print("✅ test1_log.csv and test2_log.csv created with 180 rows each (answer column removed).")
