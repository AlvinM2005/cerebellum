from __future__ import annotations
import cv2
import pygame
import math
import time
import numpy as np
import re

import utils.config as cfg
import ui.pygame_render as render

IDLE_FLASH_AFTER_S = 10.0   # seconds without mouse movement before the line flashes
FLASH_PERIOD_S = 0.7        # duration of each fade-out / fade-in while flashing
# Empty band in the base image (stim_instruction.png, 1600x900) where the stimulus image goes,
# as fractions of the base image height: below the instruction text, above "Press SPACE to continue."
STIM_AREA_TOP = 335 / 900
STIM_AREA_BOTTOM = 848 / 900
STIM_AREA_MAX_WIDTH = 0.8   # max stimulus width as a fraction of the screen width
STIM_AREA_PADDING = 25      # pixels of space kept between the stimulus image and the text
SLIDER_LABELS =("negative emotion", "neutral", "positive emotion")

_label_font: pygame.font.Font | None = None


def _draw_slider(screen: pygame.Surface, x: float, flash_elapsed: float | None = None) -> None:
    """
    Draw a horizontal slider overlay in the middle of the screen.

    :param screen: Current display surface
    :param x: Normalised slider position in [-1, 1]
    :param flash_elapsed: Seconds since the line started flashing (participant is idle),
        or None if it should be drawn solid
    """
    global _label_font
    if _label_font is None:
        _label_font = pygame.font.SysFont(None, 36)

    w, h = screen.get_size()

    bar_y = h // 2
    bar_x0 = int(w * 0.1)
    bar_x1 = int(w * 0.9)
    bar_h = 6
    bar_rect = (bar_x0, bar_y - bar_h // 2, bar_x1 - bar_x0, bar_h)
    if flash_elapsed is None:
        pygame.draw.rect(screen, cfg.COCO_RGB, bar_rect)
    else:
        # Cosine wave: starts fully visible, fades out over FLASH_PERIOD_S, fades back in over FLASH_PERIOD_S
        alpha = int(255 * (1 + math.cos(math.pi * flash_elapsed / FLASH_PERIOD_S)) / 2)
        bar_surf = pygame.Surface((bar_rect[2], bar_rect[3]), pygame.SRCALPHA)
        bar_surf.fill((*pygame.Color(cfg.COCO_RGB)[:3], alpha))
        screen.blit(bar_surf, bar_rect[:2])

    marker_xs = (bar_x0, (bar_x0 + bar_x1) // 2, bar_x1)  # left, center, right
    for mx, label in zip(marker_xs, SLIDER_LABELS):
        pygame.draw.rect(screen, cfg.COCO_RGB, (mx - 4, bar_y - 20, 8, 40))
        text_surf = _label_font.render(label, True, cfg.COCO_RGB)
        screen.blit(text_surf, text_surf.get_rect(midtop=(mx, bar_y + 30)))

    marker_x = int(bar_x0 + (x + 1) / 2 * (bar_x1 - bar_x0))
    pygame.draw.circle(screen, cfg.RED_RGB, (marker_x, bar_y), 16) # Tracker
    pygame.draw.circle(screen, cfg.COCO_RGB, (marker_x, bar_y), 16, 2) # Outline for tracker

def find_condition(path: str) -> str:
    pattern = r'(stimuli/context)'
    match = re.search(pattern, path, re.IGNORECASE)
    if match:
        print(match.group().lower())
        return "context"
    else:
        return "baseline" 

def place_stim_img(screen: pygame.Surface, base_path: str, stim_path: str, event_handler=None) -> pygame.Surface:
    """
    Draw a base image over the whole screen, then the stimulus image on top of it
    in the bottom half of the screen.

    :param screen: Current display surface
    :param base_path: Path to the base (background) image, stretched to fill the screen
    :param stim_path: Path to the stimulus image, drawn at its original size (not scaled),
        centered in the bottom half of the screen
    :param event_handler: EventHandler instance for handling events
    """
    screen_rect = screen.get_rect()

    # Base image: fill the whole screen
    render.place_image(screen, base_path) 

    # Find where the base image's empty band landed on screen. place_image scales the base
    # to cover the screen (keeping aspect ratio) and centers it, so apply the same transform.
    base_w, base_h = pygame.image.load(str(base_path)).get_size()
    base_scale = max(screen_rect.width / base_w, screen_rect.height / base_h)
    base_top = (screen_rect.height - base_h * base_scale) / 2
    area_top = base_top + STIM_AREA_TOP * base_h * base_scale + STIM_AREA_PADDING
    area_bottom = base_top + STIM_AREA_BOTTOM * base_h * base_scale - STIM_AREA_PADDING
    area_w = screen_rect.width * STIM_AREA_MAX_WIDTH
    area_h = area_bottom - area_top

    # Stimulus image: scaled to fit the band (aspect ratio kept), centered in it
    stim_img = pygame.image.load(str(stim_path)).convert_alpha()
    stim_scale = min(area_w / stim_img.get_width(), area_h / stim_img.get_height())
    stim_size = (int(stim_img.get_width() * stim_scale), int(stim_img.get_height() * stim_scale))
    stim_img = pygame.transform.smoothscale(stim_img, stim_size)
    stim_rect = stim_img.get_rect(center=(screen_rect.centerx, (area_top + area_bottom) / 2))
    screen.blit(stim_img, stim_rect)
    pygame.display.flip()

    return render._wait_for_next_page(screen, event_handler)

def play_video(
    screen: pygame.Surface,
    video_path: str,
    mouse_cord_dot=None,
    event_handler=None,
    block: str = "",
    video_name: str = "",
    logger=None,
) -> tuple[pygame.Surface, list, list, list]:
    """
    Play a video file frame-by-frame with optional slider overlay and event handling.

    :param screen: Current display surface
    :param video_path: Path to the video file
    :param mouse_cord_dot: MouseCordDot instance for slider tracking (optional)
    :param event_handler: EventHandler for quit/fullscreen events (optional)
    :param block: Block name for per-frame logging (optional)
    :param video_name: Video filename for per-frame logging (optional)
    :param logger: Logger instance (optional)
    :return: Active display surface (may change on fullscreen toggle)
    """
    from ui.pygame_render import toggle_full_screen

    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS) or 60
    clock = pygame.time.Clock()

    ms = []
    x_pos = []
    y_pos = []
    start_ticks = time.perf_counter()
    frame_num = 0
    last_mouse_pos = pygame.mouse.get_pos()
    last_move_time = start_ticks

    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        width, height = screen.get_size()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        surface = pygame.surfarray.make_surface(frame_rgb)
        surface = pygame.transform.scale(surface, (width*.9,height*.9))
        screen_rect = screen.get_rect()
        center_x, center_y = screen_rect.center
        surface_rect = surface.get_rect(center=(center_x, center_y-20))
        screen.blit(surface, surface_rect)

        x, y = 0.0, 0.0
        if mouse_cord_dot is not None:
            x, y = mouse_cord_dot.clamp(limit=1.0)
            mouse_pos = pygame.mouse.get_pos()
            now = time.perf_counter()
            if mouse_pos != last_mouse_pos:
                last_mouse_pos = mouse_pos
                last_move_time = now
            # Trigger bar flash if idle for > IDLE_FLASH_AFTER_S seconds
            idle_time = now - last_move_time
            flash_elapsed = idle_time - IDLE_FLASH_AFTER_S if idle_time >= IDLE_FLASH_AFTER_S else None
            _draw_slider(screen, x, flash_elapsed=flash_elapsed)

        pygame.display.flip()
        elapsed_time = time.perf_counter() - start_ticks
        frame_num = int(round(elapsed_time * fps))

        if logger is not None:
            logger.info(
                "FRAME | block=%s | video=%s | ticks=%d | frame=%d | x=%.4f | y=%.4f",
                block,
                video_name,
                elapsed_time,
                frame_num,
                x,
                y,

            )
        x_pos = np.append(x_pos, x)
        y_pos = np.append(y_pos, y)
        ms = np.append(ms, frame_num)

        if event_handler is not None:
            state = event_handler.poll()
            if state.quit:
                capture.release()
                pygame.quit()
                raise SystemExit
            if state.toggle_full_screen:
                pygame.event.clear()
                screen = toggle_full_screen(screen)
                pygame.event.clear()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    capture.release()
                    return screen
        # frame_num += 1
        clock.tick(fps)

    capture.release()
    return (screen, x_pos, y_pos, ms)
