# Cerebellar battery (track changes for final version)


# SD (24 Feb, 2026)

**General changes:**
- Added a 'list' column (A/B) to results for stimulus set tracking.
- Timeout trials now record correct=0 and show expected joystick direction or key, with NA for responses.
- Fixed mapping logic: Mapping 1 (d/left=meaningful, k/right=meaningless), Mapping 2 (d/left=meaningless, k/right=meaningful).
- Results columns for key/joystick responses and correct answers now always match the mapping version.
- The code automatically fills key_* or joy_* columns depending on the input device used.
- The order of sentences in each block is sampled randomly from the CSV, not fully shuffled (the result is the same since I have 45 sentences available per block).
- SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

- **Font Path Fix:** 

Resolved cross-platform font loading issues by migrating FONT definition from config.py to paths.py using pathlib.Path. Ensure proper path resolution on Windows and macOS

**Font Path Resolution:**
```python
# Before (config.py):
FONT = "resources\\OpenSans.ttf"  # Windows-only backslashes

# After (paths.py):
FONT = RESOURCES_DIR / "OpenSans.ttf"  # pathlib.Path auto-resolves separators
```

- **SD Mapping Background Implementation:** 

Added SD mapping images as backgrounds for target words. SD_Mapping_1.png or SD_Mapping_2.png are displayed based on the mapping version (cfg.MAPPING) during target word presentation. I also updated the position of the mapping in the Figma templates. 

- **Joystick Movement Restrictions:** 

Implemented horizontal-only input validation to prevent accidental up/down movements when hand is resting on joystick. I applied 2 filters: deadzone validation (abs(x) < 0.60 && abs(y) < 0.60) and directional strength requirements (horizontal movement must be ≥70% stronger than vertical component) to prevent tahta very inaccurate diagonal movements are recognized as answers. 

```python
def _process_joystick(self) -> None:
    x = self._joystick.get_axis(0)
    y = self._joystick.get_axis(1)
    
    # Layer 1: Standard deadzone (prevents micro-movements)
    if abs(x) < cfg.dz_x and abs(y) < cfg.dz_y:
        return
    
    # Layer 2: Directional strength filter (prevents accidental verticals)
    if abs(x) < abs(y) * 0.7:  # Horizontal must be ≥70% of vertical strength
        return
    
    # Process only strong horizontal movements
    angle = (math.degrees(math.atan2(x, -y)) + 360) % 360
    if 180 <= angle < 360:
        self._state.option_1 = True  # Left
    elif 0 <= angle < 180:
        self._state.option_2 = True  # Right
```

# IED (Feb 18, 2026)

- **Stimulus Assignment Fix:** 

Corrected stimulus consistency across phases P3 (CDS), P4 (CDO), and P5 (CDR) to maintain proper rule sequence. P3-P4 now use the same correct stimulus, while P5 reverses back to P1's stimulus.

- **Phase Naming Update:**

Updated internal phase names to standard abbreviations: P3=CDS (Compound Discrimination Separated), P4=CDO (Compound Discrimination Overlapped), P5=CDR (Compound Discrimination Reversal), P6=IDS (Intra-Dimensional Shift), P7=IDR (Intra-Dimensional Reversal), P8=EDS (Extra-Dimensional Shift), P9=EDR (Extra-Dimensional Reversal).

- **Force Quit Improvement:**

Modified the 50-trial force quit mechanism to transition to the thank you screen instead of abruptly terminating the experiment.

- **Response Validation:**

Implemented validation to ignore responses to empty quadrants. Only responses to actual stimulus positions (correct or incorrect) are now recorded as valid trials.

- **Stimulus Feature Decomposition:**

Added 8 new columns to CSV output for attention modeling (Talwar et al., 2024 approach): `correct_shape`, `correct_line`, `incorrect_shape`, `incorrect_line`, `chosen_shape`, `chosen_line`, `unchosen_shape`, `unchosen_line`. This enables computational analysis of attention allocation during dimensional shifts.


