# ./src/core/practice.py
"""
Practice block execution for the soccer prediction task.

Presents 12 pre-sequenced video trials (1 per player/condition/difficulty combo),
collects left/right responses, and displays feedback after each trial.
"""

from __future__ import annotations
import datetime
import pygame

import utils.config as cfg
import utils.paths as paths
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import toggle_full_screen, show_feedback
from ui.video import play_video, get_guide_overlay, show_frozen_frame
from core.saves import update_save

logger = get_logger("./src/core/practice")


def _flush_input() -> None:
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _show_fixation(screen: pygame.Surface) -> None:
    screen.fill(cfg.BLACK_RGB)
    w, h = screen.get_size()
    arm = 20
    pygame.draw.line(screen, cfg.COCO_RGB, (w // 2 - arm, h // 2), (w // 2 + arm, h // 2), 3)
    pygame.draw.line(screen, cfg.COCO_RGB, (w // 2, h // 2 - arm), (w // 2, h // 2 + arm), 3)
    pygame.display.flip()


def run_practice(
    screen: pygame.Surface,
    block_label: str,
    trials: list[dict],
    event_handler: EventHandler,
) -> tuple[pygame.Surface, str, str]:
    """
    Run all practice trials with per-trial feedback.

    Each trial:
        fixation → video → frozen frame + guide overlay → response → feedback → save

    :param screen: Active pygame display surface.
    :param block_label: Block identifier written to results CSV (e.g. 'p1').
    :param trials: Practice trial dicts from build_trials() filtered to phase='practice'.
    :param event_handler: Centralized input handler.
    :return: (screen, accuracy_pct_str, avg_rt_sec_str)
    """
    curr_trials = 0
    acc_counter = 0
    sum_rt = 0
    joystick_present = pygame.joystick.get_count() > 0
    accuracy_str = "0.00"

    for trial in trials:
        filename = f"{trial['video_name']}.mp4"
        video_path = paths.VIDEOS / filename
        stop_at = float(trial['interact_start']) + float(trial['secs_after_interact'])
        correct_direction = trial['condition']  # 'left' or 'right'

        # Fixation
        _show_fixation(screen)
        _flush_input()
        pygame.time.delay(cfg.FIXATION_CROSS)

        starting = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Play video — returns the last rendered frame
        last_frame = play_video(screen, video_path, stop_at)

        # Freeze on last frame with guide overlay for the full response window
        guide = get_guide_overlay(screen.get_size())
        show_frozen_frame(screen, last_frame, guide)
        _flush_input()

        # Response
        t0 = pygame.time.get_ticks()
        response: str | None = None
        correct = 0
        rt = cfg.MAX_RESPOND_TIME

        while True:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                guide = get_guide_overlay(screen.get_size())
                show_frozen_frame(screen, last_frame, guide)
                _flush_input()

            elapsed = pygame.time.get_ticks() - t0
            if elapsed >= cfg.MAX_RESPOND_TIME:
                rt = elapsed
                break

            if state.option_1:
                response = "left"
                correct = 1 if correct_direction == "left" else 0
                rt = elapsed
                break
            elif state.option_2:
                response = "right"
                correct = 1 if correct_direction == "right" else 0
                rt = elapsed
                break

        _flush_input()
        acc_counter += correct
        sum_rt += rt
        curr_trials += 1
        accuracy_str = f"{(acc_counter / curr_trials) * 100:.2f}" if curr_trials > 0 else "0.00"

        # Format response columns for save
        if joystick_present:
            key_corr, key_resp = "NA", "NA"
            joy_corr = correct_direction
            joy_resp = response if response else "NA"
        else:
            key_corr = "d" if correct_direction == "left" else "k"
            key_resp = ("d" if response == "left" else "k") if response else "NA"
            joy_corr, joy_resp = "NA", "NA"

        # Feedback
        show_feedback(screen, "timeout" if response is None else correct)
        pygame.display.flip()
        pygame.time.delay(cfg.FB_DURATION)
        _flush_input()

        update_save(
            block=block_label,
            type="practice",
            starttime=starting,
            endtime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            condition=trial['condition'],
            correct=correct,
            reaction_time=rt,
            key_corr=key_corr,
            key_resp=key_resp,
            joy_corr=joy_corr,
            joy_resp=joy_resp,
            accuracy=accuracy_str,
            pathname=filename,
            difficulty=trial["difficulty"],
        )

        logger.info(
            "PRACTICE | block=%s | video=%s | direction=%s | response=%s | correct=%s | rt=%d ms",
            block_label, trial['video_name'], correct_direction, response, correct, rt,
        )

    avg_rt_str = f"{(sum_rt / curr_trials) / 1000:.2f}" if curr_trials > 0 else "0.00"
    return screen, accuracy_str, avg_rt_str


