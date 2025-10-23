# ./src/core/test_flow.py

from pathlib import Path
from typing import List, Tuple

import pygame

from utils import config as cfg
from utils.logger import get_logger
from core.pull_stimuli import (
    pull_stimuli_1back,
    pull_stimuli_2back,
    pull_stimuli_3back,
)
from utils import feedback as fb
from utils.feedback import show_feedback_timed
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
    """Select the instruction resource directory."""
    return cfg.RESOURCES_DIR / "instructions"


def _load_mapping_surface(screen: pygame.Surface) -> pygame.Surface:
    """Load ./resources/mapping/1.png and scale to full screen as background."""
    path = cfg.RESOURCES_DIR / "mapping" / "1.png"
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


def _calculate_signal_detection(condition: str, key_response: str) -> str:
    """
    Calculate signal detection theory classification for trial analysis.
    
    Args:
        condition: stimulus type (match, nonmatch, or null)
        key_response: participant response (space, none)
        
    Returns:
        Signal detection classification: hit, miss, false_alarm, correct_rejection, or null
    """
    if condition == "null":
        return "null"
    elif condition == "match":
        # Target present trials
        if key_response == "space":
            return "hit"        # Responded to target
        else:
            return "miss"       # Failed to respond to target
    elif condition == "nonmatch":
        # Target absent trials  
        if key_response == "space":
            return "false_alarm"  # Incorrectly responded to non-target
        else:
            return "correct_rejection"  # Correctly withheld response to non-target
    else:
        return "null"


