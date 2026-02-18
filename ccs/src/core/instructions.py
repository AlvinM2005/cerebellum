import pygame

from utils.config import *
from utils.paths import instruction_page, load_instructions


class Instructions:
    def __init__(self, version):
        self.version = version

        # Initiate motor instructions
        self.M_INSTRUCTION_PATH = None
        self.M_ALL_INSTRUCTIONS = []
        self.M_INSTRUCTION_p1 = None
        self.M_INSTRUCTION_p2 = None

        # Initiate sensorimotor instructions
        self.SM_INSTRUCTION_PATH = None
        self.SM_ALL_INSTRUCTIONS = []
        self.SM_INSTRUCTION_p3 = None

    def generate_paths(self, version):
        # Motor
        M_ALL_INSTRUCTIONS = [
            pygame.image.load(str(p)) for p in load_instructions("motor", M_END_PAGE, version)
        ]

        M_INSTRUCTION_p1 = pygame.image.load(str(instruction_page("motor", "p1.jpg", version)))
        M_INSTRUCTION_p2 = pygame.image.load(str(instruction_page("motor", "p2.jpg", version)))

        # Sensorimotor
        SM_ALL_INSTRUCTIONS = [
            pygame.image.load(str(p)) for p in load_instructions("sensorimotor", SM_END_PAGE, version)
        ]

        SM_INSTRUCTION_p3 = pygame.image.load(str(instruction_page("sensorimotor", "p3.jpg", version)))

        self.M_INSTRUCTION_PATH = None
        self.M_ALL_INSTRUCTIONS = M_ALL_INSTRUCTIONS
        self.M_INSTRUCTION_p1 = M_INSTRUCTION_p1
        self.M_INSTRUCTION_p2 = M_INSTRUCTION_p2

        self.SM_INSTRUCTION_PATH = None
        self.SM_ALL_INSTRUCTIONS = SM_ALL_INSTRUCTIONS
        self.SM_INSTRUCTION_p3 = SM_INSTRUCTION_p3
