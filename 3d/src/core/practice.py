# ./src/core/test.py
"""
Practice block for the imported 3D mental‑rotation task (template format).

This overwrites the template's demo/practice logic to reproduce the
`imported_project` behavior while keeping the surrounding template API
unchanged. Trials are driven by CSV condition files from
`imported_project/stimuli/conditions/demo_{version}.csv`, where
`version` depends on participant mapping (odd → 1, even → 2) as in the
original project.

Key behavior replicated:
- Fixation cross (250 ms), then stimulus image centered.
- Response window up to 7500 ms for keyboard `d`/`k` or joystick left/right.
- Mapping 1: `d` = Same, `k` = Different. Mapping 2 reverses the mapping.
- Immediate per‑trial save using the template's `update_save` schema.
- Practice shows feedback for 1000 ms; test block suppresses feedback.
"""



from __future__ import annotations
from pathlib import Path
import pygame
import random
import datetime
import csv
import os

import utils.config as cfg
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import (
    toggle_full_screen,
    place_image,
    show_feedback,
    _play_beep,
)
from utils.saves import update_save


logger = get_logger("./src/core/practice")

def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def run_practice(
    screen: pygame.Surface,
    block: str,
    stimuli: list[Path],
    event_handler: EventHandler,
) -> pygame.Surface:
    """
    Run the demo/practice block using `imported_project` CSV conditions.

    - Resolves conditions from `imported_project/stimuli/conditions/demo_{version}.csv`.
    - Draws fixation, then a single composite stimulus image centered.
    - Displays D/K labels according to mapping; records keyboard or joystick.
    - Shows feedback for 1000 ms.

    The `stimuli` parameter is ignored but kept for API compatibility.

    :return: Possibly updated display surface
    """
    # Map template mapping → imported VERSION (1 or 2)
    version = 1 if (cfg.MAPPING in (None, 1)) else 2

    # Locate CSV under ./resources/stimuli
    project_root = Path(__file__).resolve().parents[2]
    resources_dir = project_root / "resources"
    cond_dir = resources_dir / "stimuli" / "conditions"
    cond_csv = cond_dir / f"demo_{version}.csv"

    # Load conditions
    trials: list[dict] = []
    try:
        with cond_csv.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel = row.get("stimuli_path", "")
                if rel.startswith("./"):
                    rel = rel[2:]
                # Resolve relative path like "./stimuli/images/..." under resources/
                stim_abs = resources_dir / rel
                trials.append({
                    "condition": row.get("condition", ""),
                    "stimuli_path": stim_abs,
                    "key_correct": row.get("key_correct", "")
                })
    except Exception as e:
        logger.error(f"Failed to load practice conditions: {e}")
        return screen

    random.shuffle(trials)

    # Constants from imported_project
    MAX_RESP_MS = 7500
    FIX_MS = 250
    ISI_MS = 500
    FB_MS = 1000

    for trial in trials:
        stim_path: Path = Path(trial["stimuli_path"])  # composite image (left+right)

        # ISI
        screen.fill(cfg.BLACK_RGB)
        pygame.display.flip()
        _flush_input()
        pygame.time.delay(ISI_MS)

        # Fixation (black background, white cross)
        screen.fill(cfg.BLACK_RGB)
        cx, cy = screen.get_rect().center
        pygame.draw.line(screen, cfg.WHITE_RGB, (cx - 40, cy), (cx + 40, cy), 6)
        pygame.draw.line(screen, cfg.WHITE_RGB, (cx, cy - 40), (cx, cy + 40), 6)
        pygame.display.flip()
        _flush_input()
        pygame.time.delay(FIX_MS)

        # Stimulus (centered, scaled to reasonable size)
        # Use ~60% of screen width, preserving imported behavior of a single composite image.
        sw, sh = screen.get_size()
        target_w, target_h = int(sw * 0.6), int(sh * 0.6)
        place_image(screen, stim_path, center=(sw / 2, sh / 2), resize=(target_w, target_h))

        pygame.display.flip()
        _flush_input()

        # Response loop
        t0 = pygame.time.get_ticks()
        option_selected: int | None = None  # 1 = left/D, 2 = right/K
        reaction_time = MAX_RESP_MS
        result = "timeout"

        while True:
            state = event_handler.poll()

            if state.quit:
                pygame.quit()
                raise SystemExit

            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
                # redraw stimulus after toggle
                place_image(screen, stim_path, center=(sw / 2, sh / 2), resize=(target_w, target_h))
                pygame.display.flip()
                _flush_input()

            elapsed = pygame.time.get_ticks() - t0

            if state.option_1:
                _play_beep()
                option_selected = 1
                reaction_time = elapsed
                break

            if state.option_2:
                _play_beep()
                option_selected = 2
                reaction_time = elapsed
                break

            if elapsed >= MAX_RESP_MS:
                break

            pygame.time.delay(1)

        # Lock input immediately
        _flush_input()

        # Determine correctness vs CSV key
        key_correct = (trial["key_correct"] or "").lower()
        if option_selected is None:
            correct_flag: int | None = None
            result = "timeout"
        else:
            chosen_key = "d" if option_selected == 1 else "k"
            correct_flag = 1 if chosen_key == key_correct else 0
            result = "correct" if correct_flag == 1 else "incorrect"

        # Log result
        logger.info(
            "TRIAL_RESULT | block=%s | stim=%s | response=%s | result=%s | reaction_time_ms=%d",
            block,
            Path(stim_path).name,
            ("d" if option_selected == 1 else ("k" if option_selected == 2 else "None")),
            result,
            reaction_time,
        )

        # Save
        cfg._end_time = datetime.datetime.now().isoformat()
        key_response = "d" if option_selected == 1 else ("k" if option_selected == 2 else "")
        joy_response = "left" if option_selected == 1 else ("right" if option_selected == 2 else "")
        joy_correct = "left" if key_correct == "d" else ("right" if key_correct == "k" else "")

        update_save(
            block_name="practice",
            trial_type="practice",
            condition=trial["condition"],
            key_correct=key_correct,
            key_response=key_response,
            joy_correct=joy_correct,
            joy_response=joy_response,
            correct=correct_flag,
            reaction_time=reaction_time if option_selected is not None else None,
            stimulus_path=str(stim_path),
        )
        cfg._start_time = datetime.datetime.now().isoformat()

        # Feedback (overlay on the stimulus)
        show_feedback(screen, result)
        pygame.display.flip()
        pygame.time.delay(FB_MS)
        _flush_input()

    return screen
