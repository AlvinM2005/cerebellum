import pygame
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Motor
M_STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "motor") + os.sep

FIXATION = pygame.image.load(M_STIMULI_PATH + "circle_fixation.jpg")
BLUE = pygame.image.load(M_STIMULI_PATH + "circle_blue.jpg")
RED = pygame.image.load(M_STIMULI_PATH + "circle_red.jpg")
NOGO = pygame.image.load(M_STIMULI_PATH + "circle_white.jpg")

# Sensorimotor
SM_STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "sensorimotor") + os.sep

FIXATION = pygame.image.load(SM_STIMULI_PATH + "circle_fixation.jpg")
BLUE = pygame.image.load(SM_STIMULI_PATH + "circle_blue.jpg")
RED = pygame.image.load(SM_STIMULI_PATH + "circle_red.jpg")
NOGO = pygame.image.load(SM_STIMULI_PATH + "circle_white.jpg")

# Contextual
C_STIMULI_PATH = os.path.join(SCRIPT_DIR, "stimuli", "contextual") + os.sep

CONTEXTUAL_FIXATION = pygame.image.load(C_STIMULI_PATH + "fixation_black.jpg")

A_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "A_upper_pink.png")
A_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "A_upper_yellow.png")
A_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "A_upper_white.png")

E_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "E_upper_pink.png")
E_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "E_upper_yellow.png")
E_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "E_upper_white.png")

G_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "G_upper_pink.png")
G_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "G_upper_yellow.png")
G_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "G_upper_white.png")

I_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "I_upper_pink.png")
I_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "I_upper_yellow.png")
I_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "I_upper_white.png")

K_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "K_upper_pink.png")
K_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "K_upper_yellow.png")
K_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "K_upper_white.png")

P_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "P_upper_pink.png")
P_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "P_upper_yellow.png")
P_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "P_upper_white.png")

R_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "R_upper_pink.png")
R_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "R_upper_yellow.png")
R_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "R_upper_white.png")

U_UPPER_PINK = pygame.image.load(C_STIMULI_PATH + "U_upper_pink.png")
U_UPPER_YELLOW = pygame.image.load(C_STIMULI_PATH + "U_upper_yellow.png")
U_UPPER_WHITE = pygame.image.load(C_STIMULI_PATH + "U_upper_white.png")

A_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "a_lower_pink.png")
A_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "a_lower_yellow.png")
A_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "a_lower_white.png")

E_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "e_lower_pink.png")
E_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "e_lower_yellow.png")
E_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "e_lower_white.png")

G_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "g_lower_pink.png")
G_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "g_lower_yellow.png")
G_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "g_lower_white.png")

I_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "i_lower_pink.png")
I_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "i_lower_yellow.png")
I_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "i_lower_white.png")

K_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "k_lower_pink.png")
K_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "k_lower_yellow.png")
K_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "k_lower_white.png")

P_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "p_lower_pink.png")
P_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "p_lower_yellow.png")
P_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "p_lower_white.png")

R_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "r_lower_pink.png")
R_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "r_lower_yellow.png")
R_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "r_lower_white.png")

U_LOWER_PINK = pygame.image.load(C_STIMULI_PATH + "u_lower_pink.png")
U_LOWER_YELLOW = pygame.image.load(C_STIMULI_PATH + "u_lower_yellow.png")
U_LOWER_WHITE = pygame.image.load(C_STIMULI_PATH + "u_lower_white.png")

# ==== Contextual Stimuli List ====

CONTEXTUAL_STIMULI = [
    # Yellow (lowercase → V, uppercase → M)
    [A_UPPER_YELLOW, pygame.K_m, "actual"],
    [E_UPPER_YELLOW, pygame.K_m, "actual"],
    [G_UPPER_YELLOW, pygame.K_m, "actual"],
    [I_UPPER_YELLOW, pygame.K_m, "actual"],
    [K_UPPER_YELLOW, pygame.K_m, "actual"],
    [P_UPPER_YELLOW, pygame.K_m, "actual"],
    [R_UPPER_YELLOW, pygame.K_m, "actual"],
    [U_UPPER_YELLOW, pygame.K_m, "actual"],
    
    [A_LOWER_YELLOW, pygame.K_v, "actual"],
    [E_LOWER_YELLOW, pygame.K_v, "actual"],
    [G_LOWER_YELLOW, pygame.K_v, "actual"],
    [I_LOWER_YELLOW, pygame.K_v, "actual"],
    [K_LOWER_YELLOW, pygame.K_v, "actual"],
    [P_LOWER_YELLOW, pygame.K_v, "actual"],
    [R_LOWER_YELLOW, pygame.K_v, "actual"],
    [U_LOWER_YELLOW, pygame.K_v, "actual"],

    # Pink (vowel → V, consonant → M)
    [A_UPPER_PINK, pygame.K_v, "actual"],
    [E_UPPER_PINK, pygame.K_v, "actual"],
    [I_UPPER_PINK, pygame.K_v, "actual"],
    [U_UPPER_PINK, pygame.K_v, "actual"],
    [G_UPPER_PINK, pygame.K_m, "actual"],
    [K_UPPER_PINK, pygame.K_m, "actual"],
    [P_UPPER_PINK, pygame.K_m, "actual"],
    [R_UPPER_PINK, pygame.K_m, "actual"],

    [A_LOWER_PINK, pygame.K_v, "actual"],
    [E_LOWER_PINK, pygame.K_v, "actual"],
    [I_LOWER_PINK, pygame.K_v, "actual"],
    [U_LOWER_PINK, pygame.K_v, "actual"],
    [G_LOWER_PINK, pygame.K_m, "actual"],
    [K_LOWER_PINK, pygame.K_m, "actual"],
    [P_LOWER_PINK, pygame.K_m, "actual"],
    [R_LOWER_PINK, pygame.K_m, "actual"],

    # White (no-go)
    [A_UPPER_WHITE, None, "no_go"],
    [E_UPPER_WHITE, None, "no_go"],
    [G_UPPER_WHITE, None, "no_go"],
    [I_UPPER_WHITE, None, "no_go"],
    [K_UPPER_WHITE, None, "no_go"],
    [P_UPPER_WHITE, None, "no_go"],
    [R_UPPER_WHITE, None, "no_go"],
    [U_UPPER_WHITE, None, "no_go"],

    [A_LOWER_WHITE, None, "no_go"],
    [E_LOWER_WHITE, None, "no_go"],
    [G_LOWER_WHITE, None, "no_go"],
    [I_LOWER_WHITE, None, "no_go"],
    [K_LOWER_WHITE, None, "no_go"],
    [P_LOWER_WHITE, None, "no_go"],
    [R_LOWER_WHITE, None, "no_go"],
    [U_LOWER_WHITE, None, "no_go"],
]