def show_instructions(screen: pygame.Surface, pid: str, start_time: str, start_page: int, end_page: int) -> None:
    """
    Play instructions sequentially from ./resources/instructions:
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

                        # 1-back
                        page_to_count_1back = {}
                        for nm in ("PRACTICE1", "BLOCK1", "BLOCK2"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_1back[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_1back:
                            block_name, trials = page_to_count_1back[idx]
                            logger.info(f"[1-back] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time)

                        # 2-back
                        page_to_count_2back = {}
                        for nm in ("PRACTICE2", "BLOCK3", "BLOCK4"):
                            count_name = f"{nm}_COUNT"
                            if hasattr(cfg, nm) and hasattr(cfg, count_name):
                                page_to_count_2back[getattr(cfg, nm)] = (nm, getattr(cfg, count_name))

                        if idx in page_to_count_2back:
                            block_name, trials = page_to_count_2back[idx]
                            logger.info(f"[2-back] Trigger at page {idx}: play {trials} trials for block={block_name}")
                            play_stimuli(trials, screen, block_name, pid, start_time)

                        # 3-back
                        page_to_count_3back = {}
                        for nm in ("PRACTICE3", "BLOCK5", "BLOCK6"):
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

def play_stimuli(trial_num: int, screen: pygame.Surface, block_name: str, pid: str, start_time: str) -> None:
    """
    Present a sequence of stimuli for the given block, with extended response window.

    Extended response window implementation:
      - Response window extends from stimulus onset until next stimulus presentation
      - Total response time: STIMULUS_DURATION_MS + ISI_MS (e.g., 3000ms + 1000ms = 4000ms)
      - Responses accepted during both stimulus display and ISI periods
      
    Keyboard handling:
      - Keyboard throttle: accept at most ONE key event every 100 ms.
      - If multiple key presses occur within the 100 ms window, handle ONLY the first
        and clear the remaining key events in that window.
      - ESC toggles fullscreen via toggle_full_screen().
      - SPACE: only the first SPACE press per trial is accepted (flag-gated).
      - Other keys are ignored for now.

    Responsibilities:
    1) Choose the appropriate pull_stimuli_*back builder based on block_name.
    2) Show each selected stimulus for cfg.STIMULUS_DURATION_MS.
    3) Continue accepting responses during ISI period until next stimulus.
    4) Smart feedback timing: immediate feedback when responded, delayed 1000ms feedback for missed targets.
    """
    # --- Keyboard throttle (accept at most 1 key per 100 ms) ---
    THROTTLE_MS = 100
    last_accept_ms = -THROTTLE_MS  # timestamp (ms) of last accepted key

    # Practice blocks set
    name = (block_name or "").upper()
    PRACTICE_BLOCKS = {"PRACTICE1", "PRACTICE2", "PRACTICE3", "PRACTICE4"}
    is_practice = name in PRACTICE_BLOCKS

    # --- Per-trial timing state (set/reset each trial) ---
    _trial_stim_on_ms = 0        # timestamp when current stimulus appeared on screen
    _feedback_requested = False  # flag indicating feedback should be displayed
    _feedback_type = None        # type of feedback to show ("correct"/"incorrect")
    response_time_ms = None      # measured response time from stimulus onset to keypress


    def _poll_events_throttled() -> None:
        """
        Poll pygame events once with a 100 ms keyboard throttle.

        - If multiple key presses occur within the 100 ms window,
          only the FIRST is handled; the rest are cleared.
        - ESC toggles fullscreen via toggle_full_screen().
        - SPACE is handled only once per trial (gated by _is_space_pressed).
        - Records feedback requirements for later display during appropriate timing phases.
        """
        nonlocal last_accept_ms, _is_space_pressed, _trial_stim_on_ms, response_time_ms, _feedback_requested, _feedback_type
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
                    # Process SPACE keypress only once per trial to prevent multiple responses
                    if not _is_space_pressed:
                        _is_space_pressed = True
                        response_time_ms = now - _trial_stim_on_ms
                        
                        # Evaluate response correctness and prepare feedback for practice blocks
                        if cfg.ANSWER == Answer.SAME:
                            cfg.STATUS = Status.CORRECT
                            if is_practice:
                                _feedback_requested = True
                                _feedback_type = "correct"
                        elif cfg.ANSWER == Answer.DIFFERENT:
                            cfg.STATUS = Status.RESPONSE_ERROR
                            if is_practice:
                                _feedback_requested = True
                                _feedback_type = "incorrect"
                        elif cfg.ANSWER == Answer.NOGO:
                            cfg.STATUS = Status.RESPONSE_ERROR
                            if is_practice:
                                _feedback_requested = True
                                _feedback_type = "incorrect"

                # Debug hotkeys for testing feedback display
                elif ev.key == pygame.K_c:
                    fb.show_feedback(screen, "correct")
                elif ev.key == pygame.K_i:
                    fb.show_feedback(screen, "incorrect")

                # After handling the first accepted key in this window,
                # clear any remaining KEYDOWNs to enforce "first only"
                pygame.event.clear(pygame.KEYDOWN)
                return

    # ---- Decide n-back level from block name ----
    block_to_level = {
        # 1-back
        "PRACTICE1": 1, "BLOCK1": 1, "BLOCK2": 1,
        # 2-back
        "PRACTICE2": 2, "BLOCK3": 2, "BLOCK4": 2,
        # 3-back
        "PRACTICE3": 3, "BLOCK5": 3, "BLOCK6": 3,
    }
    level = block_to_level.get(name)
    if level is None:
        if logger:
            logger.warning(f"Unknown block_name '{block_name}', defaulting to 1-back.")
        level = 1

    builders = {
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
        mapping_path = cfg.RESOURCES_DIR / "mapping" / "1.png"
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
        # Initialize trial state variables for response tracking and feedback control
        _is_space_pressed = False
        _feedback_requested = False
        _feedback_type = None
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

        # --- Response window implementation with precise feedback timing control ---
        # Total response window spans from stimulus onset to next stimulus presentation
        trial_start = pygame.time.get_ticks()
        _trial_stim_on_ms = trial_start  # Reference point for response time calculation
        total_response_window = cfg.STIMULUS_DURATION_MS + cfg.ISI_MS  # Complete response duration
        
        # Phase 1: Stimulus display period - maintain exact 500ms timing regardless of responses
        while (pygame.time.get_ticks() - trial_start) < cfg.STIMULUS_DURATION_MS:
            _poll_events_throttled()
            # Response detection occurs but feedback is deferred to maintain stimulus timing
            pygame.time.delay(5)

        # Phase 2: ISI period with feedback display and continued response monitoring
        screen.fill(cfg.GRAY_RGB)
        pygame.display.flip()
        isi_background = screen.copy()
        
        # Display feedback immediately if response occurred during stimulus or ISI phases
        if _feedback_requested and is_practice:
            elapsed_time = pygame.time.get_ticks() - trial_start
            remaining_window = total_response_window - elapsed_time
            feedback_duration = min(cfg.FEEDBACK_DURATION, remaining_window)
            
            show_feedback_timed(screen, _feedback_type, feedback_duration, isi_background)
            _feedback_requested = False  # Prevent duplicate feedback display
        
        # Continue response collection during remaining ISI period
        while (pygame.time.get_ticks() - trial_start) < total_response_window:
            _poll_events_throttled()
            
            # Handle feedback for responses that occur during ISI period
            if _feedback_requested and is_practice:
                elapsed_time = pygame.time.get_ticks() - trial_start
                remaining_window = total_response_window - elapsed_time
                feedback_duration = min(cfg.FEEDBACK_DURATION, remaining_window)
                
                show_feedback_timed(screen, _feedback_type, feedback_duration, isi_background)
                _feedback_requested = False
                break
            
            pygame.time.delay(5)

        # --- Trial data analysis and recording ---
        # Extract stimulus filename for data tracking
        try:
            stimuli_filename = path.name
        except Exception:
            stimuli_filename = "unknown_stimulus"
        
        # Determine condition based on n-back rule evaluation
        if cfg.ANSWER == Answer.SAME:
            condition = "match"
            key_correct = "space"
        elif cfg.ANSWER == Answer.DIFFERENT or cfg.ANSWER == Answer.NOGO:
            condition = "nonmatch"  
            key_correct = "none"
        else:
            # Handle cases where answer classification is undefined
            condition = "null"
            key_correct = "none"
            
        # Record actual participant response
        key_response = "space" if _is_space_pressed else "none"
        
        # Evaluate response correctness based on expected vs actual behavior
        if condition == "null":
            # Trials that cannot be evaluated due to insufficient n-back history
            correct_response = "null"
        elif (condition == "match" and key_response == "space") or (condition == "nonmatch" and key_response == "none"):
            correct_response = "correct"
        else:
            correct_response = "incorrect"
        
        # Calculate theoretical trial duration from stimulus onset to ISI completion
        trial_duration = cfg.STIMULUS_DURATION_MS + cfg.ISI_MS  # Fixed duration: 500ms + 2500ms = 3000ms

        # Calculate signal detection classification for d-prime analysis
        signal_detection = _calculate_signal_detection(condition, key_response)

        # Record comprehensive trial data for behavioral analysis
        update_save(
            participant_id=pid,
            block=block_name,
            stimuli_path=stimuli_filename,
            condition=condition,
            key_correct=key_correct,
            key_response=key_response,
            correct=correct_response,
            response_time_ms=response_time_ms,
            trial_duration_ms=trial_duration,
            start_time=start_time,
            trial_position=i,
            n_back_level=level,
            signal_detection=signal_detection,
        )

        # Provide delayed feedback for missed targets during practice blocks
        if not _is_space_pressed and condition == "match" and is_practice:
            elapsed_time = pygame.time.get_ticks() - trial_start
            delay_until_feedback = max(0, total_response_window - cfg.FEEDBACK_DURATION - elapsed_time)
            
            # Schedule feedback appearance in final portion of response window
            if delay_until_feedback > 0:
                pygame.time.delay(delay_until_feedback)
            
            # Display feedback for remaining available time
            final_elapsed = pygame.time.get_ticks() - trial_start
            remaining_window = max(0, total_response_window - final_elapsed)
            feedback_duration = min(cfg.FEEDBACK_DURATION, remaining_window)
            
            if feedback_duration > 0:
                show_feedback_timed(screen, "incorrect", feedback_duration, isi_background)

        # Provide feedback for correct non-responses during practice blocks  
        elif not _is_space_pressed and condition == "nonmatch" and is_practice:
            elapsed_time = pygame.time.get_ticks() - trial_start
            remaining_window = total_response_window - elapsed_time
            feedback_duration = min(cfg.FEEDBACK_DURATION, remaining_window)
            if feedback_duration > 0:
                show_feedback_timed(screen, "correct", feedback_duration, isi_background)

        # Reset trial state for next stimulus presentation
        cfg.STATUS = Status.NO_RESPONSE

    # Log completion of all stimuli presentation for this block
    if logger:
        logger.info(f"Play stimuli end | block={block_name}")