## 1. General Changes - Implemented for all tasks (February 3, 2026)

- **Hand Preference Question:** 

Replaced the question regarding the less affected hand with "Which hand will the participant use to respond?". The answer to this question must be saved in the used_hand column of the output CSV.

- **Filename Formatting:** 

The output CSV filename now includes the date in YYYY_MM_DD format.

Example: For participant ctrl01, the generated results file will be: ctrl01_nBack_results_2026_02_03.csv.

- **Overwrite Protection (Versioning):**

 If the same participant ID is used more than once on the same date, the output CSV is not overwritten. Instead, a version suffix (_v2, _v3, etc.) is appended after the ID for subsequent runs.

-First run: ctrl01_nBack_results_2026_02_03.csv

--Second run: ctrl01_v2_nBack_results_2026_02_03.csv

Third run: ctrl01_v3_nBack_results_2026_02_03.csv

- **Task Column:**

 Added a new column named task at the beginning of the output CSV, containing the name of the specific task being executed.

- **End Screen:** 

The final screen ("Thank you for your participation") will now close the experiment upon pressing the spacebar or after 10 seconds have elapsed, whichever occurs first.

- **Vsync. Warning on RT accuracy:**

Due to the 60Hz monitor refresh rate, there is a potential ~16ms lag between the software command and the actual stimulus display. To correct this, I have enabled V-Sync (vsync=1). This ensures pygame.display.flip() waits for the screen refresh before starting the timer (trial_start), synchronizing the code with the visual output. Without V-Sync, our timing would start prematurely.

I did this in the init_display function. Let’s keep it this way for all tasks, please.

- **Task Duration Tracking:**

Added automatic calculation and logging of total task completion time. The system now displays the total duration in minutes and seconds in the console when the task ends. 

**Location in code:**
- File: `nBack/src/core/experiment_flow.py`
- Function: `run()` (at the end, just before `pygame.quit()`)
- Lines: Added after line 290

**How it works:**
1. At the start of the experiment (line 137), the system records the start time: `cfg.START_TIME = datetime.datetime.now().isoformat()`
2. At the end of the task, the code calculates elapsed time:
   - Converts `cfg.START_TIME` back to a datetime object
   - Subtracts it from the current end time
   - Converts the result to minutes (total_seconds / 60)
3. Logs two messages to the console:
   - `Task completed successfully!`
   - `Total task duration: X.XX minutes (Y seconds)`

**Code implementation:**
```python
# Calculate and display total task duration
end_time = datetime.datetime.now()
start_time_obj = datetime.datetime.fromisoformat(cfg.START_TIME)
total_duration = end_time - start_time_obj
total_minutes = total_duration.total_seconds() / 60

logger.info(f"Task completed successfully!")
logger.info(f"Total task duration: {total_minutes:.2f} minutes ({int(total_duration.total_seconds())} seconds)")
```

**To reproduce this in other tasks:**
1. Ensure `datetime` is imported at the top of the file: `import datetime`
2. The task must already record `cfg.START_TIME` at startup
3. Add the above code block at the very end of the `run()` function, just before `pygame.quit()`

Example console output: `Total task duration: 23.45 minutes (1407 seconds)`

## 2. N-Back Updates (February 3, 2026)

- **Fixation Cross:** 

Added a fixation cross during the Inter-Stimulus Interval (ISI).

- **Fixed Timing (Jaeggi et al., 2010):** 

The stimulus (500 ms) and the fixation cross (2500 ms) now remain on screen for their full duration, even if a response is registered. Pressing the spacebar does not interrupt the display of these elements.

- **Smart Feedback Timing:**

Immediate feedback: Triggered when the participant responds (any time within the 3000ms window).

Delayed feedback: Displayed when there is no response to targets (appears in the last 500ms of the 3000ms window).

Maximized response opportunity: Full 3000ms uninterrupted response time allowed for missed targets.

Standard feedback duration: Set to 500ms for optimal visibility.