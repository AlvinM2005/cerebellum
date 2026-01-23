# ./src/core/gss_practice.py

from typing import Tuple
import pygame
import random
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import toggle_full_screen, show_instruction_page, interactive_instruction_page
from core.show_feedback import show_feedback
from core.saves import update_save

logger = get_logger("./src/core/gss_practice") # create logger

def load_gss_practice_stimulus(screen: pygame.Surface, img_path: Path):
    # Load image
    p = Path(img_path)
    if not p.exists():
        logger.error(f"show_feedback: file not found -> {img_path}")
        return None

    try:
        img = pygame.image.load(str(p)).convert_alpha()
    except Exception as e:
        logger.error(f"show_feedback: failed to load image -> {img_path} | {e}")
        return None

    # Resize image (max_W = w / max_H = h)
    w, h = screen.get_size()
    orig_w, orig_h = img.get_size()
    if orig_w <= 0 or orig_h <= 0:
        logger.error(f"show_feedback: invalid image size -> {img_path} ({orig_w}x{orig_h})")
        return None

    scale = min(w / orig_w, h / orig_h)
    new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    if new_size != (orig_w, orig_h):
        img = pygame.transform.smoothscale(img, new_size)

    # Compute center
    cx, cy = w / 2, h / 2
    center = (int(cx), int(cy))

    # Fill the screen with gray background (avoid black boarder)
    screen.fill(cfg.GRAY_RGB)

    # Place image at target location
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)


def load_gss_practice_goal_marker(screen: pygame.Surface, img_path: Path):
    screen.fill(cfg.GRAY_RGB)

    # Load image
    p = Path(img_path)
    if not p.exists():
        logger.error(f"show_feedback: file not found -> {img_path}")
        return None

    try:
        img = pygame.image.load(str(p)).convert_alpha()
    except Exception as e:
        logger.error(f"show_feedback: failed to load image -> {img_path} | {e}")
        return None

    # Resize image (max_W = w / max_H = h)
    max_W, max_H = cfg.MARKER_W, cfg.MARKER_H
    orig_w, orig_h = img.get_size()
    if orig_w <= 0 or orig_h <= 0:
        logger.error(f"show_feedback: invalid image size -> {img_path} ({orig_w}x{orig_h})")
        return None

    scale = min(max_W / orig_w, max_H / orig_h)
    new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    if new_size != (orig_w, orig_h):
        img = pygame.transform.smoothscale(img, new_size)

    # Compute center
    w, h = screen.get_size()
    new_W, new_H = new_size
    cx, cy = w / 2, h / 2
    center = (int(cx), int(cy))

    # Place image at target location
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)


