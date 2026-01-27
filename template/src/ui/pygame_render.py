# ./src/core/pygame_render.py
"""
Pygame setup utilities.

This module initializes the Pygame display, manages fullscreen toggling, renders basic text elements, and collects PID and VERSION.
"""


from __future__ import annotations
from typing import Tuple, Optional
import pygame
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from utils.paths import FB_CORRECT, FB_INCORRECT


logger = get_logger("./src/ui/pygame_render")


def init_display() -> pygame.Surface:
    """
    Initialize the pygame display window.

    :return: Initialized pygame display surface
    :rtype: pygame.Surface
    """

    flags = pygame.FULLSCREEN if cfg._is_fullscreen else 0
    screen = pygame.display.set_mode(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), flags
    )
    pygame.display.set_caption("IED")
    return screen


def toggle_full_screen(screen: pygame.Surface) -> pygame.Surface:
    """
    Toggle between full-screen and windowed display modes.
    
    :param screen: Current pygame display surface
    :type screen: pygame.Surface

    :return: New pygame display surface after toggling fullscreen state (window -> fullscreen; fullscreen -> window)
    :rtype: pygame.Surface
    """

    cfg._is_fullscreen = not cfg._is_fullscreen
    flags = pygame.FULLSCREEN if cfg._is_fullscreen else 0

    # Reset display mode (recommended way in Pygame to toggle fullscreen)
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), flags)

    if cfg._is_fullscreen:
        logger.info(f"[toggle_full_screen] Entered fullscreen")
    else:
        logger.info(f"[toggle_full_screen] Quitted fullscreen: {cfg.SCREEN_WIDTH} x {cfg.SCREEN_HEIGHT}")
        
    return screen


def _render_centered_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str, y: int,
    color: Tuple[int, int, int]
) -> None:
    """
    Render a single line of text horizontally centered on the screen.
    
    :param screen: Target pygame display surface
    :type screen: pygame.Surface

    :param font: Font used to render the text
    :type font: pygame.font.Font

    :param text: Text string to be rendered
    :type text: str

    :param y: Vertical pixel coordinate for the text center
    :type y: int

    :param color: RGB color tuple used to render the text
    :type color: Tuple[int, int, int]
    """

    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(screen.get_rect().centerx, y))
    screen.blit(surf, rect.topleft)


