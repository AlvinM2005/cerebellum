# Progress Report

# Soccer Predition Task 5/7/26

#### Note: Add "videos" folder in soccer_prediction/resources/stimuli/ , and add soccer videos for task to work

### About Task:

#### Mapping

- Contains two versions of SOC_Guide
  - Currently using transparent version that overlays video (a bit difficult to see, may need changing)

#### Simulus Presentation

- Can change combination constraints in 'config.py'
- Code is in 'prep_stimuli.py' in the utils folder
- 4 second freeze frame for response time for all videos

#### Results File

- Accuracy based on current trials within block
- Difficulty (miss/goal)
- Condition (left/right)
- Reaction time
- File name used

# Semantic Decision Task

### Updates

- Added "SPACE to continue" in post-block performance screen
- Mapping on last word
- Mapping files updated to .png
- Added other features to results file:
  - Original item number
  - Spelling modified
  - Word count
  - Word frequency
  - Original dataset
  - Sentence
  - Last word
  - Number of letters

### Old

#### (2/19/26):

- Changed admin screen
- Moved version in results filename to end
- Added new sentence dataset (ListA and ListB)
  - Sentence list presentation based on modulo 4 of last number in PID
- Added mapping guide during stimulus presentation
- Post-block performance summary
  - Shows accuracy (00.00%) and average reaction time (0000 ms)
- Fixed MODE's value of "actual" to "full"
- Updated instructions

#### (2/13/26):

- Changed 3 blocks of experimental (30 stimuli in each) to 2 blocks of experimental (45 blocks in each)
  - Edited instruction pages (deleted pages for 2nd block)
- Added in date in for the results file name after PID, version, and task name
  - eg: "ctrl01_SD_results_2026_02_03.csv"
- Will new .csv (v2,v3,...) if PID is same in that day
- Changed joystick y-axis deadzone to 0.75
- Experiment closes after 10 seconds or participant pressing SPACE key
- Program will detect if a joystick is present, changing results file: "response" and "correct" answers to joystick responses column
