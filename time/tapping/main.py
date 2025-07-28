import pygame
from meta_parameters import *
from framework import *
from run_trial import *
from save_results import *

# Initialize pygame
pygame.init()
start_ticks = pygame.time.get_ticks() + 1000

# Set up the display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set up for results saving
all_results = []

# Get participant id
participant_id = get_participant_id(screen)

print()
print(participant_id)
print()

# Run the trial
synchronized_result, self_pace_result = run_trial(screen, start_ticks)
trial_result = []
synchronized_result[0] = 0
for result in synchronized_result:
    trial_result.append(["synchronized", result])
for result in self_pace_result:
    trial_result.append(["self_paced", result])
all_results.append([1, 1, "right", "control", trial_result]) # block, trial_number, hand, group, trial_result

# Save results
save_results(all_results, participant_id)
