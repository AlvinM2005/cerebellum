# Cerebellar battery (track changes for final version)


# CCS (4 March, 2026)

**Directory Creation Fix:**
- Added automatic `results/` directory creation if it doesn't exist to prevent "No such file or directory" errors when saving CSV files. `RESULTS_DIR.mkdir(exist_ok=True)` added to `create_save()` function in each task's `saves.py`.
- Applied to CCS, IED, nBack, and SD tasks for consistency.

**Window Title:**
- Changed display caption from "IED" to "CCS" in `pygame_render.py` (`pygame.display.set_caption("CCS")`).
- Fixed window title persistence: caption now correctly shows "CCS" in both fullscreen and windowed modes after toggling with ESC key.
- Added `pygame.display.set_caption("CCS")` in `toggle_full_screen()` function to maintain correct title after mode switching.

**Condition Variable Format:**
- Removed "-actual" suffix from condition variable for regular trials (e.g., "motor" instead of "motor-actual").
- Catch trials still use "-catch" suffix (e.g., "motor-catch") for proper identification.
- Modified in `saves.py`: `condition = f"{condition_task}{'-catch' if is_catch else ''}"`

**Joystick Detection Fix:**
- **Root Cause:** Joystick inputs were being ignored when keyboard had any residual events in the same frame due to conditional input source assignment (`if self._input_source_frame is None: self._input_source_frame = "joy"`).
- **Solution:** Changed to unconditional input source assignment in `event_handler.py`:

```python
# event_handler.py - _process_joystick() method
# Before (problematic):
if self._input_source_frame is None:
    self._input_source_frame = "joy"

# After (fixed):
self._input_source_frame = "joy"  # Always set when joystick moves
```

This ensures joystick inputs are always registered regardless of keyboard state, fixing the bug where joystick was completely ignored in CCS.

**Joystick Movement Restrictions (Horizontal-Only Validation):**
- Implemented two-layer filtering system to prevent accidental up/down movements when hand is resting on joystick:

```python
# event_handler.py - _process_joystick() method
def _process_joystick(self) -> None:
    x = self._joystick.get_axis(0)
    y = self._joystick.get_axis(1)
    
    # Layer 1: Standard deadzone (prevents micro-movements)
    if abs(x) < cfg.DZ_X and abs(y) < cfg.DZ_Y:  # DZ_X = DZ_Y = 0.60
        return
    
    # Layer 2: Directional strength filter (prevents accidental verticals)
    if abs(x) < abs(y) * 0.7:  # Horizontal must be ≥70% of vertical strength
        return
    
    # Process only strong horizontal movements
    angle = (math.degrees(math.atan2(x, -y)) + 360) % 360
    if 180 <= angle < 360:
        self._state.option_1 = True  # Left
        cfg.joy_response = "left"
    elif 0 <= angle < 180:
        self._state.option_2 = True  # Right
        cfg.joy_response = "right"
```

- Increased deadzone from 0.5 to 0.60 for stricter movement detection (`config.py`: `DZ_X = 0.60`, `DZ_Y = 0.60`).

**Motor Directional Filtering (Wrong-Direction Rejection):**
- **Motor tasks only:** Joystick movements in the opposite direction of the correct answer are now completely ignored (not registered as responses), similar to how vertical movements are ignored.
- **Sensorimotor tasks:** No change - both left and right movements are still accepted as before.
- Implementation uses expected direction filtering in `EventHandler`:

```python
# event_handler.py - Modified __init__ to accept expected_direction
class EventHandler:
    def __init__(self, expected_direction: str | None = None) -> None:
        self._expected_direction = expected_direction  # 'left', 'right', or None
        # ... joystick initialization ...

# _process_joystick() now filters based on expected_direction
if cfg.JOY_MODE == 2:
    if 180 <= angle < 360:  # Left movement detected
        if self._expected_direction is None or self._expected_direction == "left":
            self._state.option_1 = True
            cfg.joy_response = "left"
    elif 0 <= angle < 180:  # Right movement detected
        if self._expected_direction is None or self._expected_direction == "right":
            self._state.option_2 = True
            cfg.joy_response = "right"
```

```python
# motor.py - _run_phase() determines expected direction for motor tasks
def _run_phase(phase_name, duration_ms):
    # Motor directional filter: only accept joystick in correct direction
    expected_direction = None  # default for sensorimotor
    if condition == "motor" and phase_name == "stimulus" and key_correct is not None:
        expected_direction = "left" if key_correct == pygame.K_d else "right"
    
    event_handler = _reset_phase_input(expected_direction=expected_direction)
    # ... rest of phase logic ...
```

Example: If the correct answer for a motor trial is "left" (blue circle + mapping 1), moving the joystick to the right will have no effect - no response will be registered, exactly like moving it up or down.

**Trial-by-Trial Input Source Tracking:**
- The system automatically detects and records which input device (keyboard or joystick) was used for each individual trial.
- CSV columns are populated based on actual device used:
  - Joystick used → `input_source='joy'`, `stimulus_joy_response='left'/'right'`, `joy_correct='left'/'right'`
  - Keyboard used → `input_source='key'`, `stimulus_key_response='d'/'k'`, `key_correct=100/107`
  - No response → `input_source=None`, all response columns empty
- Participants can freely switch between keyboard and joystick across trials without any configuration changes.

Implementation details:

