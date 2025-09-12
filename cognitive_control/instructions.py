import pygame
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
from meta_parameters import *

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

        # Initiate contextual instructions
        self.C_INSTRUCTION_PATH = None
        self.C_ALL_INSTRUCTIONS = []
        self.C_INSTRUCTION_p4 = None
    
    def generate_paths(self, version):

        if version == 1:

            # Motor
            M_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions", "motor")

            # Sensorimotor
            SM_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions", "sensorimotor")

            # Contextual
            C_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions", "contextual")
        
        else: # version == 2 or wrong format
            # Motor
            M_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed", "motor")

            # Sensorimotor
            SM_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed", "sensorimotor")

            # Contextual
            C_INSTRUCTION_PATH = os.path.join(SCRIPT_DIR, "instructions_reversed", "contextual")
        
        # Motor
        M_ALL_INSTRUCTIONS = [
                pygame.image.load(os.path.join(M_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1, M_END_PAGE + 1)
            ]

        M_INSTRUCTION_p1 = pygame.image.load(os.path.join(M_INSTRUCTION_PATH, "p1.jpg"))
        M_INSTRUCTION_p2 = pygame.image.load(os.path.join(M_INSTRUCTION_PATH, "p2.jpg"))

        # Sensorimotor
        SM_ALL_INSTRUCTIONS = [
            pygame.image.load(os.path.join(SM_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1,SM_END_PAGE + 1)
        ]

        SM_INSTRUCTION_p3 = pygame.image.load(os.path.join(SM_INSTRUCTION_PATH, "p3.jpg"))

        # Contextual
        C_ALL_INSTRUCTIONS = [
            pygame.image.load(os.path.join(C_INSTRUCTION_PATH, f"{i}.jpg")) for i in range(1,C_END_PAGE + 1)
        ]

        C_INSTRUCTION_p4 = pygame.image.load(os.path.join(C_INSTRUCTION_PATH, "p4.jpg"))

        self.M_INSTRUCTION_PATH = M_INSTRUCTION_PATH
        self.M_ALL_INSTRUCTIONS = M_ALL_INSTRUCTIONS
        self.M_INSTRUCTION_p1 = M_INSTRUCTION_p1
        self.M_INSTRUCTION_p2 = M_INSTRUCTION_p2

        # Initiate sensorimotor instructions
        self.SM_INSTRUCTION_PATH = SM_INSTRUCTION_PATH
        self.SM_ALL_INSTRUCTIONS = SM_ALL_INSTRUCTIONS
        self.SM_INSTRUCTION_p3 = SM_INSTRUCTION_p3

        # Initiate contextual instructions
        self.C_INSTRUCTION_PATH = C_INSTRUCTION_PATH
        self.C_ALL_INSTRUCTIONS = C_ALL_INSTRUCTIONS
        self.C_INSTRUCTION_p4 = C_INSTRUCTION_p4
