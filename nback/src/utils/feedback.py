# ./src/utils/feedback.py
from __future__ import annotations

"""
Feedback overlay renderer for n-back.

Public API:
    show_feedback(screen, status)

- status:
    "correct"   -> show feedback_correct.png at the designated position
    "incorrect" -> show feedback_incorrect.png at the designated position
    "timeout"   -> show "Too Slow" in cfg.YELLOW_RGB at the designated position

Design notes:
- Keeps the existing UI layout concept: an overlay near the lower-middle area.
- Does NOT manage timing/delay. The caller controls when to clear/hide it.
- Draws on top of the current screen contents and flips immediately.
"""

from pathlib import Path
import pygame

from utils import config as cfg

# ----------------------- Module-level cache -----------------------

_ICON_CACHE: dict[str, pygame.Surface] = {}
_FEEDBACK_DIR = cfg.RESOURCES_DIR / "feedback"
_OK_NAME = "feedback_correct.png"
_BAD_NAME = "feedback_incorrect.png"


def _load_icon(name: str) -> pygame.Surface:
    """
    Load an icon surface from resources/feedback with per-pixel alpha.
    Caches the loaded surface to avoid disk I/O on repeated calls.
    """
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]

    path = (_FEEDBACK_DIR / name)
    surf = pygame.image.load(str(path)).convert_alpha()
    _ICON_CACHE[name] = surf
    return surf


def _scale_to_feedback_size(surf: pygame.Surface) -> pygame.Surface:
    """
    Scale the icon to an appropriate on-screen size using:
      - FEEDBACK_ICON_RATIO (relative to min(screen_w, screen_h))
      - FEEDBACK_ICON_MAX_PX as an absolute cap
    Preserves aspect ratio.
    """
    sw, sh = surf.get_size()
    base = min(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
    target = int(base * cfg.FEEDBACK_ICON_RATIO)
    target = min(target, int(cfg.FEEDBACK_ICON_MAX_PX))
    target = max(1, target)

    # keep aspect ratio
    if sw >= sh:
        new_w = target
        new_h = max(1, int(sh * (target / sw)))
    else:
        new_h = target
        new_w = max(1, int(sw * (target / sh)))

    if (new_w, new_h) == (sw, sh):
        return surf
    return pygame.transform.smoothscale(surf, (new_w, new_h))


def _feedback_anchor(size: tuple[int, int]) -> tuple[int, int]:
    """
    Compute the top-left position to place the feedback overlay.

    Positioning policy (kept consistent with the prior "lower middle" feel):
        - Centered horizontally.
        - Vertically around ~72% of the screen height (slightly below center).
    """
    w, h = size
    x = (cfg.SCREEN_WIDTH - w) // 2
    y = int(cfg.SCREEN_HEIGHT) * 0.85 - (h // 2)
    return x, y


def _draw_timeout_text(screen: pygame.Surface) -> None:
    """
    Render 'Too Slow' using cfg.YELLOW_RGB at the designated position.
    """
    # Use the default font at the configured size.
    font = pygame.font.Font(None, cfg.FONT_SIZE)
    text_surf = font.render("Too Slow", True, cfg.YELLOW_RGB)
    pos = _feedback_anchor(text_surf.get_size())
    screen.blit(text_surf, pos)


# ----------------------- Public API -----------------------

def show_feedback(screen: pygame.Surface, status: str) -> None:
    """
    Draw feedback overlay, flip display, and keep it visible for FEEDBACK_DURATION.

    Args:
        screen: pygame display surface to draw onto.
        status: one of {"correct", "incorrect", "timeout"}.

    Behavior:
        - "correct":   show feedback_correct.png (scaled) at the designated position.
        - "incorrect": show feedback_incorrect.png (scaled) at the designated position.
        - "timeout":   show "Too Slow" text in cfg.YELLOW_RGB at the designated position.

    Note:
        - This function pauses for cfg.FEEDBACK_DURATION ms before returning.
        - The caller should handle clearing the screen after this pause if needed.
    """
    s = status.lower().strip()
    if s == "correct":
        icon = _scale_to_feedback_size(_load_icon(_OK_NAME))
        screen.blit(icon, _feedback_anchor(icon.get_size()))
    elif s == "incorrect":
        icon = _scale_to_feedback_size(_load_icon(_BAD_NAME))
        screen.blit(icon, _feedback_anchor(icon.get_size()))
    elif s == "timeout":
        _draw_timeout_text(screen)
    else:
        raise ValueError(f"Unknown feedback status: {status!r}. "
                         f"Expected 'correct', 'incorrect', or 'timeout'.")

    pygame.display.flip()
    # Keep feedback visible for the configured duration
    pygame.time.delay(cfg.FEEDBACK_DURATION)

__all__ = ["show_feedback"]
