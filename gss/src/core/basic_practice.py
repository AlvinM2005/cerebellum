"""
Color mapping practice using joystick with JOY_MODE == 4.

Plays a randomized sequence of X_[COLOR].png stimuli and collects joystick
responses with no fixed response window. Feedback is shown after each trial.
The sequence contains cfg.COLOR_PRACTICE_COUNT items and avoids consecutive
repetition of the same color.
"""

from __future__ import annotations

import datetime
import random
from pathlib import Path

import pygame

import utils.config as cfg
from utils.logger import get_logger
from utils.paths import X_COLOR_STIMULI, GSS_Speed, GSS_Accuracy
from utils.event_handler import EventHandler
from ui.pygame_render import toggle_full_screen, show_feedback
from utils.saves import update_save, finalize_block_end_time


logger = get_logger("./src/core/practice")


def _flush_input() -> None:
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _show_isi(screen: pygame.Surface) -> None:
    """Render a black inter-stimulus interval and swallow stray input."""
    screen.fill(cfg.BLACK_RGB)
    pygame.display.flip()
    _flush_input()
    pygame.time.delay(int(cfg.ISI_DURATION))
    _flush_input()


def _show_goal_image(screen: pygame.Surface, goal: str) -> None:
    """Show the goal image at original size, centered, before an interval begins."""
    goal_path = GSS_Speed if goal == "S" else GSS_Accuracy
    screen.fill(cfg.BLACK_RGB)
    try:
        goal_img = pygame.image.load(str(goal_path)).convert_alpha()
    except Exception as e:
        logger.error(f"[goal_image] Failed to load goal image: {goal_path} | {e}")
        return
    goal_rect = goal_img.get_rect(center=screen.get_rect().center)
    screen.blit(goal_img, goal_rect)
    pygame.display.flip()
    _flush_input()
    pygame.time.delay(int(cfg.DISPLAY_GOAL_DURATION))
    _flush_input()


def _show_centered_image(screen: pygame.Surface, img_path: Path) -> None:
    screen.fill(cfg.BLACK_RGB)
    try:
        img = pygame.image.load(str(img_path)).convert_alpha()
    except Exception as e:
        logger.error(f"[practice] Failed to load image: {img_path} | {e}")
        return
    rect = img.get_rect(center=screen.get_rect().center)
    screen.blit(img, rect)
    pygame.display.flip()

def _build_sequence(n: int) -> list[tuple[str, Path]]:
    colors = list(X_COLOR_STIMULI.keys())  # ['BLUE','GREEN','RED','YELLOW']
    seq: list[tuple[str, Path]] = []
    prev: str | None = None
    for _ in range(n):
        choices = [c for c in colors if c != prev] if prev else colors
        color = random.choice(choices)
        seq.append((color, X_COLOR_STIMULI[color]))
        prev = color
    return seq


def color_practice(screen: pygame.Surface) -> pygame.Surface:
    """
    Run color practice: present X_[COLOR].png, wait for joystick response,
    judge correctness by mapping color->direction, show feedback, and save.
    """
    event_handler = EventHandler()

    count = int(cfg.COLOR_PRACTICE_COUNT)
    sequence = _build_sequence(count)
    block_started = False

    for trial_index, (color, stim_path) in enumerate(sequence, start=1):
        if trial_index == 1:
            _show_isi(screen)

        _show_centered_image(screen, stim_path)
        pygame.display.flip()
        if not block_started:
            cfg._start_time = datetime.datetime.now().isoformat()
            block_started = True
        _flush_input()

        t0 = pygame.time.get_ticks()

        cfg.joy_response = None
        cfg.key_response = None

        result = "timeout"
        reaction_time = 0
        selected_dir: str | None = None
        correct_dir = cfg.expected_dir_for_color(color)

        while True:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _show_centered_image(screen, stim_path)
                pygame.display.flip()
                _flush_input()

            elapsed = pygame.time.get_ticks() - t0

            # Accept first joystick direction
            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                result = "correct" if selected_dir == correct_dir else "incorrect"
                reaction_time = elapsed
                break

            pygame.time.delay(1)

        _flush_input()

        logger.info(
            "TRIAL_RESULT | block=color_practice | stim=%s | color=%s | joy=%s | correct_dir=%s | result=%s | rt_ms=%d",
            stim_path.name,
            color,
            selected_dir if selected_dir is not None else "None",
            correct_dir,
            result,
            reaction_time,
        )

        # Save record (keyboard fields left empty; normalization fills NA)
        update_save(
            "color_practice",
            "practice",
            f"X_in_{color}",
            correct_dir,
            "",
            correct_dir,
            selected_dir or "",
            result,
            int(reaction_time),
            str(stim_path),
        )

        # Feedback
        show_feedback(screen, result)
        pygame.display.flip()
        pygame.time.delay(cfg.FB_DURATION)

        if trial_index < len(sequence):
            _show_isi(screen)
        else:
            screen.fill(cfg.BLACK_RGB)
            pygame.display.flip()
            _flush_input()
    
    finalize_block_end_time()
    return screen

from utils.paths import WORD_COLOR_STIMULI


