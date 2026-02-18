import pygame

from utils.config import *
from utils.paths import instruction_page, load_instructions

class Instructions:
    
    def __init__(self, version):
        self.version = version

        # Initiate contextual instructions
        self.C_INSTRUCTION_PATH = None
        self.C_ALL_INSTRUCTIONS = []
        self.C_INSTRUCTION_p4 = None
    
    def generate_paths(self, version):

        # Contextual
        C_ALL_INSTRUCTIONS = [
            pygame.image.load(str(p)) for p in load_instructions("contextual", C_END_PAGE, version)
        ]

        C_INSTRUCTION_p4 = pygame.image.load(str(instruction_page("contextual", "p1.jpg", version)))

        # Initiate contextual instructions
        self.C_INSTRUCTION_PATH = None
        self.C_ALL_INSTRUCTIONS = C_ALL_INSTRUCTIONS
        self.C_INSTRUCTION_p4 = C_INSTRUCTION_p4
