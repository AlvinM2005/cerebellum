import pygame
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Motor
M_STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "motor")

FIXATION = pygame.image.load(os.path.join(M_STIMULI_PATH, "circle_fixation.jpg"))
BLUE = pygame.image.load(os.path.join(M_STIMULI_PATH, "circle_blue.jpg"))
RED = pygame.image.load(os.path.join(M_STIMULI_PATH, "circle_red.jpg"))
NOGO = pygame.image.load(os.path.join(M_STIMULI_PATH, "circle_white.jpg"))

# Sensorimotor
SM_STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "sensorimotor")

FIXATION = pygame.image.load(os.path.join(SM_STIMULI_PATH, "circle_fixation.jpg"))
BLUE = pygame.image.load(os.path.join(SM_STIMULI_PATH, "circle_blue.jpg"))
RED = pygame.image.load(os.path.join(SM_STIMULI_PATH, "circle_red.jpg"))
NOGO = pygame.image.load(os.path.join(SM_STIMULI_PATH, "circle_white.jpg"))

# Contextual
C_STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "contextual")

# Fixation
CONTEXTUAL_FIXATION = pygame.image.load(os.path.join(C_STIMULI_PATH, "fixation_black.jpg"))

# Uppercase letters
A_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "A_upper_pink.png"))
A_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "A_upper_yellow.png"))
A_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "A_upper_white.png"))

E_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "E_upper_pink.png"))
E_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "E_upper_yellow.png"))
E_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "E_upper_white.png"))

G_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "G_upper_pink.png"))
G_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "G_upper_yellow.png"))
G_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "G_upper_white.png"))

I_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "I_upper_pink.png"))
I_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "I_upper_yellow.png"))
I_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "I_upper_white.png"))

B_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "B_upper_pink.png"))
B_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "B_upper_yellow.png"))
B_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "B_upper_white.png"))

P_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "P_upper_pink.png"))
P_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "P_upper_yellow.png"))
P_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "P_upper_white.png"))

R_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "R_upper_pink.png"))
R_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "R_upper_yellow.png"))
R_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "R_upper_white.png"))

U_UPPER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "U_upper_pink.png"))
U_UPPER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "U_upper_yellow.png"))
U_UPPER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "U_upper_white.png"))

# Lowercase letters
A_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "a_lower_pink.png"))
A_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "a_lower_yellow.png"))
A_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "a_lower_white.png"))

E_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "e_lower_pink.png"))
E_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "e_lower_yellow.png"))
E_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "e_lower_white.png"))

G_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "g_lower_pink.png"))
G_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "g_lower_yellow.png"))
G_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "g_lower_white.png"))

I_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "i_lower_pink.png"))
I_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "i_lower_yellow.png"))
I_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "i_lower_white.png"))

B_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "b_lower_pink.png"))
B_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "b_lower_yellow.png"))
B_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "b_lower_white.png"))

P_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "p_lower_pink.png"))
P_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "p_lower_yellow.png"))
P_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "p_lower_white.png"))

R_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "r_lower_pink.png"))
R_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "r_lower_yellow.png"))
R_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "r_lower_white.png"))

U_LOWER_PINK   = pygame.image.load(os.path.join(C_STIMULI_PATH, "u_lower_pink.png"))
U_LOWER_YELLOW = pygame.image.load(os.path.join(C_STIMULI_PATH, "u_lower_yellow.png"))
U_LOWER_WHITE  = pygame.image.load(os.path.join(C_STIMULI_PATH, "u_lower_white.png"))

# ==== Contextual Stimuli List ====

CONTEXTUAL_STIMULI = [
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

    # White (no-go)
    [A_UPPER_WHITE, None, "no_go"],
    [E_UPPER_WHITE, None, "no_go"],
    [G_UPPER_WHITE, None, "no_go"],
    [I_UPPER_WHITE, None, "no_go"],
    [B_UPPER_WHITE, None, "no_go"],
    [P_UPPER_WHITE, None, "no_go"],
    [R_UPPER_WHITE, None, "no_go"],
    [U_UPPER_WHITE, None, "no_go"],

    [A_LOWER_WHITE, None, "no_go"],
    [E_LOWER_WHITE, None, "no_go"],
    [G_LOWER_WHITE, None, "no_go"],
    [I_LOWER_WHITE, None, "no_go"],
    [B_LOWER_WHITE, None, "no_go"],
    [P_LOWER_WHITE, None, "no_go"],
    [R_LOWER_WHITE, None, "no_go"],
    [U_LOWER_WHITE, None, "no_go"],
]
