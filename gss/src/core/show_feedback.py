# ./src/core/show_feedback.py
import pygame
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger

logger = get_logger("./src/core/show_feedback")    # create logger

def show_feedback(screen: pygame.Surface, correct: bool) -> None:
    """
    Show feedback at the center of the screen
    - correct == True: show correct feedback image
    - correct == False: show incorrect feedback image
    """
    # Load image
    if correct:
        img_path = cfg.FB_CORRECT
    else:
        img_path = cfg.FB_INCORRECT
    p = Path(img_path)
    if not p.exists():
        logger.error(f"show_feedback: file not found -> {img_path}")
        return None

    try:
        img = pygame.image.load(str(p)).convert_alpha()
    except Exception as e:
        logger.error(f"show_feedback: failed to load image -> {img_path} | {e}")
        return None

    # Resize image
    orig_w, orig_h = img.get_size()
    max_w, max_h = cfg.FB_W, cfg.FB_H
    if orig_w <= 0 or orig_h <= 0:
        logger.error(f"show_feedback: invalid image size -> {img_path} ({orig_w}x{orig_h})")
        return None

    scale = min(max_w / orig_w, max_h / orig_h)
    new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    if new_size != (orig_w, orig_h):
        img = pygame.transform.smoothscale(img, new_size)

    # Compute center
    w, h = screen.get_size()
    cx, cy = w / 2, h / 6
    center = (int(cx), int(cy))

    # Place feedback image at target location
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)