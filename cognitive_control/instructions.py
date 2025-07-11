import pygame
from meta_parameters import *

# Motor
M_INSTRUCTION_PATH = "./instructions/motor/"

M_ALL_INSTRUCTIONS = [
    pygame.image.load(f"{M_INSTRUCTION_PATH}{i}.jpg") for i in range(1, M_END_PAGE + 1)
]

M_INSTRUCTION_p1 = pygame.image.load(f"{M_INSTRUCTION_PATH}p1.jpg")
M_INSTRUCTION_p2 = pygame.image.load(f"{M_INSTRUCTION_PATH}p2.jpg")

# Sensorimotor
SM_INSTRUCTION_PATH = "./instructions/sensorimotor/"

SM_ALL_INSTRUCTIONS = [
    pygame.image.load(f"{SM_INSTRUCTION_PATH}{i}.jpg") for i in range(1,SM_END_PAGE + 1)
]

SM_INSTRUCTION_p3 = pygame.image.load(f"{SM_INSTRUCTION_PATH}p3.jpg")

# Contextual

C_INSTRUCTION_PATH = "./instructions/contextual/"

C_ALL_INSTRUCTIONS = [
    pygame.image.load(f"{C_INSTRUCTION_PATH}{i}.jpg") for i in range(1,C_END_PAGE + 1)
]

C_INSTRUCTION_p4 = pygame.image.load(f"{C_INSTRUCTION_PATH}p4.jpg")
