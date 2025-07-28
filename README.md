# Branch Amanda
07/27/2025
General changes

(Pending implementation in the 2D mental rotation and action prediction tasks)
1.	Results are now saved after each trial to prevent data loss in case of premature task termination.
2.	Relative paths are now used (via os.path) instead of hardcoded paths (e.g., ./stimuli/condition...).
3.	The experiment starts in full-screen mode; pressing ESC toggles full-screen on/off.
4.	Response keys changed from V/M to F/J.
5.	The results file now includes a mode column with values: full or demo. (Cognitive Control task does not currently support this?)
6.	Results files are saved using the format: ParticipantID_task_results.csv.
7.	The response mapping legend below the stimuli now reflects the F/J key layout.
8.	Practice feedback now appears below the stimuli instead of on a separate screen.
9.	Practice and experimental trials are saved in the same CSV file. The block column labels them as practice, block1, block2, etc.
10. Throughout the code and conditions files, the _flipped suffix was replaced with _2 to indicate version 2, and files without it were renamed to _1 to indicate version 1. Task version mappings are documented in the “Task List” file on Drive.
    
Task-specific changes: 3D Mental Rotation

·   	Added a fixation cross before stimulus presentation.
·   	All screens now have a black background to match the stimuli (instruction screens still need updating).
·   	Experimental condition labels changed:
o   "Normal" was renamed to "Same"
o   "Reversed" was renamed to "Different"
(Instruction texts need to be updated accordingly.)
·   	Code updated to store end_time for each trial.

Task-specific changes: Tapping

·   	The synchronization phase now continues until 12 taps are detected.
·   	The inter-tap interval during synchronization is stored in the column  “interval”.
 
