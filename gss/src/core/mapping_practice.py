# ./src/core/mapping_practice.py

from typing import Tuple
import pygame
import random
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import toggle_full_screen, show_instruction_page
from core.show_feedback import show_feedback
from core.saves import update_save

logger = get_logger("./src/core/mapping_practice") # create logger

def load_mapping_stimulus(screen: pygame.Surface, img_path: Path):
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


def mapping_interval(screen: pygame.Surface):
    """
    Run one mapping practice interval
    """
    running = True
    responded = False
    clock = pygame.time.Clock()
    
    displayed_stimulus = random.choice(cfg.MAPPING_STIMULI)
    logger.debug(f"displaying stimulus {displayed_stimulus}")

    interval_duration = random.choice(cfg.INTERVALS)
    logger.info(f"interval duration is set to {interval_duration}")
    start_time = pygame.time.get_ticks()
    phase_end = start_time + interval_duration

    feedback_until = 0

    # Helper function: randomly select a different stimulus to prevent facilitation from immediate repetition
    def _update_displayed_stimulus(displayed_stimulus):
        other_mp_stimuli = []
        for mp_stimulus in cfg.MAPPING_STIMULI:
            if mp_stimulus != displayed_stimulus:
                other_mp_stimuli.append(mp_stimulus)
        return random.choice(other_mp_stimuli)

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

                    correct = (displayed_stimulus == cfg.CIRCLE_BLUE)
                    logger.debug(f"{correct} | displayed {displayed_stimulus} | answered blue")

                    pygame.event.clear()
                
                elif event.key == pygame.K_f and not responded:   # green
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION
                    
                    correct = (displayed_stimulus == cfg.CIRCLE_GREEN)
                    logger.debug(f"{correct} | displayed {displayed_stimulus} | answered green")

                    pygame.event.clear()
                
                elif event.key == pygame.K_j and not responded:   # yellow
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus == cfg.CIRCLE_YELLOW)
                    logger.debug(f"{correct} | displayed {displayed_stimulus} | answered yellow")

                    pygame.event.clear()
                
                elif event.key == pygame.K_k and not responded:   # red
                    responded = True
                    respond_time = pygame.time.get_ticks()
                    feedback_until = respond_time + cfg.FB_DURATION

                    correct = (displayed_stimulus == cfg.CIRCLE_RED)
                    logger.debug(f"{correct} | displayed {displayed_stimulus} | answered red")

                    pygame.event.clear()

        if responded:
            if now <= feedback_until:
                now = pygame.time.get_ticks()
                show_feedback(screen, correct)
            else:
                update_save("mapping practice", "mapping practice", "practice", correct, displayed_stimulus)    # phase, condition, difficulty, correct, stimulus_path

                displayed_stimulus = _update_displayed_stimulus(displayed_stimulus)
                logger.debug(f"displaying stimulus {displayed_stimulus}")

                responded = False
                phase_end += cfg.FB_DURATION
                pygame.event.clear()
        
        else:
            load_mapping_stimulus(screen, displayed_stimulus)

        pygame.display.flip()
        clock.tick(60)


def run_mapping(screen: pygame.Surface):
    for i in range(cfg.MAPPING_INTERVAL_COUNTS):
        logger.info(f"running mp_interval {i + 1}")
        mapping_interval(screen)

        # Show practice interval page if not at the last interval
        if i != cfg.MAPPING_INTERVAL_COUNTS - 1:
            show_instruction_page(screen, cfg.PRACTICE_INTERVAL_INS)
            pygame.display.flip()
            pygame.time.wait(cfg.MAPPING_III)