```python
# motor.py - Input source is determined per trial during response registration
def _register_first_response(phase_name, now_tick, phase_start_tick, phase_key):
    source = cfg._input_source  # Set by event_handler ('key' or 'joy')
    trial_input_source = source
    joy_raw = cfg.joy_response
    
    if phase_name == "stimulus":
        if source == "joy":
            stimulus_joy_response = joy_raw  # 'left' or 'right'
        else:
            stimulus_key_response = phase_key  # pygame.K_d or pygame.K_k
    # ... correctness evaluation ...

# saves.py - CSV columns adapt to actual input device
key_response = _first_non_empty(stimulus_key_response, isi_key_response)
joy_response = _first_non_empty(stimulus_joy_response, isi_joy_response)

key_correct_out = key_correct  # pygame key code or None
joy_correct_out = None
if key_correct == pygame.K_d:
    joy_correct_out = "left"
elif key_correct == pygame.K_k:
    joy_correct_out = "right"

record = {
    # ... other columns ...
    "key_correct": key_correct_out,
    "joy_correct": joy_correct_out,
    "stimulus_key_response": stimulus_key_response,
    "stimulus_joy_response": stimulus_joy_response,
    "input_source": trial_input_source,  # 'key', 'joy', or None
    # ...
}
```

Key features:
- `joy_correct` is always populated with the expected joystick direction ('left'/'right') based on mapping
- `key_correct` is always populated with the expected pygame key code (100 for K_d, 107 for K_k)
- Only the response columns corresponding to the actual input device used are filled
- Stage-level mutual exclusivity: if stimulus phase has input, ISI columns remain empty

**Motor Keyboard Filtering (Wrong-Key Rejection):**
- **Motor tasks only:** Keyboard presses of the wrong key (opposite to the correct answer) are now completely ignored, matching the joystick directional filtering behavior.
- **Sensorimotor tasks:** No change - both 'd' and 'k' keys are still accepted as before.
- Implementation uses expected key filtering in `EventHandler`:

```python
# event_handler.py - Modified __init__ to accept expected_key
class EventHandler:
    def __init__(self, expected_direction: str | None = None, expected_key: int | None = None) -> None:
        self._expected_direction = expected_direction  # 'left', 'right', or None
        self._expected_key = expected_key  # pygame.K_d, pygame.K_k, or None
        # ... initialization ...

# _process_keydown() now filters based on expected_key
def _process_keydown(self, key: int) -> None:
    # ... other key handling ...
    
    elif key == pygame.K_d:
        # Motor key filter: only accept if this is the expected key
        if self._expected_key is None or self._expected_key == pygame.K_d:
            self._state.option_1 = True
            cfg.key_response = pygame.key.name(key)
    
    elif key == pygame.K_k:
        # Motor key filter: only accept if this is the expected key
        if self._expected_key is None or self._expected_key == pygame.K_k:
            self._state.option_2 = True
            cfg.key_response = pygame.key.name(key)
```

```python
# motor.py - _run_phase() passes expected_key for keyboard filtering
def _run_phase(phase_name, duration_ms):
    expected_direction = None  # default for sensorimotor
    expected_key = None  # default for sensorimotor
    if condition == "motor" and phase_name == "stimulus" and key_correct is not None:
        expected_direction = "left" if key_correct == pygame.K_d else "right"
        expected_key = key_correct  # pygame.K_d or pygame.K_k
    
    event_handler = _reset_phase_input(expected_direction=expected_direction, expected_key=expected_key)
    # ... rest of phase logic ...
```

Example: If the correct answer for a motor trial is 'k' (red circle + mapping 1), pressing 'd' will have no effect - no response will be registered, exactly like pressing any other wrong key.

**Practice Structure Simplification (Motor & Sensorimotor):**

All practice phases have been simplified to single continuous sessions without accuracy checking, repeat loops, or intermediate instruction screens. This provides a more streamlined experience for participants.

**Motor Practice 1 (Blue Circles):**
- **Changed:** Single continuous 12-trial session (10 regular blue trials + 2 catch/no-go trials).
- **Removed:** Accuracy threshold checking and repeat loops - practice runs once regardless of performance.
- **Removed:** Intermediate instruction screens (6.png and 7.png).
- **Flow:** Instructions 1-5 → Practice 1 (12 trials) → Instruction 8 → Block 1 → ...

**Motor Practice 2 (Red Circles):**
- **Changed:** Single continuous 12-trial session (10 regular red trials + 2 catch/no-go trials).
- **Removed:** Accuracy threshold checking and repeat loops - practice runs once regardless of performance.
- **Removed:** Intermediate instruction screens (16.png and 17.png).
- **Flow:** ... → Block 1 → Instructions 9-15 → Practice 2 (12 trials) → Instruction 18 → Block 2 → ...

**Sensorimotor Practice (Mixed Colors):**
- **Changed:** Single continuous 24-trial session (10 red trials + 10 blue trials + 4 catch/no-go trials).
- **Removed:** Accuracy threshold checking and repeat loops - practice runs once regardless of performance.
- **Removed:** Intermediate instruction screens (6.png and 7.png).
- **Flow:** Instructions 1-5 → Practice (24 trials) → Instruction 8 → Block 3 → ... → Block 4

**Implementation Summary:**
- Trial generation now creates single practice arrays with combined trial counts
- Practice methods no longer check accuracy or set pass/fail flags
- Segment methods simplified to remove conditional branching and repeat logic
- All intermediate "repeat practice" instruction screens removed from instruction flow
- Catch trials randomly positioned within practice for each participant

**Benefits:**
- Simpler workflow for participants
- Consistent practice experience regardless of initial performance
- No confusion from repeated practice blocks or conditional branching
- Reduced total task duration while maintaining adequate practice exposure

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