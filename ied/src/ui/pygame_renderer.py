# ./src/ui/pygame_renderer.py
"""
Pygame rendering utilities.

This module centralizes all pygame display-related functionality.
"""

from __future__ import annotations

from typing import Tuple, Optional
from pathlib import Path
import pygame

import utils.config as cfg
import utils.paths as paths
from utils.logger import get_logger
from utils.event_handler import EventHandler


logger = get_logger("./src/ui/pygame_renderer")


def init_display() -> pygame.Surface:
    """Initialize display window. Start in full-screen mode."""
    flags = pygame.FULLSCREEN if cfg._is_fullscreen else 0
    screen = pygame.display.set_mode(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), flags, vsync=1
    )
    pygame.display.set_caption("IED")
    return screen


def toggle_full_screen(screen: pygame.Surface) -> pygame.Surface:
    """Toggle between full-screen and windowed mode, and return the new screen object."""
    cfg._is_fullscreen = not cfg._is_fullscreen
    flags = pygame.FULLSCREEN if cfg._is_fullscreen else 0
    screen = pygame.display.set_mode(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), flags, vsync=1
    )
    if cfg._is_fullscreen:
        logger.info("Entered fullscreen")
    else:
        logger.info(f"Quitted fullscreen: {cfg.SCREEN_WIDTH} x {cfg.SCREEN_HEIGHT}")
    return screen


def _render_centered_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    color: Tuple[int, int, int],
) -> None:
    """Render a line of text centered at the given y coordinate."""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(screen.get_rect().centerx, y))
    screen.blit(surf, rect.topleft)


def _play_admin_image(screen: pygame.Surface, img_path: Path) -> pygame.Surface:
    """
    Show one admin page directly.

    Returns a screen snapshot used as static background for overlay rendering.
    """
    place_image(screen, img_path)
    pygame.display.flip()
    pygame.event.clear()
    return screen.copy()


def _wait_for_left_or_right(
    screen: pygame.Surface,
    event_handler: EventHandler,
    img_path: Path,
) -> tuple[pygame.Surface, str]:
    """
    Show admin image and wait until L or R is pressed.
    """
    admin_bg = _play_admin_image(screen, img_path)

    while True:
        screen.blit(admin_bg, (0, 0))
        pygame.display.flip()

        state = event_handler.poll()

        if state.quit:
            pygame.quit()
            raise SystemExit

        if state.toggle_full_screen:
            pygame.event.clear()
            screen = toggle_full_screen(screen)
            pygame.event.clear()
            admin_bg = _play_admin_image(screen, img_path)
            continue

        if state.left_hand:
            return screen, "left"

        if state.right_hand:
            return screen, "right"

        pygame.time.delay(10)


