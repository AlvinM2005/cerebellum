"""
Test blocks: speed_test / accuracy_test / varying_test_1 / varying_test_2.

- No trial-by-trial feedback (tests).
- Interval behavior mirrors goal_practice.interval (duration-limited, unlimited trials).
- Varying tests mix Speed and Accuracy intervals in randomized order, with counts
  from cfg.VARYING_TEST_SPEED_COUNT and cfg.VARYING_TEST_ACCURACY_COUNT.
- Block execution order is determined by cfg.task_sequence (e.g., V S V A).
  The first 'V' maps to varying_test_1 and the second to varying_test_2.
"""

from __future__ import annotations

import datetime
import random
from pathlib import Path

import pygame

import utils.config as cfg
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import toggle_full_screen
from utils.saves import update_save, finalize_block_end_time
from utils.paths import WORD_COLOR_STIMULI, GSS_Speed, GSS_Accuracy


logger = get_logger("./src/core/test")


def _flush_input() -> None:
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _show_center_with_goal(screen: pygame.Surface, stim_path: Path, goal: str) -> None:
    """Draw stimulus centered and goal cue (Speed/Accuracy) top-right, half size."""
    screen.fill(cfg.BLACK_RGB)
    try:
        stim_img = pygame.image.load(str(stim_path)).convert_alpha()
    except Exception as e:
        logger.error(f"[test:{goal}] Failed to load stimulus: {stim_path} | {e}")
        return
    stim_rect = stim_img.get_rect(center=screen.get_rect().center)
    screen.blit(stim_img, stim_rect)

    try:
        overlay_path = GSS_Speed if goal == 'S' else GSS_Accuracy
        goal_img = pygame.image.load(str(overlay_path)).convert_alpha()
        gw, gh = goal_img.get_size()
        goal_img = pygame.transform.smoothscale(goal_img, (max(1, gw//2), max(1, gh//2)))
        goal_rect = goal_img.get_rect()
        goal_rect.topright = (screen.get_width(), 0)
        screen.blit(goal_img, goal_rect)
    except Exception as e:
        logger.error(f"[test:{goal}] Failed to load goal cue: {overlay_path} | {e}")
    pygame.display.flip()


def _run_interval_block(screen: pygame.Surface, block_name: str, goal: str, n_intervals: int) -> pygame.Surface:
    """Core runner: duration-limited intervals, no feedback screen in tests."""
    event_handler = EventHandler()
    block_started = False

    for _ in range(int(n_intervals)):
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        # seed first stimulus
        prev_color: str | None = None
        pairs = list(WORD_COLOR_STIMULI.keys())
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]

        _show_center_with_goal(screen, stim_path, goal)
        if not block_started:
            cfg._start_time = datetime.datetime.now().isoformat()
            block_started = True
        _flush_input()
        stim_t0 = pygame.time.get_ticks()
        cfg.joy_response = None
        cfg.key_response = None

        while pygame.time.get_ticks() - interval_t0 < duration:
            state = event_handler.poll()
            if state.quit:
                pygame.quit()
                raise SystemExit
            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _show_center_with_goal(screen, stim_path, goal)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                correct_dir = cfg.expected_dir_for_color(color)
                result = "correct" if selected_dir == correct_dir else "incorrect"
                rt = pygame.time.get_ticks() - stim_t0

                update_save(
                    block_name,
                    "test",
                    f"{word}_in_{color}",
                    correct_dir,
                    "",
                    correct_dir,
                    selected_dir or "",
                    result,
                    int(rt),
                    str(stim_path),
                )

                # next stimulus (avoid same color)
                prev_color = color
                choices = [p for p in pairs if p[1] != prev_color] if prev_color else pairs
                word, color = random.choice(choices)
                stim_path = WORD_COLOR_STIMULI[(word, color)]
                _show_center_with_goal(screen, stim_path, goal)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()
                cfg.joy_response = None
                cfg.key_response = None

            pygame.time.delay(1)

    finalize_block_end_time()
    return screen


def speed_test(screen: pygame.Surface) -> pygame.Surface:
    return _run_interval_block(screen, "speed_test", 'S', int(getattr(cfg, 'SPEED_TEST_COUNT', 0)))


def accuracy_test(screen: pygame.Surface) -> pygame.Surface:
    return _run_interval_block(screen, "accuracy_test", 'A', int(getattr(cfg, 'ACCURACY_TEST_COUNT', 0)))


def _build_varying_schedule() -> list[str]:
    n_s = int(getattr(cfg, 'VARYING_TEST_SPEED_COUNT', 0))
    n_a = int(getattr(cfg, 'VARYING_TEST_ACCURACY_COUNT', 0))
    sched = ['S'] * n_s + ['A'] * n_a
    random.shuffle(sched)
    return sched


def varying_test_1(screen: pygame.Surface) -> pygame.Surface:
    # Each varying_test_* runs (S+A) intervals as per requirement.
    schedule = _build_varying_schedule()
    event_handler = EventHandler()
    block_started = False

    for goal in schedule:
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        prev_color: str | None = None
        pairs = list(WORD_COLOR_STIMULI.keys())
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]
        _show_center_with_goal(screen, stim_path, goal)
        if not block_started:
            cfg._start_time = datetime.datetime.now().isoformat()
            block_started = True
        _flush_input()
        stim_t0 = pygame.time.get_ticks()
        cfg.joy_response = None
        cfg.key_response = None

        while pygame.time.get_ticks() - interval_t0 < duration:
            state = event_handler.poll()
            if state.quit:
                pygame.quit()
                raise SystemExit
            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _show_center_with_goal(screen, stim_path, goal)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                correct_dir = cfg.expected_dir_for_color(color)
                result = "correct" if selected_dir == correct_dir else "incorrect"
                rt = pygame.time.get_ticks() - stim_t0

                update_save(
                    "varying_test_1",
                    "test",
                    f"goal={'speed' if goal=='S' else 'accuracy'}; {word}_in_{color}",
                    correct_dir,
                    "",
                    correct_dir,
                    selected_dir or "",
                    result,
                    int(rt),
                    str(stim_path),
                )

                prev_color = color
                choices = [p for p in pairs if p[1] != prev_color] if prev_color else pairs
                word, color = random.choice(choices)
                stim_path = WORD_COLOR_STIMULI[(word, color)]
                _show_center_with_goal(screen, stim_path, goal)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()
                cfg.joy_response = None
                cfg.key_response = None

            pygame.time.delay(1)

    finalize_block_end_time()
    return screen


def varying_test_2(screen: pygame.Surface) -> pygame.Surface:
    schedule = _build_varying_schedule()
    event_handler = EventHandler()
    block_started = False

    for goal in schedule:
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        prev_color: str | None = None
        pairs = list(WORD_COLOR_STIMULI.keys())
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]
        _show_center_with_goal(screen, stim_path, goal)
        if not block_started:
            cfg._start_time = datetime.datetime.now().isoformat()
            block_started = True
        _flush_input()
        stim_t0 = pygame.time.get_ticks()
        cfg.joy_response = None
        cfg.key_response = None

        while pygame.time.get_ticks() - interval_t0 < duration:
            state = event_handler.poll()
            if state.quit:
                pygame.quit()
                raise SystemExit
            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _show_center_with_goal(screen, stim_path, goal)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                correct_dir = cfg.expected_dir_for_color(color)
                result = "correct" if selected_dir == correct_dir else "incorrect"
                rt = pygame.time.get_ticks() - stim_t0

                update_save(
                    "varying_test_2",
                    "test",
                    f"goal={'speed' if goal=='S' else 'accuracy'}; {word}_in_{color}",
                    correct_dir,
                    "",
                    correct_dir,
                    selected_dir or "",
                    result,
                    int(rt),
                    str(stim_path),
                )

                prev_color = color
                choices = [p for p in pairs if p[1] != prev_color] if prev_color else pairs
                word, color = random.choice(choices)
                stim_path = WORD_COLOR_STIMULI[(word, color)]
                _show_center_with_goal(screen, stim_path, goal)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()
                cfg.joy_response = None
                cfg.key_response = None

            pygame.time.delay(1)

    finalize_block_end_time()
    return screen



