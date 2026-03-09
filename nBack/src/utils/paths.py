# ./src/utils/paths.py
"""
Path management module.

This module defines and centralizes all filesystem paths used throughout the application.
"""


from pathlib import Path

import utils.config as cfg


# ---------- Directories ----------

# project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# resources
RESOURCES_DIR = PROJECT_ROOT / "resources"

# results
RESULTS_DIR = PROJECT_ROOT / "results"

# logs
LOGS_DIR = PROJECT_ROOT / "logs"

# TODO: Add additional paths if necessary


# ---------- Load Instrucrtions ----------

# Load general instruction pages
INSTRUCTIONS_DIR = RESOURCES_DIR / "instructions"
INSTRUCTIONS = []
for i in range(cfg.INSTRUCTIONS_COUNT):
    INSTRUCTIONS.append(INSTRUCTIONS_DIR / f"{i+1}.jpg")

# Load special instruction page(s)
PRACTICE_INSTRUCTIONS = INSTRUCTIONS_DIR / "practice.jpg"
TEST_INSTRUCTIONS = INSTRUCTIONS_DIR / "test.jpg"
PRACTICE_BREAK = INSTRUCTIONS_DIR / "practice.jpg"  # Pause screen between practice blocks

# TODO: Load additional instructions configurations if necessary


# ---------- Load Stimuli ----------

STIMULI_DIR = RESOURCES_DIR / "stimuli"

STIM_BG = STIMULI_DIR / "stim_bg.png"
STIM_D = STIMULI_DIR / "nb_d.png"
STIM_F = STIMULI_DIR / "nb_f.png"
STIM_H = STIMULI_DIR / "nb_h.png"
STIM_J = STIMULI_DIR / "nb_j.png"
STIM_K = STIMULI_DIR / "nb_k.png"
STIM_L = STIMULI_DIR / "nb_l.png"
STIM_M = STIMULI_DIR / "nb_m.png"
STIM_S = STIMULI_DIR / "nb_s.png"
STIM_T = STIMULI_DIR / "nb_t.png"
STIM_V = STIMULI_DIR / "nb_v.png"

STIMULI = [STIM_D, STIM_F, STIM_H, STIM_J, STIM_K, STIM_L, STIM_M, STIM_S, STIM_T, STIM_V]


# ---------- Load Feedback ----------

FEEDBACK_DIR = RESOURCES_DIR / "feedback"

FB_CORRECT = FEEDBACK_DIR / "correct.png"
FB_INCORRECT = FEEDBACK_DIR / "incorrect.png"

BEEP = FEEDBACK_DIR / "beep.wav"


# ---------- Load Admin ----------

ADMIN_DIR = RESOURCES_DIR / "admin"

ADMIN_1 = ADMIN_DIR / "Admin_1.png"
ADMIN_2 = ADMIN_DIR / "Admin_2.png"
ADMIN_L = ADMIN_DIR / "Admin_L.png"
ADMIN_R = ADMIN_DIR / "Admin_R.png"
ADMIN_LL = ADMIN_DIR / "Admin_LL.png"
ADMIN_LR = ADMIN_DIR / "Admin_LR.png"
ADMIN_RL = ADMIN_DIR / "Admin_RL.png"
ADMIN_RR = ADMIN_DIR / "Admin_RR.png"
ADMIN_PLEASE_L = ADMIN_DIR / "Admin_Please_L.png"
ADMIN_PLEASE_R = ADMIN_DIR / "Admin_Please_R.png"

ADMIN_LAN         = ADMIN_DIR / "Admin_Lan.png"
ADMIN_LAN_SPANISH = ADMIN_DIR / "Admin_Lan_Español.png"
ADMIN_LAN_ENGLISH = ADMIN_DIR / "Admin_Lan_English.png"
ADMIN_GRP         = ADMIN_DIR / "Admin_Grp.png"
ADMIN_GRP_1       = ADMIN_DIR / "Admin_Grp1.png"
ADMIN_GRP_2       = ADMIN_DIR / "Admin_Grp2.png"
ADMIN_GRP_3       = ADMIN_DIR / "Admin_Grp3.png"
ADMIN_GRP_4       = ADMIN_DIR / "Admin_Grp4.png"
ADMIN_GRP_5       = ADMIN_DIR / "Admin_Grp5.png"
ADMIN_GRP_6       = ADMIN_DIR / "Admin_Grp6.png"
ADMIN_SESSION     = ADMIN_DIR / "Admin_Session.png"
ADMIN_SESSION_1   = ADMIN_DIR / "Admin_Session1.png"
ADMIN_SESSION_2   = ADMIN_DIR / "Admin_Session2.png"
ADMIN_SESSION_3   = ADMIN_DIR / "Admin_Session3.png"
ADMIN_SESSION_4   = ADMIN_DIR / "Admin_Session4.png"
ADMIN_SESSION_5   = ADMIN_DIR / "Admin_Session5.png"
ADMIN_SESSION_6   = ADMIN_DIR / "Admin_Session6.png"
ADMIN_SESSION_7   = ADMIN_DIR / "Admin_Session7.png"
ADMIN_SESSION_8   = ADMIN_DIR / "Admin_Session8.png"
ADMIN_SESSION_9   = ADMIN_DIR / "Admin_Session9.png"
