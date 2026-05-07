# ./src/ui/video.py
"""
Video playback and overlay utilities for the soccer prediction task.

Requires opencv-python:
    pip install opencv-python
"""

import pygame
import utils.config as cfg
import utils.paths as paths
from utils.logger import get_logger

logger = get_logger("./src/ui/video")

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    logger.error("cv2 not found. Install with: pip install opencv-python")

# Cache: screen_size -> guide surface
_guide_cache: dict[tuple, pygame.Surface] = {}


def play_video(
    screen: pygame.Surface,
    video_path,
    stop_at_sec: float,
) -> pygame.Surface | None:
    """
    Play a video file from frame 0 until stop_at_sec seconds have elapsed.

    Returns the last frame rendered as a Surface (already scaled to screen size),
    or None if playback could not start. The caller uses this to freeze-display
    the last frame during the response window.

    :param screen: Active pygame display surface.
    :param video_path: Path-like pointing to the .mp4 file.
    :param stop_at_sec: Playback stops when the video position reaches this time (seconds).
    :return: Last rendered frame as a pygame.Surface, or None.
    """
    if not _CV2_AVAILABLE:
        logger.error("Skipping video playback — cv2 not installed.")
        return None

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error("Could not open video: %s", video_path)
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_ms = int(1000 / fps)
    sw, sh = screen.get_size()
    last_surf: pygame.Surface | None = None

    while cap.isOpened():
        pos_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if pos_sec >= stop_at_sec:
            break

        t0 = pygame.time.get_ticks()
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        fh, fw = frame_rgb.shape[:2]
        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (fw, fh), 'RGB')
        surf = pygame.transform.scale(surf, (sw, sh))
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        last_surf = surf

        pygame.event.pump()

        elapsed = pygame.time.get_ticks() - t0
        pygame.time.delay(max(1, frame_ms - elapsed))

    cap.release()
    return last_surf


def get_guide_overlay(screen_size: tuple[int, int]) -> pygame.Surface:
    """
    Return SOC_Guide.png scaled to screen_size, with alpha preserved.
    Result is cached so the file is only loaded once per screen resolution.

    :param screen_size: (width, height) of the current display.
    :return: pygame.Surface ready to blit over a frozen video frame.
    """
    if screen_size not in _guide_cache:
        raw = pygame.image.load(str(paths.MAPPING)).convert_alpha()
        _guide_cache[screen_size] = pygame.transform.scale(raw, screen_size)
    return _guide_cache[screen_size]


def show_frozen_frame(
    screen: pygame.Surface,
    last_frame: pygame.Surface | None,
    guide: pygame.Surface,
) -> None:
    """
    Blit the frozen video frame then the guide overlay onto screen and flip.
    Falls back to black if last_frame is None.
    """
    if last_frame is not None:
        scaled = pygame.transform.scale(last_frame, screen.get_size())
        screen.blit(scaled, (0, 0))
    else:
        screen.fill(cfg.BLACK_RGB)
    screen.blit(guide, (0, 0))
    pygame.display.flip()
