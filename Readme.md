d#Progress Report (Nov 7, 2025)

# Main Changes (test Amanda)

- Code from Amanda's PEST implementation
- Added `TIM_final_results.csv` file to record final results for duration and loudness blocks. Does not include correct/incorrect results for last trial.
  - `TIM_results.csv` contains same contents as `TIM_final_results.csv` for additional data.
- Made presentation of standard and comparison stimuli fixed, does not randomize. Accurate to PASCAL code and documentation
- Evaluation of threshold to use is deterministic, set up upon initialization of PEST object, randomizing an array of 25 upper (1) and 25 lower (0) thresholds

d# Progress Report (Oct 11, 2025)

# Time Perception Task

## `stimuli.py`

### PEST Class

Contains PEST algorithm

- Initialize variables with `__init__` function
- Gets comparison interval
  - Set as choosing louder-longer/shorter-quieter comparison as random (will fix)
- Determines to change step (difficulty) with `should_change_level()` function
  - Uses E[Correct Trials] +- std (1.5) to get upper and lower bound
- `change_level()` function changes the difficulty based on `should_change_level()` function
- Calculates step size using PEST rules in `_calculate_step_size()` function

### Duration Task

`durationTask_stimuli()` - Function to handle duration blocks/practices

- Plays sound using `pygame.mixer.Sound()`
- Uses `evaluateResponse()` function
- Calling `PESTState` class to update conditions based on correct responses
  - Checks to change level
- Logs results in csv

### Loudness Task

`loudnessTask_stimuli()` - Function to handle loudness blocks/practices

- Changes volume using pygame's `set_volume()` function
- Uses `evaluateResponse()` function
- Calling `PESTState` class to update conditions based on correct responses
  - Checks to change level
- Logs results in csv

### Evaluate Response

- Captures participant response through handler function
- Determine correct answer
- Shows feedback if practice block

### Handler Functions

- ` _map_key_to_answer()`, `_wait_for_response_capture()`, `_wait_ms_with_events_wait()`, `_handle_events_only_interrupt()`
  - Same function type used in previous tasks
- `_wait_ms_with_events_capture()`
  - During stimulus, not capturing d/k responses

## `main_window.py`

- Changed `play_stimuli()` function to run stimulus as needed in `stimuli.py`
