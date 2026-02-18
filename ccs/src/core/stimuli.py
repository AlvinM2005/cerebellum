import pygame

from utils.paths import STIMULI_DIR, load_stimuli

# Motor
M_STIMULI_PATH = STIMULI_DIR / "motor"

M_FIXATION = pygame.image.load(str(M_STIMULI_PATH / "circle_fixation.jpg"))
M_BLUE = pygame.image.load(str(M_STIMULI_PATH / "circle_blue.jpg"))
M_RED = pygame.image.load(str(M_STIMULI_PATH / "circle_red.jpg"))
M_NOGO = pygame.image.load(str(M_STIMULI_PATH / "circle_white.jpg"))


# Sensorimotor
class SensorimotorStimuli:
    def __init__(self, version):
        self.version = version
        self.load_stimuli()

    def load_stimuli(self):
        paths = load_stimuli(self.version)
        self.SM_STIMULI_PATH = paths["fixation"].parent

        # Load images
        self.SM_FIXATION = pygame.image.load(str(paths["fixation"]))
        self.SM_BLUE = pygame.image.load(str(paths["blue"]))
        self.SM_RED = pygame.image.load(str(paths["red"]))
        self.SM_NOGO = pygame.image.load(str(paths["white"]))