def _wait_for_key_raw_pygame(
    screen: pygame.Surface,
    img_path: Path,
    target_key: int,
) -> pygame.Surface:
    """
    Wait until target key is pressed using raw pygame events (no EventHandler).
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _play_admin_image(screen, img_path)
                continue

            if event.key == target_key:
                return screen

        pygame.time.delay(10)


def _compute_mapping_from_pid(pid: str) -> int:
    """
    Compute mapping from PID suffix.

    Rule:
    - Last char is an even digit -> mapping 2
    - Last char is an odd digit OR not a digit -> mapping 1
    """
    if not pid:
        return 1
    last_char = pid[-1]
    if not last_char.isdigit():
        return 1
    return 2 if int(last_char) % 2 == 0 else 1


def get_participant_id(screen: pygame.Surface) -> pygame.Surface:
    """
    Show ADMIN_1 and collect participant ID via keyboard input.
    """
    font = pygame.font.SysFont(None, cfg.FONT_SIZE)
    input_text = ""
    admin_bg = _play_admin_image(screen, paths.ADMIN_1)

    while True:
        screen.blit(admin_bg, (0, 0))
        _render_centered_text(screen, font, input_text, screen.get_rect().centery + 20, cfg.COCO_RGB)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                admin_bg = _play_admin_image(screen, paths.ADMIN_1)
                continue

            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
                continue

            if event.key == pygame.K_RETURN:
                if input_text.strip():
                    cfg.PID = input_text.strip()
                    cfg.MAPPING = _compute_mapping_from_pid(cfg.PID)
                    return screen
                continue

            if event.unicode:
                input_text += "".join(ch for ch in event.unicode if ch.isprintable())

        pygame.time.delay(10)


def record_hands(screen: pygame.Surface) -> pygame.Surface:
    """
    Play admin pages and record dominant hand + hand used.
    """
    event_handler = EventHandler()

    # 1) Show ADMIN_2 and collect dominant hand.
    screen, dominant_hand = _wait_for_left_or_right(screen, event_handler, paths.ADMIN_2)
    cfg.dominant_hand = dominant_hand

    # 2) Branch by dominant hand, then collect hand_used.
    if dominant_hand == "left":
        screen, hand_used = _wait_for_left_or_right(screen, event_handler, paths.ADMIN_L)
        cfg.hand_used = hand_used

        if hand_used == "left":
            confirm_img = paths.ADMIN_LL
            please_img = paths.ADMIN_PLEASE_L
        else:
            confirm_img = paths.ADMIN_LR
            please_img = paths.ADMIN_PLEASE_R
    else:
        screen, hand_used = _wait_for_left_or_right(screen, event_handler, paths.ADMIN_R)
        cfg.hand_used = hand_used

        if hand_used == "left":
            confirm_img = paths.ADMIN_RL
            please_img = paths.ADMIN_PLEASE_L
        else:
            confirm_img = paths.ADMIN_RR
            please_img = paths.ADMIN_PLEASE_R

    _play_admin_image(screen, confirm_img)
    screen = _wait_for_key_raw_pygame(screen, confirm_img, pygame.K_RETURN)

    _play_admin_image(screen, please_img)
    screen = _wait_for_key_raw_pygame(screen, please_img, pygame.K_SPACE)

    return screen


def _compute_centers(size: Tuple[int, int]) -> dict[str, tuple[int, int]]:
    """
    Measure the center of screen
    Locate the center for 4 blocks
    """
    w, h = size
    cx, cy = w / 2, h / 2
    top = (int(cx), int(cy - h * 0.25))
    bottom = (int(cx), int(cy + h * 0.25))
    left = (int(cx - w * 0.25), int(cy))
    right = (int(cx + w * 0.25), int(cy))

    return {
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right,
    }


def _rect_from_center(center: tuple[int, int]) -> pygame.Rect:
    """Place the 4 blocks based on their located centers."""
    x, y = center
    return pygame.Rect(int(x - cfg.RECT_W / 2), int(y - cfg.RECT_H / 2), cfg.RECT_W, cfg.RECT_H)


def draw_blocks(screen: pygame.Surface) -> None:
    """
    Fill the background
    Draw the 4 blocks (filled)
    """
    screen.fill(cfg.BLACK_RGB)
    centers = _compute_centers(screen.get_size())
    for c in centers.values():
        pygame.draw.rect(
            screen,
            cfg.COCO_RGB,
            _rect_from_center(c),
            width=cfg.BORDER_PX,
            border_radius=20,
        )


def show_ied_ui(screen: pygame.Surface) -> None:
    """Display UI."""
    draw_blocks(screen)


def _load_image(path: Path) -> pygame.Surface | None:
    if not path.exists():
        logger.error(f"place_image: file not found -> {path}")
        return None
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except Exception as e:
        logger.error(f"place_image: failed to load image -> {path} | {e}")
        return None


def place_image(
    screen: pygame.Surface,
    img_path: Path,
    center: Optional[Tuple[float, float]] = None,
    resize: Optional[Tuple[int, int]] = None,
) -> None:
    """
    Load an image from disk, resize it, and blit it onto the screen at a given center position.
    """
    img = _load_image(Path(img_path))
    if img is None:
        return None

    w, h = screen.get_size()

    if resize is not None:
        img = pygame.transform.smoothscale(img, resize)
    else:
        orig_w, orig_h = img.get_size()
        if orig_w > 0 and orig_h > 0:
            scale = min(w / orig_w, h / orig_h)
            new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
            if new_size != (orig_w, orig_h):
                img = pygame.transform.smoothscale(img, new_size)

    if center is None:
        center = (int(w / 2), int(h / 2))

    screen.fill(cfg.BLACK_RGB)
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)


def place_single_image(screen: pygame.Surface, img_path: Path, ind: int) -> None:
    """
    Place stimulus image on assigned position
        - 1: top
        - 2: bottom
        - 3: left
        - 4: right
    """
    img = _load_image(Path(img_path))
    if img is None:
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

    centers = _compute_centers(screen.get_size())
    key_map = {1: "top", 2: "bottom", 3: "left", 4: "right"}
    key = key_map.get(ind)
    if key is None:
        logger.error(f"place_image: invalid position code ind={ind} (expect 1 / 2 / 3 / 4)")
        return None

    center = centers[key]
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)


def place_side_by_side_images(screen: pygame.Surface, shape_img_path: Path, line_img_path: Path, ind: int) -> None:
    """
    Place two stimulus images (shape + line) on the assigned position.
    Place shape on the left, line on the right.
    """
    paths = {"shape": shape_img_path, "line": line_img_path}
    images = {}

    for key, path in paths.items():
        img = _load_image(Path(path))
        if img is None:
            return None

        orig_w, orig_h = img.get_size()
        max_w, max_h = cfg.RECT_W - 50, cfg.RECT_H - 50
        if orig_w <= 0 or orig_h <= 0:
            logger.error(f"place_image: invalid image size -> {path} ({orig_w}x{orig_h})")
            return None

        scale = min(max_w / orig_w, max_h / orig_h)
        new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
        if new_size != (orig_w, orig_h):
            img = pygame.transform.smoothscale(img, new_size)

        images[key] = img

    centers = _compute_centers(screen.get_size())
    key_map = {1: "top", 2: "bottom", 3: "left", 4: "right"}
    key = key_map.get(ind)
    if key is None:
        logger.error(f"place_image: invalid position code ind={ind} (expect 1 / 2 / 3 / 4)")
        return None

    center = centers[key]
    offset_x = cfg.RECT_W * 0.25
    cx, cy = center

    shape_center = (int(cx - offset_x), int(cy))
    line_center = (int(cx + offset_x), int(cy))

    screen.blit(images["shape"], images["shape"].get_rect(center=shape_center))
    screen.blit(images["line"], images["line"].get_rect(center=line_center))


def place_overlapped_images(screen: pygame.Surface, shape_img_path: Path, line_img_path: Path, ind: int) -> None:
    """
    Place two stimulus images (shape + line) on the assigned position.
    Place shape behind line.
    """
    paths = {"shape": shape_img_path, "line": line_img_path}
    images = {}

    for key, path in paths.items():
        img = _load_image(Path(path))
        if img is None:
            return None

        orig_w, orig_h = img.get_size()
        max_w, max_h = cfg.RECT_W - 50, cfg.RECT_H - 50
        if orig_w <= 0 or orig_h <= 0:
            logger.error(f"place_image: invalid image size -> {path} ({orig_w}x{orig_h})")
            return None

        scale = min(max_w / orig_w, max_h / orig_h)
        new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
        if new_size != (orig_w, orig_h):
            img = pygame.transform.smoothscale(img, new_size)

        images[key] = img

    centers = _compute_centers(screen.get_size())
    key_map = {1: "top", 2: "bottom", 3: "left", 4: "right"}
    key = key_map.get(ind)
    if key is None:
        logger.error(f"place_image: invalid position code ind={ind} (expect 1 / 2 / 3 / 4)")
        return None

    center = centers[key]
    screen.blit(images["shape"], images["shape"].get_rect(center=center))
    screen.blit(images["line"], images["line"].get_rect(center=center))


def show_feedback(screen: pygame.Surface, correct: bool) -> None:
    """
    Show feedback at the center of the screen.
    """
    img_path = paths.FB_CORRECT if correct else paths.FB_INCORRECT
    img = _load_image(Path(img_path))
    if img is None:
        return None

    orig_w, orig_h = img.get_size()
    max_w, max_h = cfg.RECT_W - 50, cfg.RECT_H - 50
    if orig_w <= 0 or orig_h <= 0:
        logger.error(f"show_feedback: invalid image size -> {img_path} ({orig_w}x{orig_h})")
        return None

    scale = min(max_w / orig_w, max_h / orig_h)
    new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    if new_size != (orig_w, orig_h):
        img = pygame.transform.smoothscale(img, new_size)

    w, h = screen.get_size()
    center = (int(w / 2), int(h / 2))
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)
