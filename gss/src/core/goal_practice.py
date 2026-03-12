"""
Goal practice blocks (Speed / Accuracy / Varying): interval-based trials with corresponding goal cue overlay.

Copies interval practice logic and overlays GSS_Speed at the top-right corner
while presenting each stimulus centered without resizing.
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
from core.basic_practice import _show_interval_feedback


logger = get_logger("./src/core/goal_practice")


def _flush_input() -> None:
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _show_center_with_goal(screen: pygame.Surface, stim_path: Path) -> None:
    """Draw the stimulus centered and GSS_Speed top-right, no resizing."""
    screen.fill(cfg.BLACK_RGB)
    # center stimulus
    try:
        stim_img = pygame.image.load(str(stim_path)).convert_alpha()
    except Exception as e:
        logger.error(f"[speed_practice] Failed to load stimulus: {stim_path} | {e}")
        return
    stim_rect = stim_img.get_rect(center=screen.get_rect().center)
    screen.blit(stim_img, stim_rect)

    # goal cue top-right (flush to top and right)
    # goal cue top-right (flush to top and right)
    try:
        goal_img = pygame.image.load(str(GSS_Speed)).convert_alpha()
        gw, gh = goal_img.get_size()
        goal_img = pygame.transform.smoothscale(goal_img, (max(1, gw//2), max(1, gh//2)))
        goal_rect = goal_img.get_rect()
        goal_rect.topright = (screen.get_width(), 0)
        screen.blit(goal_img, goal_rect)
    except Exception as e:
        logger.error(f"[speed_practice] Failed to load goal cue: {GSS_Speed} | {e}")
    pygame.display.flip()


def speed_practice(screen: pygame.Surface) -> pygame.Surface:
    """Interval-based practice with Speed goal cue overlay."""
    event_handler = EventHandler()

    # Block start time on first stimulus flip
    block_started = False

    for interval_idx in range(int(getattr(cfg, "SPEED_PRACTICE_COUNT", cfg.INTERVAL_PRACTICE_COUNT))):
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        correct_cnt = 0
        total_cnt = 0

        # seed first stimulus
        prev_color: str | None = None
        pairs = list(WORD_COLOR_STIMULI.keys())  # (WORD, COLOR)
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]
        _show_center_with_goal(screen, stim_path)
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
                _show_center_with_goal(screen, stim_path)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                correct_dir = cfg.expected_dir_for_color(color)
                result = "correct" if selected_dir == correct_dir else "incorrect"
                rt = pygame.time.get_ticks() - stim_t0

                total_cnt += 1
                if result == "correct":
                    correct_cnt += 1

                # save
                update_save(
                    "speed_practice",
                    "practice",
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
                _show_center_with_goal(screen, stim_path)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()
                cfg.joy_response = None
                cfg.key_response = None

            pygame.time.delay(1)

        # interval feedback screen
        acc = (correct_cnt / total_cnt * 100.0) if total_cnt > 0 else 0.0
        _show_interval_feedback(screen, acc, total_cnt)
        pygame.time.delay(int(cfg.FB_SCREEN_DURATION))
        _flush_input()

    finalize_block_end_time()
    return screen





def _show_center_with_goal_accuracy(screen: pygame.Surface, stim_path: Path) -> None:
    """Draw the stimulus centered and GSS_Accuracy top-right, no resizing."""
    screen.fill(cfg.BLACK_RGB)
    # center stimulus
    try:
        stim_img = pygame.image.load(str(stim_path)).convert_alpha()
    except Exception as e:
        logger.error(f"[accuracy_practice] Failed to load stimulus: {stim_path} | {e}")
        return
    stim_rect = stim_img.get_rect(center=screen.get_rect().center)
    screen.blit(stim_img, stim_rect)

    # goal cue top-right (flush to top and right), scaled to half size
    try:
        goal_img = pygame.image.load(str(GSS_Accuracy)).convert_alpha()
        gw, gh = goal_img.get_size()
        goal_img = pygame.transform.smoothscale(goal_img, (max(1, gw//2), max(1, gh//2)))
        goal_rect = goal_img.get_rect()
        goal_rect.topright = (screen.get_width(), 0)
        screen.blit(goal_img, goal_rect)
    except Exception as e:
        logger.error(f"[accuracy_practice] Failed to load goal cue: {GSS_Accuracy} | {e}")
    pygame.display.flip()
def accuracy_practice(screen: pygame.Surface) -> pygame.Surface:
    """Interval-based practice with Accuracy goal cue overlay."""
    event_handler = EventHandler()
    block_started = False

    for interval_idx in range(int(getattr(cfg, "ACCURACY_PRACTICE_COUNT", cfg.INTERVAL_PRACTICE_COUNT))):
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        correct_cnt = 0
        total_cnt = 0

        # seed first stimulus
        prev_color: str | None = None
        pairs = list(WORD_COLOR_STIMULI.keys())
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]
        _show_center_with_goal_accuracy(screen, stim_path)
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
                _show_center_with_goal_accuracy(screen, stim_path)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                correct_dir = cfg.expected_dir_for_color(color)
                result = "correct" if selected_dir == correct_dir else "incorrect"
                rt = pygame.time.get_ticks() - stim_t0

                total_cnt += 1
                if result == "correct":
                    correct_cnt += 1

                update_save(
                    "accuracy_practice",
                    "practice",
                    f"{word}_in_{color}",
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
                _show_center_with_goal_accuracy(screen, stim_path)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()
                cfg.joy_response = None
                cfg.key_response = None

            pygame.time.delay(1)

        acc = (correct_cnt / total_cnt * 100.0) if total_cnt > 0 else 0.0
        _show_interval_feedback(screen, acc, total_cnt)
        pygame.time.delay(int(cfg.FB_SCREEN_DURATION))
        _flush_input()

    finalize_block_end_time()
    return screen

def varying_practice(screen: pygame.Surface) -> pygame.Surface:
    """Interval-based practice mixing Speed and Accuracy goals.

    The block contains cfg.VARYING_PRACTICE_SPEED_COUNT Speed intervals and
    cfg.VARYING_PRACTICE_ACCURACY_COUNT Accuracy intervals in randomized order.
    Each interval behaves like speed_practice/accuracy_practice: unlimited trials
    within a randomly sampled duration [cfg.INTERVAL_MIN, cfg.INTERVAL_MAX].
    """
    event_handler = EventHandler()

    # Build randomized schedule, e.g., ['S','A','S','A','A','A']
    n_s = int(getattr(cfg, "VARYING_PRACTICE_SPEED_COUNT", 0))
    n_a = int(getattr(cfg, "VARYING_PRACTICE_ACCURACY_COUNT", 0))
    schedule: list[str] = ["S"] * n_s + ["A"] * n_a
    random.shuffle(schedule)

    block_started = False

    for goal in schedule:
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        correct_cnt = 0
        total_cnt = 0

        # seed first stimulus
        prev_color: str | None = None
        pairs = list(WORD_COLOR_STIMULI.keys())  # (WORD, COLOR)
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]

        if goal == "S":
            _show_center_with_goal(screen, stim_path)
        else:
            _show_center_with_goal_accuracy(screen, stim_path)

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
                if goal == "S":
                    _show_center_with_goal(screen, stim_path)
                else:
                    _show_center_with_goal_accuracy(screen, stim_path)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                correct_dir = cfg.expected_dir_for_color(color)
                result = "correct" if selected_dir == correct_dir else "incorrect"
                rt = pygame.time.get_ticks() - stim_t0

                total_cnt += 1
                if result == "correct":
                    correct_cnt += 1

                # save
                goal_tag = "speed" if goal == "S" else "accuracy"
                update_save(
                    "varying_practice",
                    "practice",
                    f"goal={goal_tag}; {word}_in_{color}",
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
                if goal == "S":
                    _show_center_with_goal(screen, stim_path)
                else:
                    _show_center_with_goal_accuracy(screen, stim_path)
                _flush_input()
                stim_t0 = pygame.time.get_ticks()
                cfg.joy_response = None
                cfg.key_response = None

            pygame.time.delay(1)

        # interval feedback screen
        acc = (correct_cnt / total_cnt * 100.0) if total_cnt > 0 else 0.0
        _show_interval_feedback(screen, acc, total_cnt)
        pygame.time.delay(int(cfg.FB_SCREEN_DURATION))
        _flush_input()

    finalize_block_end_time()
    return screen

