# Cerebellar battery (track changes for final version)


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