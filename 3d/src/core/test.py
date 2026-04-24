# ./src/core/test.py
"""
Experimental blocks for the imported 3D mental‑rotation task (template format).

This overwrites the template's test logic to reproduce the
`imported_project` behavior while keeping the surrounding template API
unchanged. It can run one phase at a time (block1/test1 or block2/test2)
or both phases when called with any other block name.

- Demo mode uses short condition files.
- Full mode uses full condition files.

`version` depends on mapping (odd → 1, even → 2). No feedback is shown
in test phases. Results are saved through the template's `update_save`.
"""



from __future__ import annotations
from pathlib import Path
import pygame
import random
import datetime
import csv

import utils.config as cfg
from utils.logger import get_logger
from utils.event_handler import EventHandler
from ui.pygame_render import (
    toggle_full_screen,
    place_image,
)
from utils.saves import update_save


logger = get_logger("./src/core/test")

def _flush_input() -> None:
    """
    Flush all pending pygame input events.

    :return: None
    """
    pygame.event.clear()
    pygame.time.delay(1)
    pygame.event.clear()


def run_test(
    screen: pygame.Surface,
    block: str,
    stimuli: list[Path],
    event_handler: EventHandler,
) -> pygame.Surface:
    """
    Run one or both experimental phases using CSV conditions.

    - demo mode: test1_short_{version}.csv / test2_short_{version}.csv
    - full mode: test1_{version}.csv / test2_{version}.csv

    The `stimuli` parameter is ignored but kept for API compatibility.
    """
    version = 1 if (cfg.MAPPING in (None, 1)) else 2

    project_root = Path(__file__).resolve().parents[2]
    resources_dir = project_root / "resources"
    cond_dir = resources_dir / "stimuli" / "conditions"

    condition_suffix = f"short_{version}" if cfg.MODE == "demo" else str(version)
    all_phases = {
        "block1": cond_dir / f"test1_{condition_suffix}.csv",
        "block2": cond_dir / f"test2_{condition_suffix}.csv",
    }
    phases = [(block, all_phases[block])] if block in all_phases else list(all_phases.items())

    MAX_RESP_MS = 7500
    FIX_MS = 250
    ISI_MS = 500

    sw, sh = screen.get_size()
    target_w, target_h = int(sw * 0.6), int(sh * 0.6)

    for block_name, csv_path in phases:
        # Load conditions
        trials: list[dict] = []
        try:
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rel = row.get("stimuli_path", "")
                    if rel.startswith("./"):
                        rel = rel[2:]
                    stim_abs = resources_dir / rel
                    trials.append({
                        "condition": row.get("condition", ""),
                        "stimuli_path": stim_abs,
                        "key_correct": row.get("key_correct", ""),
                    })
        except Exception as e:
            logger.error(f"Failed to load test conditions {csv_path.name}: {e}")
            continue

        random.shuffle(trials)

        for trial in trials:
            stim_path: Path = Path(trial["stimuli_path"])  # composite image

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

            # Stimulus
            place_image(screen, stim_path, center=(sw / 2, sh / 2), resize=(target_w, target_h))

            pygame.display.flip()
            _flush_input()

            # Response
            t0 = pygame.time.get_ticks()
            option_selected: int | None = None
            reaction_time = MAX_RESP_MS

            while True:
                state = event_handler.poll()

                if state.quit:
                    pygame.quit()
                    raise SystemExit

                if state.toggle_full_screen:
                    pygame.event.clear()
                    screen = toggle_full_screen(screen)
                    pygame.event.clear()
                    place_image(screen, stim_path, center=(sw / 2, sh / 2), resize=(target_w, target_h))
                    pygame.display.flip()
                    _flush_input()

                elapsed = pygame.time.get_ticks() - t0

                if state.option_1:
                    option_selected = 1
                    reaction_time = elapsed
                    break

                if state.option_2:
                    option_selected = 2
                    reaction_time = elapsed
                    break

                if elapsed >= MAX_RESP_MS:
                    break

                pygame.time.delay(1)

            _flush_input()

            # Evaluate
            key_correct = (trial["key_correct"] or "").lower()
            if option_selected is None:
                correct_flag: int | None = None
                result = "timeout"
            else:
                chosen_key = "d" if option_selected == 1 else "k"
                correct_flag = 1 if chosen_key == key_correct else 0
                result = "correct" if correct_flag == 1 else "incorrect"

            logger.info(
                "TRIAL_RESULT | block=%s | stim=%s | response=%s | result=%s | reaction_time_ms=%d",
                block_name,
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
                block_name=block_name,
                trial_type="experimental",
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

    return screen