def get_participant_id(screen: pygame.Surface) -> pygame.Surface:
    """
    Display the Participant ID input page; Enter to confirm; ESC to toggle fullscreen.

    The screen prompts the user to enter a participant ID.
    - Press Enter to confirm and return the input.
    - Press ESC to toggle full-screen mode.
    - Close window to terminate the program.
    
    Visual settings:
    - Background: cfg.GRAY_RGB
    - Text color: cfg.BLACK_RGB
    - Font: cfg.FONT_SIZE
    
    :param screen: Active pygame display surface
    :type screen: pygame.Surface

    :return: pygame.Surface
    """

    font = pygame.font.SysFont(None, cfg.FONT_SIZE)
    input_text = ""
    active = True

    while active:
        screen.fill(cfg.GRAY_RGB)
        screen_rect = screen.get_rect()

        _render_centered_text(
            screen, font,
            "Enter Participant ID (press Enter when completed):",
            screen_rect.centery - 80,
            cfg.BLACK_RGB,
        )

        _render_centered_text(
            screen, font, input_text, screen_rect.centery, cfg.BLACK_RGB
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    screen = toggle_full_screen(screen)
                    pygame.event.clear()

                elif event.key == pygame.K_RETURN and input_text != "":
                    active = False
                    pygame.display.flip()

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                else:
                    # Accept printable characters
                    if event.unicode:
                        input_text += event.unicode

    cfg.PID = input_text

    return screen


def record_hands(screen: pygame.Surface) -> pygame.Surface:
    """
    Record participant hand information.

    This function sequentially asks:
    1) Dominant hand
    2) Less affected hand

    Input rules:
    - Press '1' for left hand
    - Press '2' for right hand
    - Press ESC to toggle full-screen mode
    - Close window to terminate the program

    :param screen: Active pygame display surface
    :type screen: pygame.Surface

    :return: Updated pygame display surface
    :rtype: pygame.Surface
    """
    from utils.event_handler import EventHandler

    font = pygame.font.SysFont(None, cfg.FONT_SIZE)
    event_handler = EventHandler()

    questions = [
        ("What is the participant's dominant hand?", "dominant_hand"),
        ("What is the participant's less affected hand?", "less_affected_hand"),
    ]

    for question_text, attr_name in questions:
        active = True

        while active:
            screen.fill(cfg.GRAY_RGB)
            screen_rect = screen.get_rect()

            _render_centered_text(
                screen,
                font,
                question_text,
                screen_rect.centery - 120,
                cfg.BLACK_RGB,
            )

            _render_centered_text(
                screen,
                font,
                "1 = Left hand        2 = Right hand",
                screen_rect.centery - 40,
                cfg.BLACK_RGB,
            )

            pygame.display.flip()

            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()

            if state.version_1:
                setattr(cfg, attr_name, "left")
                active = False

            elif state.version_2:
                setattr(cfg, attr_name, "right")
                active = False

    return screen


def place_image(
    screen: pygame.Surface,
    img_path: Path,
    center: Optional[Tuple[float, float]] = None,
    resize: Optional[Tuple[int, int]] = None,
    overlay: bool = False,
) -> None:
    """
    Load an image from disk, resize it, and blit it onto the screen at a given center position.

    The function:
    - Loads an image with alpha channel support.
    - Resizes the image to the target size.
    - Clears the screen with cfg.GRAY_RGB to avoid black borders.
    - Places the image centered at the target location.

    Parameter rules:
    - center:
        - If None, defaults to the screen center.
        - Must be a 2-tuple (x, y) within screen bounds.
    - resize:
        - If None, defaults to the screen size.
        - Must be a 2-tuple (width, height) with positive values.

    Visual settings (overlay:
    - If True, blits onto the existing screen content (overlay mode).
    - If False, fills the screen with cfg.GRAY_RGB before blitting (default behavior).

    :param screen: Active pygame display surface
    :type screen: pygame.Surface

    :param img_path: Path to the image file
    :type img_path: Path

    :param center: Center position (x, y) for placing the image
    :type center: Optional[Tuple[float, float]]

    :param resize: Target resize size (width, height)
    :type resize: Optional[Tuple[int, int]]

    :param overlay: Activate overlay mode (default = False)
    :type overlay: bool

    :return: None
    """

    # Get screen geometry
    screen_w, screen_h = screen.get_size()

    # Default parameters
    if center is None:
        center = (screen_w / 2, screen_h / 2)
    if resize is None:
        resize = (screen_w, screen_h)

    # Validate parameter shape
    if len(center) != 2 or len(resize) != 2:
        logger.error("[place_image] Invalid input: 'center' and 'resize' must be 2-element tuples.")
        return

    target_cx, target_cy = center
    target_w, target_h = resize

    # Validate center range
    if not (0 <= target_cx <= screen_w and 0 <= target_cy <= screen_h):
        logger.error(
            f"[place_image] Invalid input: 'center' out of bounds: center={center}, screen=({screen_w}, {screen_h})"
        )
        return

    # Validate resize values
    try:
        target_w = int(target_w)
        target_h = int(target_h)
    except (TypeError, ValueError):
        logger.error(f"[place_image] Invalid input: 'resize' must be numeric: resize={resize}")
        return

    if target_w <= 0 or target_h <= 0:
        logger.error(f"[place_image] Invalid input: 'resize' must be positive: resize=({target_w}, {target_h})")
        return

    # Check image file existence
    if not img_path.exists():
        logger.error(f"[place_image] Image file not found -> {img_path}")
        return

    # Load image with alpha support
    try:
        img = pygame.image.load(str(img_path)).convert_alpha()
    except Exception as e:
        logger.error(f"[place_image] Failed to load image -> {img_path} | {e}")
        return

    # Resize image
    img = pygame.transform.smoothscale(img, (target_w, target_h))

    # Activate overlay mode
    if not overlay:
        screen.fill(cfg.GRAY_RGB)

    # Blit image at target center
    img_rect = img.get_rect(center=(target_cx, target_cy))
    screen.blit(img, img_rect)


def show_feedback(screen: pygame.Surface, status: str) -> None:
    """
    Show feedback based on response status.

    Feedback is rendered as an overlay on the current stimulus screen

    Parameter rules:
    - status:
        - "correct": show cfg.FB_CORRECT image centered in the lower-middle area
        - "incorrect": show cfg.FB_INCORRECT image centered in the lower-middle area
        - "timeout": show yellow "Timeout!" text centered in the lower-middle area

    Visual settings:
    - Image resize: cfg.FB_W x cfg.FB_H
    - Timeout text color: cfg.YELLOW_RGB

    :param screen: Active pygame display surface
    :type screen: pygame.Surface

    :param status: Feedback status string ("correct", "incorrect", "timeout")
    :type status: str

    :return: None
    """
    screen_w, screen_h = screen.get_size()
    # Lower-middle placement (centered, slightly below midline)
    center = (screen_w / 2, screen_h * 0.68)

    if status == "correct":
        place_image(
            screen=screen,
            img_path=Path(FB_CORRECT),
            center=center,
            resize=(cfg.FB_W, cfg.FB_H),
            overlay=True,
        )
        return

    if status == "incorrect":
        place_image(
            screen=screen,
            img_path=Path(FB_INCORRECT),
            center=center,
            resize=(cfg.FB_W, cfg.FB_H),
            overlay=True,
        )
        return

    if status == "timeout":
        font = pygame.font.SysFont(None, cfg.FONT_SIZE)
        text_surf = font.render("Timeout!", True, cfg.YELLOW_RGB)
        text_rect = text_surf.get_rect(center=center)
        screen.blit(text_surf, text_rect)
        return

    logger.error(f"[show_feedback] Invalid status: {status}")
