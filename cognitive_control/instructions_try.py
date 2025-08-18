import pygame
import os
from meta_parameters import *

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

M_ALL_INSTRUCTIONS = []
M_INSTRUCTION_p1 = None
M_INSTRUCTION_p2 = None

SM_ALL_INSTRUCTIONS = []
SM_INSTRUCTION_p3 = None

C_ALL_INSTRUCTIONS = []
C_INSTRUCTION_p4 = None

def instruction():
    global M_ALL_INSTRUCTIONS, M_INSTRUCTION_p1, M_INSTRUCTION_p2
    global SM_ALL_INSTRUCTIONS, SM_INSTRUCTION_p3
    global C_ALL_INSTRUCTIONS, C_INSTRUCTION_p4

    # Motor
    M_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions", "motor")

    M_ALL_INSTRUCTIONS = [
        pygame.image.load(os.path.join(M_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1, M_END_PAGE + 1)
    ]

    M_INSTRUCTION_p1 = pygame.image.load(os.path.join(M_INSTRUCTION_PATH, "p1.jpg"))
    M_INSTRUCTION_p2 = pygame.image.load(os.path.join(M_INSTRUCTION_PATH, "p2.jpg"))

    # Sensorimotor
    SM_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions", "sensorimotor")

    SM_ALL_INSTRUCTIONS = [
        pygame.image.load(os.path.join(SM_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1,SM_END_PAGE + 1)
    ]

    SM_INSTRUCTION_p3 = pygame.image.load(os.path.join(SM_INSTRUCTION_PATH, "p3.jpg"))

    # Contextual

    C_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions", "contextual")

    C_ALL_INSTRUCTIONS = [
        pygame.image.load(os.path.join(C_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1,C_END_PAGE + 1)
    ]

    C_INSTRUCTION_p4 = pygame.image.load(os.path.join(C_INSTRUCTION_PATH, "p4.jpg"))

def reversed_instruction():
    global M_ALL_INSTRUCTIONS, M_INSTRUCTION_p1, M_INSTRUCTION_p2
    global SM_ALL_INSTRUCTIONS, SM_INSTRUCTION_p3
    global C_ALL_INSTRUCTIONS, C_INSTRUCTION_p4

    # Motor
    M_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed", "motor")

    M_ALL_INSTRUCTIONS = [
        pygame.image.load(os.path.join(M_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1, M_END_PAGE + 1)
    ]

    M_INSTRUCTION_p1 = pygame.image.load(os.path.join(M_INSTRUCTION_PATH, "p1.jpg"))
    M_INSTRUCTION_p2 = pygame.image.load(os.path.join(M_INSTRUCTION_PATH, "p2.jpg"))

    # Sensorimotor
    SM_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed", "sensorimotor")

    SM_ALL_INSTRUCTIONS = [
        pygame.image.load(os.path.join(SM_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1, SM_END_PAGE + 1)
    ]

    SM_INSTRUCTION_p3 = pygame.image.load(os.path.join(SM_INSTRUCTION_PATH, "p3.jpg"))

    # Contextual

    C_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed", "contextual")

    C_ALL_INSTRUCTIONS = [
        pygame.image.load(os.path.join(C_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1, C_END_PAGE + 1)
    ]

    C_INSTRUCTION_p4 = pygame.image.load(os.path.join(C_INSTRUCTION_PATH, "p4.jpg"))
