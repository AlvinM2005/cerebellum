import pygame

from utils.paths import STIMULI_DIR, load_stimuli

# Contextual
C_STIMULI_PATH = STIMULI_DIR / "contextual"

# Mapping
MAPPING_1 = pygame.image.load(str(STIMULI_DIR / "CCC_Mapping_1.jpg"))
MAPPING_2 = pygame.image.load(str(STIMULI_DIR / "CCC_Mapping_2.jpg"))

# Fixation
CONTEXTUAL_FIXATION = pygame.image.load(str(C_STIMULI_PATH / "Fixation.png"))

# Uppercase letters
A_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "A_upper_pink.png"))
A_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "A_upper_yellow.png"))

E_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "E_upper_pink.png"))
E_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "E_upper_yellow.png"))

G_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "G_upper_pink.png"))
G_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "G_upper_yellow.png"))

I_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "I_upper_pink.png"))
I_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "I_upper_yellow.png"))

B_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "B_upper_pink.png"))
B_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "B_upper_yellow.png"))

P_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "P_upper_pink.png"))
P_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "P_upper_yellow.png"))

R_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "R_upper_pink.png"))
R_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "R_upper_yellow.png"))

U_UPPER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "U_upper_pink.png"))
U_UPPER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "U_upper_yellow.png"))

# Lowercase letters
A_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "a_lower_pink.png"))
A_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "a_lower_yellow.png"))

E_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "e_lower_pink.png"))
E_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "e_lower_yellow.png"))

G_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "g_lower_pink.png"))
G_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "g_lower_yellow.png"))

I_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "i_lower_pink.png"))
I_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "i_lower_yellow.png"))

B_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "b_lower_pink.png"))
B_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "b_lower_yellow.png"))

P_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "p_lower_pink.png"))
P_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "p_lower_yellow.png"))

R_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "r_lower_pink.png"))
R_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "r_lower_yellow.png"))

U_LOWER_PINK   = pygame.image.load(str(C_STIMULI_PATH / "u_lower_pink.png"))
U_LOWER_YELLOW = pygame.image.load(str(C_STIMULI_PATH / "u_lower_yellow.png"))

class ContextualStimuli:
    def __init__(self, version):
        self.version = version
        self.load_stimuli()
    
    def load_stimuli(self):
        if self.version == 1:
            self.CONTEXTUAL_STIMULI = [
                # Yellow (lowercase → V, uppercase → M)
                [A_UPPER_YELLOW, pygame.K_k, "actual"],
                [E_UPPER_YELLOW, pygame.K_k, "actual"],
                [G_UPPER_YELLOW, pygame.K_k, "actual"],
                [I_UPPER_YELLOW, pygame.K_k, "actual"],
                [B_UPPER_YELLOW, pygame.K_k, "actual"],
                [P_UPPER_YELLOW, pygame.K_k, "actual"],
                [R_UPPER_YELLOW, pygame.K_k, "actual"],
                [U_UPPER_YELLOW, pygame.K_k, "actual"],
                
                [A_LOWER_YELLOW, pygame.K_d, "actual"],
                [E_LOWER_YELLOW, pygame.K_d, "actual"],
                [G_LOWER_YELLOW, pygame.K_d, "actual"],
                [I_LOWER_YELLOW, pygame.K_d, "actual"],
                [B_LOWER_YELLOW, pygame.K_d, "actual"],
                [P_LOWER_YELLOW, pygame.K_d, "actual"],
                [R_LOWER_YELLOW, pygame.K_d, "actual"],
                [U_LOWER_YELLOW, pygame.K_d, "actual"],

                # Pink (vowel → V, consonant → M)
                [A_UPPER_PINK, pygame.K_d, "actual"],
                [E_UPPER_PINK, pygame.K_d, "actual"],
                [I_UPPER_PINK, pygame.K_d, "actual"],
                [U_UPPER_PINK, pygame.K_d, "actual"],
                [G_UPPER_PINK, pygame.K_k, "actual"],
                [B_UPPER_PINK, pygame.K_k, "actual"],
                [P_UPPER_PINK, pygame.K_k, "actual"],
                [R_UPPER_PINK, pygame.K_k, "actual"],

                [A_LOWER_PINK, pygame.K_d, "actual"],
                [E_LOWER_PINK, pygame.K_d, "actual"],
                [I_LOWER_PINK, pygame.K_d, "actual"],
                [U_LOWER_PINK, pygame.K_d, "actual"],
                [G_LOWER_PINK, pygame.K_k, "actual"],
                [B_LOWER_PINK, pygame.K_k, "actual"],
                [P_LOWER_PINK, pygame.K_k, "actual"],
                [R_LOWER_PINK, pygame.K_k, "actual"],

            ]
        else:
            self.CONTEXTUAL_STIMULI = [
                # Yellow (lowercase → V, uppercase → M)
                [A_UPPER_YELLOW, pygame.K_d, "actual"],
                [E_UPPER_YELLOW, pygame.K_d, "actual"],
                [G_UPPER_YELLOW, pygame.K_d, "actual"],
                [I_UPPER_YELLOW, pygame.K_d, "actual"],
                [B_UPPER_YELLOW, pygame.K_d, "actual"],
                [P_UPPER_YELLOW, pygame.K_d, "actual"],
                [R_UPPER_YELLOW, pygame.K_d, "actual"],
                [U_UPPER_YELLOW, pygame.K_d, "actual"],
                
                [A_LOWER_YELLOW, pygame.K_k, "actual"],
                [E_LOWER_YELLOW, pygame.K_k, "actual"],
                [G_LOWER_YELLOW, pygame.K_k, "actual"],
                [I_LOWER_YELLOW, pygame.K_k, "actual"],
                [B_LOWER_YELLOW, pygame.K_k, "actual"],
                [P_LOWER_YELLOW, pygame.K_k, "actual"],
                [R_LOWER_YELLOW, pygame.K_k, "actual"],
                [U_LOWER_YELLOW, pygame.K_k, "actual"],

                # Pink (vowel → V, consonant → M)
                [A_UPPER_PINK, pygame.K_k, "actual"],
                [E_UPPER_PINK, pygame.K_k, "actual"],
                [I_UPPER_PINK, pygame.K_k, "actual"],
                [U_UPPER_PINK, pygame.K_k, "actual"],
                [G_UPPER_PINK, pygame.K_d, "actual"],
                [B_UPPER_PINK, pygame.K_d, "actual"],
                [P_UPPER_PINK, pygame.K_d, "actual"],
                [R_UPPER_PINK, pygame.K_d, "actual"],

                [A_LOWER_PINK, pygame.K_k, "actual"],
                [E_LOWER_PINK, pygame.K_k, "actual"],
                [I_LOWER_PINK, pygame.K_k, "actual"],
                [U_LOWER_PINK, pygame.K_k, "actual"],
                [G_LOWER_PINK, pygame.K_d, "actual"],
                [B_LOWER_PINK, pygame.K_d, "actual"],
                [P_LOWER_PINK, pygame.K_d, "actual"],
                [R_LOWER_PINK, pygame.K_d, "actual"],

            ]


def get_contextual_mapping_background(mapping: int | None):
    if mapping == 2:
        return MAPPING_2
    return MAPPING_1
