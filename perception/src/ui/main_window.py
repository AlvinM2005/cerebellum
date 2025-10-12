# ./src/ui/main_window.py
from __future__ import annotations
from typing import Tuple
import pygame
from pathlib import Path
import datetime

import utils.config as cfg
import utils.saves as saves
import utils.feedback as fb
from utils.logger import get_logger
from core.stimuli import stimuli
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
    pygame.display.set_caption("Time Perception")
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


def _scale_and_center(surface: pygame.Surface, screen: pygame.Surface) -> pygame.Surface:
    """Scale the surface proportionally to fit the screen and return the scaled surface."""
    sw, sh = screen.get_size()
    iw, ih = surface.get_size()
    scale = min(sw / iw, sh / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    return pygame.transform.smoothscale(surface, new_size)


def _blit_centered(screen: pygame.Surface, surf: pygame.Surface) -> None:
    """Blit the given surface centered on the screen."""
    rect = surf.get_rect(center=screen.get_rect().center)
    screen.blit(surf, rect.topleft)


def _instructions_dir() -> Path:
    """Select the instruction resource directory according to VERSION."""
    sub = "instructions" if (cfg.VERSION == 1) else "instructions_reversed"
    return cfg.RESOURCES_DIR / sub

def show_instructions(screen: pygame.Surface, pid: str, start_time: str) -> None:
    """
    Play instructions sequentially:
    - VERSION=1 read ./resources/instructions
      VERSION=2 read ./resources/instructions_reversed
    - Minimum reading time per page: cfg.MIN_READING_TIME_MS
    - After time has passed, check SPACE to turn page; clear event queue after turning
    - ESC can toggle fullscreen anytime
    - After the last page, pressing SPACE again exits the function
    """
    dir_path = _instructions_dir()
    logger.info(f"Instruction directory =  {dir_path}")
    if not dir_path.exists():
        logger.error(f"Instructions folder not found: {dir_path}")
        raise FileNotFoundError(f"Instructions folder not found: {dir_path}")

    clock = pygame.time.Clock()

    for idx in range(1, cfg.INSTRUCTION_COUNT + 1):
        img_path = dir_path / f"{idx}.png"
        if not img_path.exists():
            # If image is missing, show placeholder text (prevent crash)
            screen.fill(cfg.GRAY_RGB)
            font = pygame.font.SysFont(None, cfg.FONT_SIZE)
            msg = font.render(f"Missing: {img_path.name}", True, cfg.YELLOW_RGB)
            _blit_centered(screen, msg)
            pygame.display.flip()
            logger.warning(f"Missing image {img_path.name}")
            # Allow immediate skip to next page
            wait_ms = 0
        else:
            # Load and scale image
            image = pygame.image.load(str(img_path)).convert()
            image = _scale_and_center(image, screen)
            screen.fill(cfg.GRAY_RGB)
            _blit_centered(screen, image)
            pygame.display.flip()
            wait_ms = cfg.MIN_READING_TIME
            logger.info(f"Instruction page {idx} displayed")

        # Timing and wait for SPACE
        start = pygame.time.get_ticks()
        while True:
            elapsed = pygame.time.get_ticks() - start
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Allow toggling fullscreen anytime before turning page
                        screen = toggle_full_screen(screen)

                        # Clear screen to gray
                        screen.fill(cfg.GRAY_RGB)
                        _blit_centered(screen, image)
                        pygame.display.flip()

                    elif event.key == pygame.K_SPACE and elapsed >= wait_ms:
                        logger.info(f"Advance to instruction page {idx}")
                        pygame.event.clear()

                        # After this page, check if we should start a practice/block.

                        # Duration Subtask
                        page_to_count_duration = {}
                        for nm in ("PRACTICE1", "BLOCK1", "BLOCK2"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_duration[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_duration:
                            block_name, trials = page_to_count_duration[idx]
                            logger.info(f"[Duration Subtask] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time, task_type=0)

                        # Loudness Subtask
                        page_to_count_loudness = {}
                        for nm in ("PRACTICE2", "BLOCK3", "BLOCK4"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_loudness[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_loudness:
                            block_name, trials = page_to_count_loudness[idx]
                            logger.info(f"[Loudness Subtask] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time, task_type=1)

                        break
            else:
                # If break not triggered: continue loop
                clock.tick(60)
                continue
            # If break triggered: exit waiting loop for this page
            break

def play_stimuli(trial_num: int, screen: pygame.Surface, block: str, pid: str, start_time: str, task_type: bool) -> None:
    """
    Play `trial_num` stimuli.
    - QUIT closes the program
    - ESC toggles full screen
    - Q / X aborts playback (return from this function)
    - During stimulus ON, D/K are recorded as participant answers (mapping depends on VERSION)
    """

    logger.info(f"Play stimuli: trial_num = {trial_num}, block = {block}")

    stimuli(
        trial_count=trial_num,
        screen=screen,
        task_type=task_type,
        block_name=block,
        pid=pid,
        start_time=start_time
    )

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
    show_instructions(screen, pid, start_time)

    pygame.quit()


if __name__ == "__main__":
    run()
