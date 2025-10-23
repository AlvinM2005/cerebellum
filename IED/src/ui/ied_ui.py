# ./src/ui/ied_ui.py
from __future__ import annotations
import pygame
from typing import Tuple
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from utils.pygame_setup import toggle_full_screen


logger = get_logger("./src/ui/ied_ui")  # create logger


def _compute_centers(size: Tuple[int, int]) -> dict[str, tuple[int, int]]:
    """
    Measure the center of screen
    Locate the center for 4 blocks
    """
    w, h = size
    cx, cy = w / 2, h / 2
    top =       (int(cx),            int(cy - h * 0.25))
    bottom =    (int(cx),            int(cy + h * 0.25))
    left =      (int(cx - w * 0.25), int(cy))
    right =     (int(cx + w * 0.25), int(cy))

    logger.debug(f"Top block centers at: {top}")
    logger.debug(f"Bottom block centers at: {bottom}")
    logger.debug(f"Left block centers at: {left}")
    logger.debug(f"Right block centers at: {right}")

    return {
        "top":      top,
        "bottom":   bottom,
        "left":     left,
        "right":    right,
    }


def _rect_from_center(center: tuple[int,int]) -> pygame.Rect:
    """Place the 4 blocks based on their located centers"""
    x, y = center
    return pygame.Rect(int(x - cfg.RECT_W/2), int(y - cfg.RECT_H/2), cfg.RECT_W, cfg.RECT_H)


def draw_blocks(screen: pygame.Surface) -> None:
    """
    Fill the background
    Draw the 4 blocks (filled)
    """
    screen.fill(cfg.GRAY_RGB)
    centers = _compute_centers(screen.get_size())
    for c in centers.values():
        pygame.draw.rect(
            screen,
            cfg.BLACK_RGB,
            _rect_from_center(c),
            border_radius=20
        )


def show_ied_ui(screen: pygame.Surface) -> None:
    """
    Display UI
    Toggle full screen when pressed ESCAPE
    """
    draw_blocks(screen)


def place_image(screen: pygame.Surface, img_path: str, ind: int) -> None:
    """
    Place stimulus image on assigned position
        - 1: top
        - 2: bottom
        - 3: left
        - 4: right
    """
    # Load image
    p = Path(img_path)
    if not p.exists():
        logger.error(f"place_image: file not found -> {img_path}")
        return None

    try:
        img = pygame.image.load(str(p)).convert_alpha()
    except Exception as e:
        logger.error(f"place_image: failed to load image -> {img_path} | {e}")
        return None

    # Resize image (max_W = RECT_W - 50 / max_H = RECT_H - 50)
    orig_w, orig_h = img.get_size()
    max_w, max_h = cfg.RECT_W - 50, cfg.RECT_H - 50
    if orig_w <= 0 or orig_h <= 0:
        logger.error(f"place_image: invalid image size -> {img_path} ({orig_w}x{orig_h})")
        return None

    scale = min(max_w / orig_w, max_h / orig_h)
    new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    if new_size != (orig_w, orig_h):
        img = pygame.transform.smoothscale(img, new_size)

    # Calculate centers
    centers = _compute_centers(screen.get_size())
    key_map = {1: "top", 2: "bottom", 3: "left", 4: "right"}
    key = key_map.get(ind)
    if key is None:
        logger.error(f"place_image: invalid position code ind={ind} (expect 1 / 2 / 3 / 4)")
        return None

    center = centers[key]

    # Place image to target location
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)

    logger.debug(
        f"place_image: {img_path} -> pos={key} center={center} size={img_rect.size}"
    )
    return img_rect