def run_test(screen: pygame.Surface) -> pygame.Surface:
    """Run 4 test blocks in the order specified by cfg.task_sequence.

    Mapping: S -> speed_test, A -> accuracy_test, V -> varying_test_1 / varying_test_2 (in order).
    """
    if not cfg.task_sequence:
        sequence = ("S","A","V","V")
    else:
        sequence = cfg.task_sequence

    v_count = 0
    for code in sequence:
        if code == 'S':
            _show_block_intro(screen, 'speed')
            screen = speed_test(screen)
        elif code == 'A':
            _show_block_intro(screen, 'accuracy')
            screen = accuracy_test(screen)
        elif code == 'V':
            v_count += 1
            _show_block_intro(screen, 'varying')
            if v_count == 1:
                screen = varying_test_1(screen)
            else:
                screen = varying_test_2(screen)
        else:
            logger.warning(f"Unknown code in task_sequence: {code}")
    return screen
def _show_block_intro(screen: pygame.Surface, label: str) -> None:
    """Show a short intro page before each test block.
    - Background: BLACK_RGB
    - Text color: COCO_RGB
    - Content: task sequence + current block label (speed/accuracy/varying)
    """
    screen.fill(cfg.BLACK_RGB)
    try:
        font_title = pygame.font.SysFont(None, cfg.FONT_LARGE)
        font_body = pygame.font.SysFont(None, cfg.FONT_SMALL)
    except Exception:
        font_title = pygame.font.Font(None, cfg.FONT_LARGE)
        font_body = pygame.font.Font(None, cfg.FONT_SMALL)

    seq = cfg.task_sequence if cfg.task_sequence else ("S", "A", "V", "V")
    seq_text = "Task sequence: " + " ".join(seq)
    title_text = f"Current block: {label}"

    title_surf = font_title.render(title_text, True, cfg.COCO_RGB)
    seq_surf = font_body.render(seq_text, True, cfg.COCO_RGB)

    center = screen.get_rect().center
    title_rect = title_surf.get_rect(center=(center[0], center[1]-20))
    seq_rect = seq_surf.get_rect(center=(center[0], center[1]+30))

    screen.blit(title_surf, title_rect)
    screen.blit(seq_surf, seq_rect)
    pygame.display.flip()
    pygame.time.delay(int(getattr(cfg, 'FB_DURATION', 1000)))
    pygame.event.clear()