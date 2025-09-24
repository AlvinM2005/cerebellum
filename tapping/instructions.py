import pygame
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Instructions settings
INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions")
REVERSED_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed")
TOTAL_INSTRUCTIONS_PAGE = 25

# Page nums
PRACTICE_1 = 6 # Practice 1 (2 trials, left hand) begins after page ~
BLOCK_1_1 = 9 # Block 1-1 (3 trials, left hand) begins after page ~
BLOCK_1_2 = 12 # Block 1-2 (3 trials, left hand) begins after page ~
BREAK = 13 # Break begins after page ~
PRACTICE_2 = 18 # Practice 2 (2 trials, right hand) begins after page ~
BLOCK_2_1 = 21 # Block 2-1 (3 trials, right hand) begins after page ~
BLOCK_2_2 = 24 # Block 2-1 (3 trials, right hand) begins after page ~

def get_instructions(instruction_path):
    instructions = []

    for i in range(1, TOTAL_INSTRUCTIONS_PAGE + 1):
        instructions.append([pygame.image.load(os.path.join(instruction_path, f"{i}.jpg")), None])

    instructions[PRACTICE_1 - 1][1] = "practice_1"
    instructions[PRACTICE_2 - 1][1] = "practice_2"
    instructions[BLOCK_1_1 - 1][1] = "block1_1"
    instructions[BLOCK_1_2 - 1][1] = "block1_2"
    instructions[BLOCK_2_1 - 1][1] = "block2_1"
    instructions[BLOCK_2_2 - 1][1] = "block2_2"
    instructions[BREAK - 1][1] = "break"

    return instructions
