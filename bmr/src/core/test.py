"""Experimental block execution for the target mental-rotation task."""

from __future__ import annotations

import random
from pathlib import Path

import pygame

import utils.config as cfg
from ui.pygame_render import place_image, place_mapping_background, toggle_full_screen
from utils.event_handler import EventHandler
from utils.logger import get_logger
from utils.paths import FIXATION_CROSS_IMAGE
from utils.saves import format_time, update_save
from utils.stimuli_conditions import get_conditions


logger = get_logger("./src/core/test")


def _flush_input() -> None:
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def _draw_fixation_cross(screen: pygame.Surface) -> None:
    if FIXATION_CROSS_IMAGE.exists():
        place_image(screen, FIXATION_CROSS_IMAGE)
    else:
        screen.fill(cfg.BLACK_RGB)
    pygame.display.flip()


def _draw_response_hint(screen: pygame.Surface) -> None:
    w, h = screen.get_size()
    font = pygame.font.SysFont(None, 48)

    left_key = "D"
    right_key = "K"
    if cfg.MAPPING == 1:
        left_label = "normal"
        right_label = "mirrored"
    else:
        left_label = "mirrored"
        right_label = "normal"

    text_d = font.render(left_key, True, cfg.BLACK_RGB)
    text_d_label = font.render(left_label, True, cfg.BLACK_RGB)
    text_k = font.render(right_key, True, cfg.BLACK_RGB)
    text_k_label = font.render(right_label, True, cfg.BLACK_RGB)

    screen.blit(text_d, (w // 2.8 - text_d.get_width() // 2, h // 2 + 150))
    screen.blit(text_d_label, (w // 2.8 - text_d_label.get_width() // 2, h // 2 + 190))
    screen.blit(text_k, (int(1.8 * w // 2.8) - text_k.get_width() // 2, h // 2 + 150))
    screen.blit(text_k_label, (int(1.8 * w // 2.8) - text_k_label.get_width() // 2, h // 2 + 190))


def run_experimental_block(
    screen: pygame.Surface,
    event_handler: EventHandler,
    phase_label: str,
    block_name: str,
    stimuli_root: Path,
    show_trial_feedback: bool = False,
    break_duration_ms: int = 0,
) -> tuple[pygame.Surface, float]:
    """Run one block and return `(screen, accuracy_percent)`.

    `phase_label` must match `utils.stimuli_conditions.get_conditions`.
    """
    version = cfg.MAPPING if cfg.MAPPING in (1, 2) else 1
    conditions = get_conditions(phase_label, version, script_dir=stimuli_root)
    random.shuffle(conditions)

    correct_flags: list[bool] = []
    pending_rows: list[dict[str, object]] = []
    block_start_time = format_time()

    block_map = {
        "practice": "p1",
        "experimental_block_1": "b1",
        "experimental_block_2": "b2",
        "experimental_block_3": "b3",
        "experimental_block_4": "b4",
    }
    block_short = block_map.get(block_name, block_name)
    block_type = "practice" if block_short == "p1" else "experimental"

    for idx, cond in enumerate(conditions, start=1):
        stim_path = Path(cond["stimuli_path"])

        _draw_fixation_cross(screen)
        pygame.time.delay(cfg.FIXATION_CROSS)

        place_mapping_background(screen)
        place_image(
            screen,
            stim_path,
            center=(screen.get_width() / 2, screen.get_height() / 2),
            resize=(200, 200),
            overlay=True,
        )
        _draw_response_hint(screen)
        pygame.display.flip()

        _flush_input()
        t0 = pygame.time.get_ticks()

        selected_option: int | None = None
        key_response: str | None = None
        joy_response: str | None = None
        reaction_time = cfg.MAX_RESPONSE_TIME
        result = "timeout"

        while pygame.time.get_ticks() - t0 < cfg.MAX_RESPONSE_TIME:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                place_mapping_background(screen)
                place_image(
                    screen,
                    stim_path,
                    center=(screen.get_width() / 2, screen.get_height() / 2),
                    resize=(200, 200),
                    overlay=True,
                )
                _draw_response_hint(screen)
                pygame.display.flip()
                _flush_input()
                continue

            elapsed = pygame.time.get_ticks() - t0
            if state.option_1:
                selected_option = 1
                key_response = cfg.key_for_option(1)
                joy_response = cfg.joy_for_key(key_response)
                reaction_time = elapsed
                break

            if state.option_2:
                selected_option = 2
                key_response = cfg.key_for_option(2)
                joy_response = cfg.joy_for_key(key_response)
                reaction_time = elapsed
                break

            pygame.time.delay(1)

        if selected_option is not None:
            result = "correct" if key_response == cond["key_correct"] else "incorrect"

        correct_val = 1 if result == "correct" else 0
        correct_flags.append(result == "correct")

        pending_rows.append(
            {
                "condition": cond["condition"],
                "key_correct": cond["key_correct"],
                "key_response": key_response,
                "joy_correct": cfg.joy_for_key(cond["key_correct"]),
                "joy_response": joy_response,
                "correct": correct_val,
                "reaction_time": reaction_time,
            }
        )

        logger.info(
            "TRIAL_RESULT | block=%s | item=%d | stim=%s | result=%s | rt_ms=%d",
            block_name,
            idx,
            stim_path.name,
            result,
            reaction_time,
        )

        if show_trial_feedback:
            from ui.pygame_render import show_feedback

            show_feedback(screen, result)
            pygame.display.flip()
            pygame.time.delay(cfg.FB_DURATION)

        screen.fill(cfg.BLACK_RGB)
        pygame.display.flip()
        pygame.time.delay(cfg.ISI_TIME)
        _flush_input()

    block_end_time = format_time()
    global_start_time = format_time(cfg.START_TIME)

    for row in pending_rows:
        update_save(
            block=block_short,
            block_type=block_type,
            condition=row["condition"],
            key_correct=row["key_correct"],
            key_response=row["key_response"],
            joy_correct=row["joy_correct"],
            joy_response=row["joy_response"],
            correct=row["correct"],
            reaction_time=row["reaction_time"],
            start_time=block_start_time,
            end_time=block_end_time,
            gloabl_start_time=global_start_time,
        )

    accuracy = 100.0 * sum(correct_flags) / len(correct_flags) if correct_flags else 0.0
    return screen, accuracy