def gss_practice_trial(screen: pygame.Surface, goal = str):
    """
    Run one gss practice interval
        - goal == "accuracy": accuracy block (cfg.)
        - goal == "speed": speed block
    """
    displaying_marker = True
    running = True
    responded = False
    clock = pygame.time.Clock()
    
    displayed_stimulus = random.choice(cfg.GSS_PRACTICE_STIMULI)
    displayed_stimulus_path = displayed_stimulus[0]
    logger.debug(f"displaying stimulus {displayed_stimulus_path}")

    # Overall time management
    interval_duration = random.choice(cfg.INTERVALS)
    logger.info(f"interval duration is set to {interval_duration}")
    start_at = pygame.time.get_ticks()
    end_marker_at = pygame.time.get_ticks() + cfg.MARKER_DISPLAY_DURATION
    trial_start_at = pygame.time.get_ticks() + cfg.MARKER_DISPLAY_DURATION
    end_phase_at = end_marker_at + interval_duration

    feedback_until = 0
    
    trial_count = 0

    # Helper function: randomly select a different stimulus to prevent facilitation from immediate repetition
    def _update_displayed_stimulus(displayed_stimulus):
        other_stroop_stimuli = []
        for stroop_stimulus in cfg.GSS_PRACTICE_STIMULI:
            if stroop_stimulus[1] != displayed_stimulus[1] and stroop_stimulus[2] != displayed_stimulus[2]:
                other_stroop_stimuli.append(stroop_stimulus)
        return random.choice(other_stroop_stimuli)

    # Display marker
    while displaying_marker:

        now = pygame.time.get_ticks()
        if now > end_marker_at:
            displaying_marker = False
            pygame.event.clear()
            pygame.display.flip()
            break

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                displaying_marker = False
                raise SystemExit

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    toggle_full_screen(screen)
                    pygame.event.clear()
        
        if goal == "accuracy":
            load_gss_practice_goal_marker(screen, cfg.ACCURACY_MARKER)
        
        elif goal == "speed":
            load_gss_practice_goal_marker(screen, cfg.SPEED_MARKER)
        
        else:
            logger.debug(f"Mode not supported")

        pygame.display.flip()
        clock.tick(60)

    # Begin trial
    while running:

        # Begin trial
        now = pygame.time.get_ticks()
        if now > max(end_phase_at, feedback_until):
            running = False
            pygame.display.flip()
            pygame.event.clear()
            break
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False
                raise SystemExit
            
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    toggle_full_screen(screen)
                    pygame.event.clear()
                
                elif event.key == pygame.K_d and not responded:   # blue
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus[1] == "blue")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered blue")
                    
                    trial_count += 1

                    responded_at = pygame.time.get_ticks()
                    reaction_time = responded_at - trial_start_at

                    pygame.event.clear()
                
                elif event.key == pygame.K_f and not responded:   # green
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION
                    
                    correct = (displayed_stimulus[1] == "green")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered green")

                    trial_count += 1

                    responded_at = pygame.time.get_ticks()
                    reaction_time = responded_at - trial_start_at

                    pygame.event.clear()
                
                elif event.key == pygame.K_j and not responded:   # yellow
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus[1] == "yellow")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered yellow")

                    trial_count += 1
                    
                    responded_at = pygame.time.get_ticks()
                    reaction_time = responded_at - trial_start_at
                    
                    pygame.event.clear()
                
                elif event.key == pygame.K_k and not responded:   # red
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus[1] == "red")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered red")

                    trial_count += 1

                    responded_at = pygame.time.get_ticks()
                    reaction_time = responded_at - trial_start_at

                    pygame.event.clear()

        if responded:
            if now <= feedback_until:
                now = pygame.time.get_ticks()
                show_feedback(screen, correct)
            else:
                update_save("gss practice", "gss practice", goal, correct, reaction_time, displayed_stimulus_path)    # phase, condition, difficulty, correct, reaction_time, stimulus_path
                
                displayed_stimulus = _update_displayed_stimulus(displayed_stimulus)
                displayed_stimulus_path = displayed_stimulus[0]
                trial_start_at = pygame.time.get_ticks()
                logger.debug(f"displaying stimulus {displayed_stimulus_path}")
                
                responded = False
                end_phase_at += cfg.FB_DURATION
                pygame.event.clear()
        
        else:
            load_gss_practice_stimulus(screen, displayed_stimulus_path)

        pygame.display.flip()
        clock.tick(60)


def run_gss_practice(screen: pygame.Surface):
    # Interval 1: accuracy interval
    pygame.event.clear()
    interactive_instruction_page(screen, cfg.ACCURACY_BLOCK_INS, cfg.MAX_BLOCK_INFO_DISPLAY_DURATION)

    for i in range(cfg.GSS_PRACTICE_TRIAL_COUNTS):
        logger.info(f"running gss interval 1, trial {i + 1}: accuracy interval")
        gss_practice_trial(screen, "accuracy")

    show_instruction_page(screen, cfg.PRACTICE_INTERVAL_INS)
    pygame.display.flip()
    pygame.time.wait(cfg.GSS_PRACTICE_ITI)
    pygame.event.clear()

    # Interval 2: speed interval
    pygame.event.clear()
    interactive_instruction_page(screen, cfg.SPEED_BLOCK_INS, cfg.MAX_BLOCK_INFO_DISPLAY_DURATION)

    for i in range(cfg.GSS_PRACTICE_TRIAL_COUNTS):
        logger.info(f"running gss interval 2, trial {i + 1}: speed interval")
        gss_practice_trial(screen, "speed")

    show_instruction_page(screen, cfg.PRACTICE_INTERVAL_INS)
    pygame.display.flip()
    pygame.time.wait(cfg.GSS_PRACTICE_ITI)
    pygame.event.clear()

    # Interval 3: varying interval
    pygame.event.clear()
    interactive_instruction_page(screen, cfg.VARYING_BLOCK_INS, cfg.MAX_BLOCK_INFO_DISPLAY_DURATION)

    for i in range(cfg.GSS_PRACTICE_TRIAL_COUNTS):
        logger.info(f"running gss interval 3, trial {i + 1}: varying interval")
        goal = random.choice(["accuracy", "speed"])
        gss_practice_trial(screen, goal)
    
    # Do not show practice interval page after this interval