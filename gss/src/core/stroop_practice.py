# ./src/core/stroop_practice.py

from typing import Tuple
import pygame
import random
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import toggle_full_screen, show_instruction_page
from core.show_feedback import show_feedback
from core.saves import update_save

logger = get_logger("./src/core/stroop_practice") # create logger

def load_stroop_stimulus(screen: pygame.Surface, img_path: Path):
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


def stroop_interval(screen: pygame.Surface):
    """
    Run one stroop practice interval
    """
    running = True
    responded = False
    clock = pygame.time.Clock()
    
    displayed_stimulus = random.choice(cfg.STROOP_STIMULI)
    displayed_stimulus_path = displayed_stimulus[0]
    logger.debug(f"displaying stimulus {displayed_stimulus_path}")

    interval_duration = random.choice(cfg.INTERVALS)
    logger.info(f"interval duration is set to {interval_duration}")
    start_time = pygame.time.get_ticks()
    phase_end = start_time + interval_duration

    feedback_until = 0

    # Helper function: randomly select a different stimulus to prevent facilitation from immediate repetition
    def _update_displayed_stimulus(displayed_stimulus):
        other_stroop_stimuli = []
        for stroop_stimulus in cfg.STROOP_STIMULI:
            if stroop_stimulus[1] != displayed_stimulus[1] and stroop_stimulus[2] != displayed_stimulus[2]:
                other_stroop_stimuli.append(stroop_stimulus)
        return random.choice(other_stroop_stimuli)

    while running:

        now = pygame.time.get_ticks()
        if now > max(phase_end, feedback_until):
            running = False
            pygame.event.clear()
            pygame.display.flip()
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

                    pygame.event.clear()
                
                elif event.key == pygame.K_f and not responded:   # green
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION
                    
                    correct = (displayed_stimulus[1] == "green")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered green")

                    pygame.event.clear()
                
                elif event.key == pygame.K_j and not responded:   # yellow
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus[1] == "yellow")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered yellow")

                    pygame.event.clear()
                
                elif event.key == pygame.K_k and not responded:   # red
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus[1] == "red")
                    logger.debug(f"{correct} | displayed {displayed_stimulus_path} | answered red")

                    pygame.event.clear()

        if responded:
            if now <= feedback_until:
                now = pygame.time.get_ticks()
                show_feedback(screen, correct)
            else:
                update_save("stroop practice", "stroop practice", "practice", correct, displayed_stimulus_path)    # phase, condition, difficulty, correct, stimulus_path
                
                displayed_stimulus = _update_displayed_stimulus(displayed_stimulus)
                displayed_stimulus_path = displayed_stimulus[0]
                logger.debug(f"displaying stimulus {displayed_stimulus_path}")

                responded = False
                phase_end += cfg.FB_DURATION
                pygame.event.clear()
        
        else:
            load_stroop_stimulus(screen, displayed_stimulus_path)

        pygame.display.flip()
        clock.tick(60)


def run_stroop(screen: pygame.Surface):
    for i in range(cfg.STROOP_INTERVAL_COUNTS):
        logger.info(f"running stroop_interval {i + 1}")
        stroop_interval(screen)

        # Show practice interval page if not at the last round
        if i != cfg.STROOP_INTERVAL_COUNTS - 1:
            show_instruction_page(screen, cfg.PRACTICE_INTERVAL_INS)
            pygame.display.flip()
            pygame.time.wait(cfg.STROOP_III)
