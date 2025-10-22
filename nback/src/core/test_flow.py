# ./src/core/test_flow.py

from pathlib import Path
from typing import List, Tuple

import pygame

from utils import config as cfg
from utils.logger import get_logger
from core.pull_stimuli import (
    _pick_0back_target_path,
    pull_stimuli_0back,
    pull_stimuli_1back,
    pull_stimuli_2back,
    pull_stimuli_3back,
)
from utils import feedback as fb
from utils.enums import Answer, Status
from utils.saves import update_save

# ---------- Internal state ----------
_is_fullscreen = True                           # acticate in full-screen mode
logger = get_logger("./src/core/test_flow")     # create logger


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


def show_instructions(screen: pygame.Surface, pid: str, start_time: str, start_page: int, end_page: int) -> None:
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

    for idx in range(start_page, end_page):
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

                        # 3-back
                        page_to_count_3back = {}
                        for nm in ("PRACTICE4", "BLOCK7", "BLOCK8"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_3back[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_3back:
                            block_name, trials = page_to_count_3back[idx]
                            logger.info(f"[3-back] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time)

                        break
            else:
                # If break not triggered: continue loop
                clock.tick(60)
                continue
            # If break triggered: exit waiting loop for this page
            break

def play_0back_target(screen: pygame.Surface) -> None:
    """
    Show the selected Attneave target over the mapping background.
    - ESC toggles full screen
    - QUIT closes the program
    Auto-exits after TARGET_DISPLAY ms if not aborted.
    """
    # Load mapping background
    mapping_path = Path("resources/0_back_target_shape/target_shape.png")
    mapping = pygame.image.load(str(mapping_path)).convert()

    # Pick and load the Attneave target
    path = _pick_0back_target_path()
    logger.debug(f"Picked {path} as the target for 0-back trials")
    target_img = pygame.image.load(str(path)).convert_alpha()

    # Compute region (slightly lower than center)
    region = _stim_region_rect(screen).copy()
    region.y += int(0.03 * screen.get_height())

    # Draw and present
    screen.fill(cfg.GRAY_RGB)
    screen.blit(mapping, (0, 0))
    _blit_into_region(screen, target_img, region)
    pygame.display.flip()

    def _handle_events() -> bool:
        """Quit game / Toggle full screen"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("User requested quit during 0-back target.")
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed: toggling full screen.")
                    toggle_full_screen(screen)
        return False

    # Keep visible for TARGET_DISPLAY ms (or until interrupted)
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < cfg.TARGET_DISPLAY:
        if _handle_events():
            return
        pygame.time.delay(5)


def play_stimuli(trial_num: int, screen: pygame.Surface, block_name: str, pid: str, start_time: str) -> None:
    """
    Present a sequence of stimuli for the given block, with keyboard listening.

    Adds:
      - Keyboard throttle: accept at most ONE key event every 100 ms.
      - If multiple key presses occur within the 100 ms window, handle ONLY the first
        and clear the remaining key events in that window.
      - ESC toggles fullscreen via toggle_full_screen().
      - SPACE: only the first SPACE press per trial is accepted (flag-gated).
      - Other keys are ignored for now.

    Responsibilities:
    1) Choose the appropriate pull_stimuli_*back builder based on block_name.
    2) Show each selected stimulus for cfg.STIMULUS_DURATION_MS.
    3) After each stimulus, show a gray ISI screen for cfg.ISI_MS.
    4) Feedback/answer saving is minimal and practice-only for SPACE; end-of-trial timeout feedback handled per spec.
    """
    # --- Keyboard throttle (accept at most 1 key per 100 ms) ---
    THROTTLE_MS = 100
    last_accept_ms = -THROTTLE_MS  # timestamp (ms) of last accepted key

    # Practice blocks set
    name = (block_name or "").upper()
    PRACTICE_BLOCKS = {"PRACTICE1", "PRACTICE2", "PRACTICE3", "PRACTICE4"}
    is_practice = name in PRACTICE_BLOCKS

    # --- Per-trial timing state (set/reset each trial) ---
    _trial_stim_on_ms = 0        # NEW: ms timestamp when the current stimulus appeared
    response_time_ms = None      # NEW: measured RT from stimulus-on to first accepted SPACE


    def _poll_events_throttled() -> None:
        """
        Poll pygame events once with a 100 ms keyboard throttle.

        - If multiple key presses occur within the 100 ms window,
          only the FIRST is handled; the rest are cleared.
        - ESC toggles fullscreen via toggle_full_screen().
        - SPACE is handled only once per trial (gated by _is_space_pressed).
        - Other keys are ignored for now.
        """
        nonlocal last_accept_ms, _is_space_pressed, _trial_stim_on_ms, response_time_ms
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if logger:
                    logger.info("QUIT received during stimuli; exiting playback.")
                raise SystemExit

            if ev.type == pygame.KEYDOWN:
                now = pygame.time.get_ticks()
                # Enforce 100 ms lock
                if (now - last_accept_ms) < THROTTLE_MS:
                    # Too soon: drop further KEYDOWNs in this window
                    pygame.event.clear(pygame.KEYDOWN)
                    return

                # Accept this key
                last_accept_ms = now

                if ev.key == pygame.K_ESCAPE:
                    if logger:
                        logger.info("ESC pressed: toggling full screen.")
                    toggle_full_screen(screen)

                elif ev.key == pygame.K_SPACE:
                    # Handle SPACE only once per trial
                    if not _is_space_pressed:
                        _is_space_pressed = True
                        response_time_ms = now - _trial_stim_on_ms
                        
                        # Judge against current cfg.ANSWER and set cfg.STATUS
                        if cfg.ANSWER == Answer.SAME:
                            cfg.STATUS = Status.CORRECT
                            if is_practice:
                                fb.show_feedback(screen, "correct")
                        elif cfg.ANSWER == Answer.DIFFERENT:
                            # Treat as incorrect for generic status
                            cfg.STATUS = Status.RESPONSE_ERROR
                            if is_practice:
                                fb.show_feedback(screen, "incorrect")
                        elif cfg.ANSWER == Answer.NOGO:
                            # No-Go pressed -> incorrect
                            cfg.STATUS = Status.RESPONSE_ERROR
                            if is_practice:
                                fb.show_feedback(screen, "incorrect")

                # Debug hotkeys (optional; do not affect the SPACE flag)
                elif ev.key == pygame.K_c:
                    fb.show_feedback(screen, "correct")
                elif ev.key == pygame.K_i:
                    fb.show_feedback(screen, "incorrect")
                elif ev.key == pygame.K_t:
                    fb.show_feedback(screen, "timeout")

                # After handling the first accepted key in this window,
                # clear any remaining KEYDOWNs to enforce "first only"
                pygame.event.clear(pygame.KEYDOWN)
                return

    # ---- Decide n-back level from block name ----
    block_to_level = {
        # 0-back
        "PRACTICE1": 0, "BLOCK1": 0, "BLOCK2": 0,
        # 1-back
        "PRACTICE2": 1, "BLOCK3": 1, "BLOCK4": 1,
        # 2-back
        "PRACTICE3": 2, "BLOCK5": 2, "BLOCK6": 2,
        # 3-back
        "PRACTICE4": 3, "BLOCK7": 3, "BLOCK8": 3,
    }
    level = block_to_level.get(name)
    if level is None:
        if logger:
            logger.warning(f"Unknown block_name '{block_name}', defaulting to 0-back.")
        level = 0

    builders = {
        0: pull_stimuli_0back,
        1: pull_stimuli_1back,
        2: pull_stimuli_2back,
        3: pull_stimuli_3back,
    }
    builder = builders[level]

    if logger:
        logger.info(f"Play stimuli start | block={block_name} (n-back={level}), trials={trial_num}")

    # ---- Build the stimulus sequence ----
    try:
        seq, ans = builder(trial_num)  # seq -> List[Path], ans -> List[Answer]
    except Exception as e:
        if logger:
            logger.exception(f"Failed to build stimuli for {block_name}: {e}")
        return

    # ---- Load & scale mapping background to screen ----
    try:
        mapping_path = cfg.RESOURCES_DIR / "mapping" / f"{cfg.VERSION}.png"
        bg = pygame.image.load(str(mapping_path)).convert()
    except Exception as e:
        if logger:
            logger.exception(f"Cannot load mapping background: {e}")
        return

    sw, sh = screen.get_width(), screen.get_height()
    bg_scaled = pygame.transform.smoothscale(bg, (sw, sh))

    # Region where stimuli should be placed (normalized coords)
    l_n, t_n, w_n, h_n = cfg.STIM_REGION
    region = pygame.Rect(int(l_n * sw), int(t_n * sh), int(w_n * sw), int(h_n * sh))

    # ---- Present each stimulus ----
    for i, path in enumerate(seq, start=1):
        # Per-trial: reset the SPACE acceptance flag
        _is_space_pressed = False
        response_time_ms = None
        cfg.STATUS = Status.NO_RESPONSE

        # Set up correct answer for the current trial
        # (ans is 0-based; enumerate starts at 1)
        try:
            cfg.ANSWER = ans[i - 1]
        except Exception:
            cfg.ANSWER = None  # fallback if indexing fails
        if logger:
            logger.info(f"Trial {i}: stimulus = {str(path)}")
            logger.info(f"Trial {i}: correct answer = {cfg.ANSWER}")

        # Draw background first
        screen.blit(bg_scaled, (0, 0))

        try:
            stim = pygame.image.load(str(path)).convert_alpha()
            # Fit the stimulus into the region (keep aspect ratio)
            iw, ih = stim.get_width(), stim.get_height()
            scale = min(region.width / max(iw, 1), region.height / max(ih, 1))
            new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            stim_scaled = pygame.transform.smoothscale(stim, new_size)

            # Center in region
            dx = region.x + (region.width - stim_scaled.get_width()) // 2
            dy = region.y + (region.height - stim_scaled.get_height()) // 2
            screen.blit(stim_scaled, (dx, dy))
        except Exception as e:
            if logger:
                logger.warning(f"Trial {i}: failed to load {path}: {e}")
            pygame.draw.rect(screen, cfg.YELLOW_RGB, region, width=2)

        pygame.display.flip()

        if logger:
            try:
                fname = path.name
            except Exception:
                fname = "N/A"
            logger.debug(f"Trial {i}/{len(seq)} | show: {fname} for {cfg.STIMULUS_DURATION_MS} ms")

        # --- Stimulus on-screen duration with keyboard polling ---
        stim_start = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - stim_start) < cfg.STIMULUS_DURATION_MS:
            _poll_events_throttled()
            pygame.time.delay(5)

        
        # --- Prepare for saves ---
        condition = str(level) + "-back"
        if cfg.ANSWER == Answer.SAME:
            correct = "same"
        elif cfg.ANSWER == Answer.DIFFERENT:
            correct = "different"
        elif cfg.ANSWER == Answer.NOGO:
            correct = "nogo"
        start_time = start_time


        # --- End-of-trial response / saves handling (per spec) ---
        if cfg.STATUS == Status.NO_RESPONSE:
            # No response received within the window -> show timeout in practice
            if cfg.ANSWER == Answer.DIFFERENT or cfg.ANSWER == Answer.NOGO:
                if is_practice:
                    fb.show_feedback(screen, "correct")
                update_save(pid, block_name, condition, correct, None, None, start_time)

            elif cfg.ANSWER == Answer.SAME:
                if is_practice:
                    fb.show_feedback(screen, "timeout")
                update_save(pid, block_name, condition, correct, cfg.STIMULUS_DURATION_MS, "no response error", start_time)
        else:
            response_time_ms -= stim_start
            if cfg.STATUS == Status.CORRECT:
                update_save(pid, block_name, condition, correct, response_time_ms, None, start_time)
            elif cfg.STATUS == Status.NO_GO_ERROR:
                update_save(pid, block_name, condition, correct, response_time_ms, "no go error", start_time)
            elif cfg.STATUS == Status.RESPONSE_ERROR:
                update_save(pid, block_name, condition, correct, response_time_ms, "response error", start_time)

            # A response was made -> reset STATUS for the next trial
            cfg.STATUS = Status.NO_RESPONSE


        # --- ISI: gray screen with keyboard polling ---
        screen.fill(cfg.GRAY_RGB)
        pygame.display.flip()
        isi_start = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - isi_start) < cfg.ISI_MS:
            _poll_events_throttled()
            pygame.time.delay(5)

        logger.info(f"Play stimuli end | block={block_name}")
