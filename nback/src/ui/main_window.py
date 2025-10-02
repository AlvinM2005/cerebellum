# ./sr/ui/main_window.py
from __future__ import annotations
from typing import Tuple
import pygame
from pathlib import Path
import datetime

import utils.config as cfg
import utils.saves as saves
import utils.feedback as fb
from utils.logger import get_logger
from core.test_flow import show_instructions
from utils.enums import Answer

# ---------- Internal state ----------
_is_fullscreen = True                           # acticate in full-screen mode
logger = get_logger("./src/ui/main_window")     # create logger


def init_display() -> pygame.Surface:
    """Initialize display window. Start in full-screen mode."""
    flags = pygame.FULLSCREEN if _is_fullscreen else 0
    screen = pygame.display.set_mode(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), flags
    )
    pygame.display.set_caption("N-Back")
    return screen


def toggle_full_screen(screen: pygame.Surface) -> pygame.Surface:
    """Toggle between full-screen and windowed mode, and return the new screen object."""
    global _is_fullscreen
    _is_fullscreen = not _is_fullscreen
    flags = pygame.FULLSCREEN if _is_fullscreen else 0
    # Reset display mode (recommended way in Pygame to toggle fullscreen)
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), flags)
    if _is_fullscreen:
        logger.info(f"Entered fullscreen")
    else:
        logger.info(f"Quitted fullscreen: {cfg.SCREEN_WIDTH} x {cfg.SCREEN_HEIGHT}")
    return screen


def _render_centered_text(screen: pygame.Surface, font: pygame.font.Font,
                          text: str, y: int, color: Tuple[int, int, int]) -> None:
    """Render a line of text centered at the given y coordinate."""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(screen.get_rect().centerx, y))
    screen.blit(surf, rect.topleft)


def get_participant_id(screen: pygame.Surface) -> str:
    """
    Display the Participant ID input page; Enter to confirm; ESC to toggle fullscreen.
    - Background: cfg.GRAY_RGB
    - Text color: cfg.BLACK_RGB
    - Font: cfg.FONT_SIZE
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
        # Input box text
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
                    screen = toggle_full_screen(screen)
                elif event.key == pygame.K_RETURN and input_text != "":
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    # Accept printable characters
                    if event.unicode:
                        input_text += event.unicode

    return input_text


def _compute_version_from_pid(pid: str) -> int:
    """
    Determine VERSION based on the last character of Participant ID:
    - If the last character is an odd digit -> VERSION = 1
    - Otherwise (even digit / non-digit / empty) -> VERSION = 2
    """
    if not pid:
        return 2
    last = pid[-1]
    if last.isdigit():
        return 1 if (int(last) % 2 == 1) else 2
    return 2


# ---------- Runtime module ----------
def run() -> None:
    """
    Main entry point (called by main.py)
    """
    pygame.init()
    pygame.font.init()
    start_time = datetime.datetime.now().isoformat()

    screen = init_display()
    pid = get_participant_id(screen)
    saves.create_save(pid)
    logger.info(f"Saves CSV created.")

    # Compute VERSION based on the last digit of ID and write it
    cfg.VERSION = _compute_version_from_pid(pid)
    logger.info(f"Participant ID = {pid} | VERSION = {cfg.VERSION}")

    # Play instruction pages
    # 0-back
    show_instructions(screen, pid, start_time, cfg.START_PAGE_0BACK, cfg.START_PAGE_1BACK)
    # 1-back
    show_instructions(screen, pid, start_time, cfg.START_PAGE_1BACK, cfg.START_PAGE_2BACK)
    # 2-back
    show_instructions(screen, pid, start_time, cfg.START_PAGE_2BACK, cfg.START_PAGE_3BACK)
    # 3-back
    show_instructions(screen, pid, start_time, cfg.START_PAGE_3BACK, cfg.INSTRUCTION_COUNT + 1)
    pygame.quit()
