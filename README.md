ACTION PREDICTION 
1.	Moved variable initialization to proper location

•	Moved VERSION, INSTRUCTION_DIR, RESULT_DIR, and CONDITION_DIR initialization from the bottom of the file to before they are first used.
•	Added participant_info = participant_id assignment to ensure the variable is properly defined.

2.	Fixed execution order

•	Rearranged the code so that all variables are defined before any functions that use them are called.
•	Moved the participant ID collection and processing logic to execute in the correct sequence.

3.	Corrected global variable assignment

•	Fixed the global_end_time assignment to occur at the proper time (after task completion).
•	Removed duplicate/incorrect global_start_time assignment.                                          
4. Absolute paths for the videos
•	Convert relative paths (./stimuli/...) to absolute path.

5.	Unified key behavior across versions 

•	Removed version-dependent key mapping (VERSION 1 vs VERSION 2 differences). 
•	Set consistent mapping: D = Left, K = Right for all versions. 
•	Copied normal CSV files over "_flipped" variants to ensure identical key mappings.
•	Changed all CSV files from using "v"/"m" keys to "d"/"k" keys to match code expectations. Updated both  /stimuli/conditions/ and /condition/conditions/ directories.

6.	Improved response mapping layout 

•	Split key letters and direction labels into separate lines for cleaner display.

7.	Improved Practice Feedback:

•	Feedback now displays on same screen as D/K mapping during practice trials.
•	Positioned feedback icon centered below response options.
•	Feedback duration (1000ms).
•	Standardized feedback icon size (102x102px). 
•	“Too slow” feedback updated to show the words instead of icon
 
8.	ESC Key Functionality

•	Ensured consistent ESC functionality across all experiment phases


9.	Real-time data saving

•	Data I saved after each trial to preserve results even if experiment is interrupted middle-session

10.	Unified results for both practice and evaluation trials

•	The variable “block” was added to the results, with the values “practice” or “block1”, “block2”, etc.
•	The variable “type” was added to the results, with the values “practice” or “test”.
•	The variable “mode” was added to the results, with the vales “full” or “demo” for actual or test modes. 

11.	Updated video difficulty labels

•	 Videos where the player misses the goal are now labeled as "easy" trials, while videos where the player successfully scores are labeled as "hard" trials in the “difficulty” variable. 

12.	Reduced reading time in instruction screens

•	I reduced the waiting time for reading the instructions to 1 s, just to avoid accidental key presses.

13.	Change in the format of the name in the results sheet

•	The results sheet now includes the test name after the participant’s name. The initials listed in the “Task List” document on Drive were used. For example, in action prediction: YC001_SOC_results.

14.	Correction of end_time variable

•	An end_time was created for each trial. Previously, there was a bug and this variable was only generated at the end of the experiment, so the column remained empty.

     15. Blocks

•	The task was divided into 4 blocks of 60 trials each, instead of 2 blocks of 180 trials each, to reduce patient fatigue. This was updated for the MODE = actual, for MODE= test there are still 2 blocks.
16. Automatic file versioning system

•	The code automatically detects if a results file already exists for a given participant ID and creates a new file with an incremental suffix instead of overwriting the existing data.
•	How it Works:
a)	Base filename generation: Creates the standard filename format [participantID]_2D_results.csv.
b)	Collision detection: Checks if the file already exists in the results directory.
c)	Automatic versioning: If the file exists, it appends _2, _3, _4, etc., until it finds an available filename.
d)	Global filename tracking: Stores the final unique filename in a global variable so all trial data gets saved to the same file throughout the experiment.

17. Exit

•	Exit the task by pressing the space bar on the last screen.


MENTAL ROTATION 2D

. Absolute paths for the feedback and stimuli in the actual MODE
•	Convert relative paths to absolute path.
2. Mapping labels changed
•	The labels “same” and “different” were changed to “normal” and “mirrored.” “Same” and “different” are only for the 3D version.

3. Change in the format of the name in the results sheet

•	The results sheet now includes the test name after the participant’s name. The initials listed in the “Task List” document on Drive were used. For example, in mental rotation 2D: YC001_2D_results.

4. Reduced reading time in instruction screens

•	I reduced the waiting time for reading the instructions to 1 s, just to avoid accidental key presses.

5. Unified results 

•	The variable “block” was added to the results, with the values “practice” or “block1”, “block2”, etc.
•	The variable “type” was added to the results, with the values “practice” or “test”.
•	The variable “mode” was added to the results, with the vales “full” or “demo” for actual or test modes. 


6. Automatic file versioning system

•	The code automatically detects if a results file already exists for a given participant ID and creates a new file with an incremental suffix instead of overwriting the existing data.
•	How it Works:
e)	Base filename generation: Creates the standard filename format [participantID]_2D_results.csv.
f)	Collision detection: Checks if the file already exists in the results directory.
g)	Automatic versioning: If the file exists, it appends _2, _3, _4, etc., until it finds an available filename.
h)	Global filename tracking: Stores the final unique filename in a global variable so all trial data gets saved to the same file throughout the experiment.


