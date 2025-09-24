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
from core.pull_stimuli import pull_stimuli, _pick_0back_target_path
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


def _load_mapping_surface(screen: pygame.Surface) -> pygame.Surface:
    """Load ./resources/mapping/{1|2}.png by VERSION and scale to full screen as background."""
    version_png = "1.png" if cfg.VERSION == 1 else "2.png"
    path = cfg.RESOURCES_DIR / "mapping" / version_png
    if not path.exists():
        raise FileNotFoundError(f"Mapping image not found: {path}")
    img = pygame.image.load(str(path)).convert()
    return pygame.transform.smoothscale(img, screen.get_size())


def _stim_region_rect(screen: pygame.Surface) -> pygame.Rect:
    """
    Compute the target rectangle (in pixels) for placing the stimulus image.
    The region is defined in config as normalized coordinates (left, top, width, height).
    """
    sw, sh = screen.get_size()
    l, t, w, h = cfg.STIM_REGION
    return pygame.Rect(int(l * sw), int(t * sh), int(w * sw), int(h * sh))


def _blit_into_region(screen: pygame.Surface, img: pygame.Surface, region: pygame.Rect) -> None:
    """Scale the stimulus to fit the region (keep aspect ratio), then center-blit inside the region."""
    iw, ih = img.get_size()
    scale = min(region.width / iw, region.height / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    scaled = pygame.transform.smoothscale(img, new_size)
    dst = scaled.get_rect(center=region.center)
    screen.blit(scaled, dst.topleft)


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
        img_path = dir_path / f"{idx}.jpg"
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
                        # Redraw current page (toggling fullscreen clears the screen)
                        if img_path.exists():
                            screen.fill(cfg.GRAY_RGB)
                            _blit_centered(screen, image)
                        else:
                            screen.fill(cfg.GRAY_RGB)
                            font = pygame.font.SysFont(None, cfg.FONT_SIZE)
                            msg = font.render(f"Missing: {img_path.name}", True, cfg.YELLOW_RGB)
                            _blit_centered(screen, msg)
                        pygame.display.flip()
                    elif event.key == pygame.K_SPACE and elapsed >= wait_ms:
                        logger.info(f"Advance to instruction page {idx}")
                        pygame.event.clear()

                        # After this page, check if we should start a practice/block.
                        # 0-back
                        page_to_count_0back = {}
                        for nm in ("PRACTICE1", "BLOCK1", "BLOCK2"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_0back[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_0back:
                            block_name, trials = page_to_count_0back[idx]
                            logger.info(f"[0-back] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_0back_target(screen)
                            play_stimuli(trials, screen, block_name, pid, start_time)

                        # 1-back
                        page_to_count_1back = {}
                        for nm in ("PRACTICE2", "BLOCK3", "BLOCK4"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_1back[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_1back:
                            block_name, trials = page_to_count_1back[idx]
                            logger.info(f"[1-back] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time)

                        # 2-back
                        page_to_count_2back = {}
                        for nm in ("PRACTICE3", "BLOCK5", "BLOCK6"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_2back[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_2back:
                            block_name, trials = page_to_count_2back[idx]
                            logger.info(f"[2-back] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time)

                        break
            else:
                # If break not triggered: continue loop
                clock.tick(60)
                continue
            # If break triggered: exit waiting loop for this page
            break


def play_stimuli(trial_num: int, screen: pygame.Surface, block: str, pid: str, start_time: str) -> None:
    """
    Play `trial_num` stimuli with mapping background.
    - QUIT closes the program
    - ESC toggles full screen
    - Q / X aborts playback (return from this function)
    - During stimulus ON, D/K are recorded as participant answers (mapping depends on VERSION)
    """
    block_0back = ["PRACTICE1", "BLOCK1", "BLOCK2"]
    block_1back = ["PRACTICE2", "BLOCK3", "BLOCK4"]
    block_2back = ["PRACTICE3", "BLOCK5", "BLOCK6"]

    logger.info(f"Play stimuli: trial_num = {trial_num}, block = {block}")
    paths = pull_stimuli(trial_num)
    logger.debug(f"Paths of stimuli images = {paths}")
    mapping_bg = _load_mapping_surface(screen)
    region = _stim_region_rect(screen)

    # ---------- Helpers ----------
    def _map_key_to_answer(key: int) -> tuple[Answer | None, str | None]:
        """
        Map keyboard to participant Answer per VERSION, and return a human-friendly raw key label.
        VERSION 1: D -> DIFFERENT, K -> SAME
        VERSION 2: D -> SAME, K -> DIFFERENT
        Returns (Answer_or_None, 'd'/'k'/None).
        """
        if key == pygame.K_d:
            return ((Answer.SAME if cfg.VERSION == 1 else Answer.DIFFERENT), "d")
        if key == pygame.K_k:
            return ((Answer.DIFFERENT if cfg.VERSION == 1 else Answer.SAME), "k")
        return (None, None)

    def _handle_events_capture_answer() -> tuple[bool, Answer | None, str | None]:
        """
        Process events during stimulus ON window.
        - ESC: toggle fullscreen
        - Q/X: abort -> interrupt=True
        - D/K: capture participant answer (mapped by VERSION), log raw key
        Return (interrupt, participant_answer, raw_key_str)
        """
        participant_ans: Answer | None = None
        raw_key: str | None = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("User requested quit during stimuli.")
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed: toggling full screen.")
                    toggle_full_screen(screen)
                elif event.key in (pygame.K_q, pygame.K_x):
                    logger.info("User aborted stimuli with key (Q/X).")
                    return True, participant_ans, raw_key
                else:
                    mapped, raw = _map_key_to_answer(event.key)
                    if mapped is not None:
                        participant_ans = mapped
                        raw_key = raw
                        logger.info(f"Participant keydown: '{raw_key}' -> mapped to {participant_ans.value}")
        return False, participant_ans, raw_key

    def _wait_ms_with_events_capture(ms: int) -> tuple[bool, Answer | None, str | None]:
        """
        Wait for `ms` ms while handling events and capturing at most one participant answer (D/K).
        Keyboard lock: accept only the FIRST valid key within the window; ignore subsequent presses.
        Returns (interrupt, participant_answer_or_None, raw_key_or_None).
        """
        start = pygame.time.get_ticks()
        participant_ans: Answer | None = None
        raw_key: str | None = None
        locked = False  # keyboard lock: True after first valid press

        while pygame.time.get_ticks() - start < ms:
            # We still call the handler to process ESC / QUIT / Q/X,
            # but we enforce the "first-press wins" rule here.
            interrupted, ans, rk = _handle_events_capture_answer()
            if interrupted:
                return True, participant_ans, raw_key

            if not locked and ans is not None:
                participant_ans = ans
                raw_key = rk
                locked = True
                logger.debug(f"Keyboard locked for this trial (first key='{raw_key}').")

                # Immediate feedback in practice blocks (PRACTICE1/2/3), for 0/1/2-back
                # Suppress immediate feedback on PRACTICE2 trial 1 and PRACTICE3 trials 1–2
                if (
                    block in ("PRACTICE1", "PRACTICE2", "PRACTICE3")
                    and not ((block == "PRACTICE2" and i == 1) or (block == "PRACTICE3" and i in (1, 2)))
                ):
                    # Map Answer.NOGO -> correct=None (means "no response expected");
                    # otherwise correct=True (means "a response was expected").
                    correct_flag = None if correct == Answer.NOGO else True
                    try:
                        fb.show_immediate(
                            screen,
                            block_name=block,
                            participant_ans=1,  # any non-None value indicates a key was pressed
                            correct=correct_flag,
                            is_correct=(participant_ans == correct),
                        )
                    except Exception as e:
                        logger.warning(f"Immediate feedback failed: {e}")

            # Else: ignore any further key presses silently

            pygame.time.delay(5)
        return False, participant_ans, raw_key

    def _handle_events_only_interrupt() -> bool:
        """
        Handle events without capturing answers (used during ISI).
        Returns True if playback should be interrupted (QUIT or Q/X).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("User requested quit during ISI.")
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed: toggling full screen.")
                    toggle_full_screen(screen)
                elif event.key in (pygame.K_q, pygame.K_x):
                    logger.info("User aborted stimuli during ISI.")
                    return True
        return False

    def _wait_ms_with_events_only(ms: int) -> bool:
        """
        Wait for `ms` ms, keep UI responsive, do not capture D/K, only honor QUIT or Q/X.
        Returns True if interrupted.
        """
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < ms:
            if _handle_events_only_interrupt():
                return True
            pygame.time.delay(5)
        return False

    total = len(paths)
    prev_path: Path | None = None
    prev2_path: Path | None = None

    for i, p in enumerate(paths, 1):
        # Clear leftover inputs from previous trial (keyboard lock precondition)
        pygame.event.clear()

        # Draw mapping + stimulus
        image = pygame.image.load(str(p)).convert_alpha()
        screen.blit(mapping_bg, (0, 0))
        _blit_into_region(screen, image, region)
        pygame.display.flip()
        logger.debug(f"Trial {i}/{total}: show {p.name} for {cfg.STIMULUS_DURATION_MS} ms")

        # correctness setup for current block (0/1/2-back), computed BEFORE the response window
        correct: Answer | None = None
        if block in block_0back:
            if not cfg.ANSWER0:
                logger.warning("ANSWER0 is not set; 0-back correctness cannot be computed.")
            else:
                try:
                    is_target = Path(p).resolve() == Path(cfg.ANSWER0).resolve()
                except Exception:
                    is_target = str(p) == str(cfg.ANSWER0)
                correct = Answer.SAME if is_target else Answer.DIFFERENT

        elif block in block_1back:
            # 1-back: first trial is NOGO, else compare with previous stimulus
            correct = Answer.NOGO if i == 1 else (
                Answer.SAME if (prev_path is not None and p.name == prev_path.name) else Answer.DIFFERENT
            )

        elif block in block_2back:
            # 2-back: first two trials are NOGO, else compare with the stimulus two steps back
            correct = Answer.NOGO if i <= 2 else (
                Answer.SAME if (prev2_path is not None and p.name == prev2_path.name) else Answer.DIFFERENT
            )

        # Visible window: capture participant input
        interrupted, participant_ans, raw_key = _wait_ms_with_events_capture(cfg.STIMULUS_DURATION_MS)
        if interrupted:
            logger.info(f"Interrupted during stimulus ON at trial {i}/{total}.")
            return

        # Log 0-back result
        if block in block_0back:
            if participant_ans is None:
                participant_ans = Answer.NOGO
                raw_key = None  # no key pressed
            if correct is not None:
                is_correct = (participant_ans == correct)
                # Raw key logging (explicitly log 'd'/'k' or 'none')
                raw_repr = raw_key if raw_key in ("d", "k") else "none"
                logger.info(
                    f"Trial {i}/{total} | 0-back | correct={correct.value} | "
                    f"participant={participant_ans.value} | key={raw_repr} | is_correct={is_correct} | stim={p.name}"
                )
            saves.update_save(pid, block, "0back", "0back", correct.value, participant_ans.value, start_time)
            logger.info(f"Trial results saved to ./result/{pid}_NB_results.csv")

            fb.show_after_trial(
                screen,
                block_name=block,
                is_practice_only=True,
                # None if no key; any non-None if there was a keypress:
                participant_ans=(None if raw_key is None else 1),
                # None if NOGO (no response expected); True otherwise (response expected):
                correct=(None if correct == Answer.NOGO else True),
                is_correct=is_correct,
                wait_ms=getattr(cfg, "FEEDBACK_DURATION", getattr(cfg, "FEEDBACK_DURATION_MS", 600)),
            )
        
        # Log 1-back result
        if block in block_1back:    
            if participant_ans is None:
                participant_ans = Answer.NOGO
                raw_key = None  # no key pressed

            is_correct = (participant_ans == correct)
            raw_repr = raw_key if raw_key in ("d", "k") else "none"
            logger.info(
                f"Trial {i}/{total} | 1-back | correct={correct.value} | "
                f"participant={participant_ans.value} | key={raw_repr} | "
                f"is_correct={is_correct} | stim={p.name}"
            )

            # remember current stimulus for next trial comparison
            prev_path = p
            saves.update_save(pid, block, "1back", "1back", correct.value, participant_ans.value, start_time)
            logger.info(f"Trial results saved to ./result/{pid}_NB_results.csv")

            # PRACTICE2: show feedback for trials >= 2 ONLY (skip trial 1 entirely)
            if block == "PRACTICE2" and i >= 2:
                fb.show_after_trial(
                    screen,
                    block_name=block,
                    is_practice_only=True,
                    participant_ans=(None if raw_key is None else 1),
                    correct=(None if correct == Answer.NOGO else True),
                    is_correct=is_correct,
                    wait_ms=getattr(cfg, "FEEDBACK_DURATION", getattr(cfg, "FEEDBACK_DURATION_MS", 600)),
                )

        # Log 2-back result
        if block in block_2back:
            # (do NOT recompute 'correct' here; it was computed before the response window)

            if participant_ans is None:
                participant_ans = Answer.NOGO
                raw_key = None  # no key pressed

            is_correct = (participant_ans == correct)
            raw_repr = raw_key if raw_key in ("d", "k") else "none"
            logger.info(
                f"Trial {i}/{total} | 2-back | correct={correct.value} | "
                f"participant={participant_ans.value} | key={raw_repr} | "
                f"is_correct={is_correct} | stim={p.name}"
            )

            # update history for next trial
            if prev_path is not None:
                prev2_path = prev_path
            prev_path = p
            saves.update_save(pid, block, "2back", "2back", correct.value, participant_ans.value, start_time)
            logger.info(f"Trial results saved to ./result/{pid}_NB_results.csv")

            # PRACTICE3: show feedback for trials >= 3 ONLY (skip trials 1–2 entirely)
            if block == "PRACTICE3" and i >= 3:
                fb.show_after_trial(
                    screen,
                    block_name=block,
                    is_practice_only=True,
                    participant_ans=(None if raw_key is None else 1),
                    correct=(None if correct == Answer.NOGO else True),
                    is_correct=is_correct,
                    wait_ms=getattr(cfg, "FEEDBACK_DURATION", getattr(cfg, "FEEDBACK_DURATION_MS", 600)),
                )

        # ISI gray screen (do NOT capture answers here)
        if cfg.ISI_MS > 0:
            screen.fill(cfg.GRAY_RGB)
            pygame.display.flip()
            if _wait_ms_with_events_only(cfg.ISI_MS):
                logger.info(f"Interrupted during ISI at trial {i}/{total}.")
                return

        # Explicit marker so we can confirm the loop proceeds
        logger.debug(f"End of trial {i}/{total}")


def play_0back_target(screen: pygame.Surface) -> None:
    """
    Show the selected Attneave target over the mapping background.
    - ESC toggles full screen
    - Q / X abort early
    - QUIT closes the program
    Auto-exits after TARGET_DISPLAY ms if not aborted.
    """
    # Load mapping background
    mapping_path = Path("resources/0_back_target_shape/target_shape.png")
    mapping = pygame.image.load(str(mapping_path)).convert()

    # Pick and load the Attneave target
    path = _pick_0back_target_path()
    cfg.ANSWER0 = str(path)  # persist for 0-back answer checking
    logger.debug(f"ANSWER0 set to: {cfg.ANSWER0}")
    logger.debug(f"Picked {path} as the target for 0-back trials")
    target_img = pygame.image.load(str(path)).convert_alpha()

    # Compute region (slightly lower than center)
    region = _stim_region_rect(screen).copy()
    region.y += int(0.03 * screen.get_height())  # downward offset

    # Draw and present
    screen.fill(cfg.GRAY_RGB)
    screen.blit(mapping, (0, 0))
    _blit_into_region(screen, target_img, region)
    pygame.display.flip()

    def _handle_events() -> bool:
        """Return True if playback should be interrupted."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("User requested quit during 0-back target.")
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed: toggling full screen.")
                    toggle_full_screen(screen)
                elif event.key in (pygame.K_q, pygame.K_x):
                    logger.info("User aborted 0-back target with key.")
                    return True
        return False

    # Keep visible for TARGET_DISPLAY ms (or until interrupted)
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < cfg.TARGET_DISPLAY:
        if _handle_events():
            return
        pygame.time.delay(5)


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