def _build_stroop_sequence(n: int) -> list[tuple[str, str, Path]]:
    pairs = list(WORD_COLOR_STIMULI.keys())  # list of (WORD, COLOR)
    seq: list[tuple[str, str, Path]] = []
    prev_pair: tuple[str, str] | None = None
    for _ in range(n):
        choices = [
            p for p in pairs
            if p[0] != prev_pair[0] and p[1] != prev_pair[1]
        ] if prev_pair else pairs
        word, color = random.choice(choices)
        seq.append((word, color, WORD_COLOR_STIMULI[(word, color)]))
        prev_pair = (word, color)
    return seq


def stroop_practice(screen: pygame.Surface) -> pygame.Surface:
    """
    Stroop practice using WORD_in_COLOR stimuli.
    Correctness is judged by ink color (the part after '_').
    """
    event_handler = EventHandler()

    count = int(cfg.STROOP_PRACTICE_COUNT)
    sequence = _build_stroop_sequence(count)
    block_started = False

    for trial_index, (word, color, stim_path) in enumerate(sequence, start=1):
        if trial_index == 1:
            _show_isi(screen)

        _show_centered_image(screen, stim_path)
        pygame.display.flip()
        if not block_started:
            cfg._start_time = datetime.datetime.now().isoformat()
            block_started = True
        _flush_input()

        t0 = pygame.time.get_ticks()
        cfg.joy_response = None
        cfg.key_response = None

        result = "timeout"
        reaction_time = 0
        selected_dir: str | None = None
        correct_dir = cfg.expected_dir_for_color(color)

        while True:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                _show_centered_image(screen, stim_path)
                pygame.display.flip()
                _flush_input()

            elapsed = pygame.time.get_ticks() - t0

            if cfg.joy_response is not None:
                selected_dir = cfg.joy_response
                result = "correct" if selected_dir == correct_dir else "incorrect"
                reaction_time = elapsed
                break

            pygame.time.delay(1)

        _flush_input()

        logger.info(
            "TRIAL_RESULT | block=stroop_practice | stim=%s | word=%s | color=%s | joy=%s | correct_dir=%s | result=%s | rt_ms=%d",
            stim_path.name,
            word,
            color,
            selected_dir if selected_dir is not None else "None",
            correct_dir,
            result,
            reaction_time,
        )

        update_save(
            "stroop_practice",
            "practice",
            f"{word}_in_{color}",
            correct_dir,
            "",
            correct_dir,
            selected_dir or "",
            result,
            int(reaction_time),
            str(stim_path),
        )

        show_feedback(screen, result)
        pygame.display.flip()
        pygame.time.delay(cfg.FB_DURATION)

        if trial_index < len(sequence):
            _show_isi(screen)
        else:
            screen.fill(cfg.BLACK_RGB)
            pygame.display.flip()
            _flush_input()

    
    finalize_block_end_time()
    return screen

def _show_interval_feedback(screen: pygame.Surface, accuracy: float, n_trials: int) -> None:
    screen.fill(cfg.BLACK_RGB)
    font = pygame.font.SysFont(None, cfg.FONT_LARGE)
    font_small = pygame.font.SysFont(None, cfg.FONT_SMALL)
    acc_text = f"Accuracy: {accuracy:.1f}%"
    cnt_text = f"Trials: {n_trials}"
    acc_surf = font.render(acc_text, True, cfg.COCO_RGB)
    cnt_surf = font_small.render(cnt_text, True, cfg.COCO_RGB)
    center = screen.get_rect().center
    acc_rect = acc_surf.get_rect(center=(center[0], center[1]-20))
    cnt_rect = cnt_surf.get_rect(center=(center[0], center[1]+30))
    screen.blit(acc_surf, acc_rect)
    screen.blit(cnt_surf, cnt_rect)
    pygame.display.flip()


def interval_practice(screen: pygame.Surface) -> pygame.Surface:
    """Interval-based practice: as many trials as possible within duration."""
    event_handler = EventHandler()

    # Block start time on first stimulus flip
    block_started = False

    for interval_idx in range(int(cfg.INTERVAL_PRACTICE_COUNT)):
        duration = random.randint(int(cfg.INTERVAL_MIN), int(cfg.INTERVAL_MAX))
        interval_t0 = pygame.time.get_ticks()
        correct_cnt = 0
        total_cnt = 0

        # seed first stimulus
        prev_pair: tuple[str, str] | None = None
        # pick first pair
        from utils.paths import WORD_COLOR_STIMULI
        pairs = list(WORD_COLOR_STIMULI.keys())
        word, color = random.choice(pairs)
        stim_path = WORD_COLOR_STIMULI[(word, color)]
        _show_isi(screen)
        _show_centered_image(screen, stim_path)
        pygame.display.flip()
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
                _show_centered_image(screen, stim_path)
                pygame.display.flip()
                _flush_input()

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
                    "interval_practice",
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

                # next stimulus (avoid same word and same color)
                prev_pair = (word, color)
                choices = [
                    p for p in pairs
                    if p[0] != prev_pair[0] and p[1] != prev_pair[1]
                ] if prev_pair else pairs
                word, color = random.choice(choices)
                stim_path = WORD_COLOR_STIMULI[(word, color)]
                _show_isi(screen)
                _show_centered_image(screen, stim_path)
                pygame.display.flip()
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