7. Corrected condition files

•	The “condition” column was fixed to recognize “mirrored” and “normal.” Previously, everything had the value “normal.”


8. Blocks

•	The task was divided into 4 blocks of 48 trials each, instead of 2 blocks of 96 trials each, to reduce patient fatigue. This was updated for the MODE = actual, for MODE= test there are 2 blocks.

9. Time settings

•	Max time to respond updated to 5000 ms
•	Fixation cross 500 ms

10. Exit

•	Exit the task by pressing the space bar on the last screen.

MENTAL ROTATION 3D

1.	General format

•	Fixation cross with the same format as bidimensional. 

2.	Condition files corrected

•	The variable “key_correct” in all condition files were correct with the new mapping d and k.

3.	Exit

•	Exit the task by pressing the space bar on the last screen.

4.	Unified results for both practice and evaluation trials

•	The variable “block” was added to the results, with the values “practice” or “block1”, “block2”, etc.
•	The variable “type” was added to the results, with the values “practice” or “test”.
•	The variable “mode” was added to the results, with the vales “full” or “demo” for actual or test modes. 
5. Automatic file versioning system

•	The code automatically detects if a results file already exists for a given participant ID and creates a new file with an incremental suffix instead of overwriting the existing data.
•	How it Works:
i)	Base filename generation: Creates the standard filename format [participantID]_2D_results.csv.
j)	Collision detection: Checks if the file already exists in the results directory.
k)	Automatic versioning: If the file exists, it appends _2, _3, _4, etc., until it finds an available filename.
l)	Global filename tracking: Stores the final unique filename in a global variable so all trial data gets saved to the same file throughout the experiment.

6. Reduction in the number of trials per block. 

•	The stimuli were reduced to 48 per block, 12 per angle (6 identical and 6 mirrored), resulting in a total of 96 trials plus practice.


COGNITIVE CONTROL

Absolute paths for the feedback and stimuli in the actual MODE
•	Convert relative paths to absolute path.

2. Full screen problem corrected

•	The cognitive control task had stimulus centering issues in fullscreen mode because images were displayed at fixed position (0,0) with fixed dimensions (1516x852) that didn't adapt to different screen resolutions. I solved this by: 1) Creating a get_scaled_stimulus() function that automatically scales images to fit within 90% of the current screen size while maintaining aspect ratio, 2) Replacing all screen.blit(image, (0,0)) calls with proper centering using image.get_rect(center=screen_rect.center)

3. Real-time data saving

•	Data I saved after each trial to preserve results even if experiment is interrupted middle-session

4. ESC Key Functionality

•	Ensured consistent ESC functionality across all experiment phases

5.	Delayed problem fixed (MODE = actual)

•	The key_logging() function was designed to wait for the full allocated time duration (e.g., 2000ms) even after a key was pressed. This caused:

•	User presses key and system registers response but continues waiting Feedback/next trial delayed until full time expires. Solution Implemented: Modified key_logging() to break immediately after receiving a valid key response.

6.	Window close button fix

•	When switching from fullscreen to windowed mode using ESC, pygame displays a window with a close button (X), but the key_logging() function was only handling keyboard events (pygame.KEYDOWN) and not window events (pygame.QUIT). This meant users could close the window during instruction screens but not during trials (fixation, stimulus, ISI phases). The fix involved adding pygame.QUIT event handling to the key_logging() function, which immediately calls pygame.quit() and quit() when the close button is clicked. 

7. Automatic file versioning system

•	The code automatically detects if a results file already exists for a given participant ID and creates a new file with an incremental suffix instead of overwriting the existing data.
•	How it Works:
m)	Base filename generation: Creates the standard filename format [participantID]_2D_results.csv.
n)	Collision detection: Checks if the file already exists in the results directory.
o)	Automatic versioning: If the file exists, it appends _2, _3, _4, etc., until it finds an available filename.
p)	Global filename tracking: Stores the final unique filename in a global variable so all trial data gets saved to the same file throughout the experiment.

8.	Keys

•	Block any key other than D and K during the trials.

9.	Results file corrected

•	Modified key_to_str() function to convert pygame key codes (100, 107) to readable letters ("d", "k") and updated hand assignment logic (D=left, K=right). Changed correct calculation from boolean (True/False) to numeric values (1/0) for proper CSV.

10.	Change in the format of the name in the results sheet

•	The results sheet now includes the test name after the participant’s name. The initials listed in the “Task List” document on Drive were used. For example, in action prediction: YC001_SOC_results.

*IN ALL TASKS ACTUAL_READ_TIME = 1000 ms*






