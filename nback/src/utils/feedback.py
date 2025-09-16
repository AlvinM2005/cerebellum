from __future__ import annotations
from pathlib import Path
import pygame
import utils.config as cfg

# Cache loaded images to avoid disk I/O every trial
_CACHE: dict[str, pygame.Surface] = {}

# Resource paths (PNG ~400x400)
RES_DIR = Path("resources") / "feedback"
PATH_CORRECT   = RES_DIR / "feedback_correct.png"
PATH_INCORRECT = RES_DIR / "feedback_incorrect.png"

def _load_image(path: Path) -> pygame.Surface:
    """Load and cache a feedback image."""
    key = str(path.resolve())
    if key in _CACHE:
        return _CACHE[key]
    if not path.exists():
        raise FileNotFoundError(f"Feedback image not found: {path}")
    img = pygame.image.load(str(path)).convert_alpha()
    _CACHE[key] = img
    return img

def _blit_lower_center(screen: pygame.Surface, surf: pygame.Surface, max_px: int = 400) -> None:
    """
    Scale surf to fit within max_px x max_px, then draw it at 'middle-lower' area:
    horizontally centered, vertically around ~72% screen height.
    """
    sw, sh = screen.get_size()
    iw, ih = surf.get_size()
    scale = min(max_px / iw, max_px / ih, 1.0)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    surf_scaled = pygame.transform.smoothscale(surf, new_size)
    target_y = int(sh * 0.72)
    rect = surf_scaled.get_rect(center=(sw // 2, target_y))
    screen.blit(surf_scaled, rect.topleft)

def _blit_too_slow_text(screen: pygame.Surface, font_name: str | None = None) -> None:
    """
    Render 'Too Slow' in yellow at the same lower-center position as the images.
    """
    sw, sh = screen.get_size()
    font = pygame.font.SysFont(font_name, max(18, int(sh * 0.06)))
    text_surf = font.render("Too Slow", True, getattr(cfg, "YELLOW_RGB", (255, 204, 0)))
    rect = text_surf.get_rect(center=(sw // 2, int(sh * 0.72)))
    screen.blit(text_surf, rect.topleft)

def show_after_trial(
    screen: pygame.Surface,
    block_name: str,
    *,
    is_practice_only: bool = True,
    is_correct: bool | None = None,
    participant_pressed: bool | None = None,  # True/False for pressed or not; None if unknown
    correct_is_nogo: bool = False,
    duration_ms: int | None = None,
) -> None:
    """
    Show trial feedback for practice blocks.

    Parameters
    ----------
    screen : pygame.Surface
        Pygame screen to draw onto (assumed already showing the stimulus background).
    block_name : str
        Current block name, e.g., 'PRACTICE1', 'BLOCK3', ...
    is_practice_only : bool
        If True, only PRACTICE1/2/3 will display feedback; other blocks skip silently.
    is_correct : bool | None
        Whether the trial is correct/incorrect (for ✅/❌). If None and Too Slow applies, the text will show.
    participant_pressed : bool | None
        Whether any key was pressed during response window; used to detect Too Slow.
    correct_is_nogo : bool
        Whether the correct answer for this trial is NOGO.
    duration_ms : int | None
        How long to show feedback; default uses cfg.FEEDBACK_MS if present, else 600ms.
    """
    # Guard: practice-only display
    if is_practice_only:
        if block_name not in ("PRACTICE1", "PRACTICE2", "PRACTICE3"):
            return

    dur = duration_ms if duration_ms is not None else getattr(cfg, "FEEDBACK_MS", 600)

    # Decide which feedback to show:
    # - Too Slow: no key pressed AND correct answer is not NOGO
    # - Else Correct / Incorrect via images
    show_too_slow = (participant_pressed is False) and (not correct_is_nogo)

    if show_too_slow:
        _blit_too_slow_text(screen)
    else:
        if is_correct is True:
            img = _load_image(PATH_CORRECT)
            _blit_lower_center(screen, img, max_px=400)
        elif is_correct is False:
            img = _load_image(PATH_INCORRECT)
            _blit_lower_center(screen, img, max_px=400)
        else:
            # Nothing to display if state is unknown
            return

    pygame.display.flip()

    # Keep on screen for 'dur' ms, but still responsive to ESC/quit
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < dur:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Allow toggling even during feedback
                from src.ui.main_window import toggle_full_screen  # local import to avoid cycle
                toggle_full_screen(screen)
                pygame.display.flip()
        pygame.time.delay(5)
