

d# Progress Report (Oct 13, 2025)

## 1. NBack (NB)

### 1. Configuration Updates (`src/utils/config.py`)
- **Added new constants:**
  - `TARGETS_PER_BLOCK = 6` - Exact number of targets per block
  - `NON_TARGETS_BASE = 14` - Base number of non-targets 
  - `MAX_CONSECUTIVE_REPEATS = 3` - Maximum allowed consecutive stimulus repetitions
  - `STIMULI_COUNT = 10` - Updated to reflect actual stimulus count

- **Updated trial counts** (both test and actual modes):
  - 1-back blocks: 21 trials (14 + 6 + 1)
  - 2-back blocks: 22 trials (14 + 6 + 2)  
  - 3-back blocks: 23 trials (14 + 6 + 3)
 
### Target Distribution
- **Practice blocks:**
  - **1-back practice:** 3 targets in 10 trials (30%)
  - **2-back practice:** 3 targets in 10 trials (30%)
  - **3-back practice:** 3 targets in 10 trials (30%)
- **Experimental blocks:**
  - **1-back:** 6 targets in 21 trials (28.6%)
  - **2-back:** 6 targets in 22 trials (27.3%)
  - **3-back:** 6 targets in 23 trials (26.1%)

### 2. New Core Function (`src/core/pull_stimuli.py`)
- **Added `_create_deterministic_sequence()`:**
  - Generates sequences with exactly 6 targets per block
  - Validates no more than 3 consecutive repetitions of same stimulus
  - Uses iterative regeneration until valid sequence found
  - Returns stimulus paths and corresponding answer sequence

- **Added `_create_practice_sequence()`:**
  - Generates practice sequences with exactly 3 targets per block
  - Uses same deterministic algorithm as experimental blocks
  - Specifically designed for 10-trial practice blocks
  - Maintains all validation constraints (consecutive repetitions)

- **Added `_is_practice_block()`:**
  - Automatically detects practice vs experimental blocks
  - Based on trial count: 10 trials = practice, 21-23 trials = experimental
  - Enables automatic switching between 3-target and 6-target generation

- **Enhanced timing structure:**
  - **Phase 1:** Stimulus display with response monitoring (500ms)
  - **Phase 2:** ISI period with continued response monitoring (2500ms)
  - **Total response window:** 3000ms (matching nBack-master standards)

### 3. Smart Feedback Timing (`src/core/test_flow.py`)
- **Implemented adaptive feedback strategy:**
  - **Immediate feedback:** When participant responds (any time within 2000ms)
  - **Delayed feedback:** When no response to targets (appears in last 1000ms of 3000ms window)
  - **Maximized response opportunity:** 2000ms uninterrupted response time for missed targets
  - **Standard feedback duration:** 1000ms for optimal visibility
    
 ### 4. 0-Back Task Removal
- **Completely removed 0-back condition** from the task
- **Updated task structure** to start directly with 1-back
- **Modified instruction flow** to begin at page 1 with 1-back instructions
- **Adjusted page mappings:** Total pages reduced from 51 to 39
- **Cleaned configuration:** Removed all 0-back related variables and functions
- **Updated block naming:** 1-back now uses PRACTICE1, BLOCK1, BLOCK2

### 5. Version 2 Elimination
- **Removed dual-version system:** Eliminated version-based participant assignment

d# Progress Report (Oct 9, 2025)

## 2. Motor timming (TAP)

- **Figma**
  
•	Instructions updated.

**General changes**

•	The classification of trials as successful or unsuccessful now depends only on the self-paced phase, excluding the synchronization phase.

•	The response key has been changed to “G”, as it is located in the center of the keyboard.

•	The instructions have been updated to specify that only the more affected hand should be tested (all 12 trials will be performed with the same hand).The details of this decision have been updated in the documentation sheet.



