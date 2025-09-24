d# Progress Report (Sep 12, 2025)

## 1. Motor timming (TAP)

- **Figma**
  
•	Corrected the task diagram and included estimated timing for each block in the instructions.

•	Revised instructions. The keyboard mappings remain with v and m.

**General changes**

•	Changed code comments from Mandarin to English.

•	Changed relative paths to absolute paths in the instructions.

•	Corrected the output filename format to ParticipantID_TAP_results.

•	Added a variable called "key_response".

**File Handling**

•	The code automatically detects if a results file already exists for a given participant ID and creates a new file with an incremental suffix instead of overwriting the existing data.

•	How it Works:

 1.Base filename generation: Creates the standard filename format [participantID]_2D_results.csv.
 
 2.Collision detection: Checks if the file already exists in the results directory.
 
 3.Automatic versioning: If the file exists, it appends _2, _3, _4, etc., until it finds an available filename.
 
 4.Global filename tracking: Stores the final unique filename in a global variable so all trial data gets saved to the same file throughout the experiment.

**Response detection fixed**

•	Problem: Pygame was intermittently failing to detect key presses during synchronized tapping trials, resulting in empty "key_response" fields despite users actually pressing keys. Single event-based detection (pygame.event.get()) was missing some keypress events.

•	Solution: Response logging was made more robust to prevent any missed inputs. The function run_synchronized in run_trial.py was modified:

-Added key_was_pressed tracking variable.

-Improved event polling with events = pygame.event.get().

-Added fallback detection: if keys[target_key] and not key_was_pressed:

-Added pygame.time.wait(1) for better CPU management (1 ms delay tops).



