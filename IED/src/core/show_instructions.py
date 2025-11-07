# ./src/core/show_instructions.py
import pygame
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import toggle_full_screen
from core.test_flow import run_practice, run_single_stimulus_phase, run_side_by_side_multiple_stimulus_phase, run_overlapped_multiple_stimulus_phase_targeting_shape, run_overlapped_multiple_stimulus_phase_targeting_line

logger = get_logger("./src/core/show_instructions")    # create logger

def show_instruction_page(screen: pygame.Surface, img_path: Path) -> None:
    # Load image
    p = Path(img_path)
    if not p.exists():
        logger.error(f"show_feedback: file not found -> {img_path}")
        return None

    try:
        img = pygame.image.load(str(p)).convert_alpha()
    except Exception as e:
        logger.error(f"show_feedback: failed to load image -> {img_path} | {e}")
        return None

    # Resize image (max_W = w / max_H = h)
    w, h = screen.get_size()
    orig_w, orig_h = img.get_size()
    if orig_w <= 0 or orig_h <= 0:
        logger.error(f"show_feedback: invalid image size -> {img_path} ({orig_w}x{orig_h})")
        return None

    scale = min(w / orig_w, h / orig_h)
    new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    if new_size != (orig_w, orig_h):
        img = pygame.transform.smoothscale(img, new_size)

    # Compute center
    cx, cy = w / 2, h / 2
    center = (int(cx), int(cy))

    # Place feedback image at target location
    img_rect = img.get_rect(center=center)
    screen.blit(img, img_rect)

def show_instructions(screen: pygame.Surface) -> None:
    """
    Show instructions
    Insert phases after corresponding instruction page
    """

    running = True
    waiting = True
    clock = pygame.time.Clock()
    current_page = 0
    img_path = cfg.INSTRUCTIONS[current_page]
    lock_until = pygame.time.get_ticks() + cfg.MIN_READING_TIME
    logger.info(f"Displaying instruction page 1")

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif waiting and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_full_screen(screen)
                elif event.key == pygame.K_SPACE:
                    logger.debug(f"Space is pressed")
                    now = pygame.time.get_ticks()
                    if now > lock_until:
                        if current_page < cfg.INSTRUCTION_COUNT - 1:
                            current_page += 1
                            img_path = cfg.INSTRUCTIONS[current_page]
                            logger.info(f"Displaying instruction page {current_page + 1}")

                            if current_page == cfg.PRACTICE1:
                                run_practice(screen, "PRACTICE1")
                            elif current_page == cfg.PRACTICE2:
                                run_practice(screen, "PRACTICE2")
                            elif current_page == cfg.PHASES:
                                run_single_stimulus_phase(screen, "P1", True)
                                run_single_stimulus_phase(screen, "P2", False)
                                run_side_by_side_multiple_stimulus_phase(screen, "P3")
                                run_overlapped_multiple_stimulus_phase_targeting_shape(screen, "P4")
                                run_overlapped_multiple_stimulus_phase_targeting_shape(screen, "P5")
                                run_overlapped_multiple_stimulus_phase_targeting_shape(screen, "P6")
                                run_overlapped_multiple_stimulus_phase_targeting_shape(screen, "P7")
                                run_overlapped_multiple_stimulus_phase_targeting_line(screen, "P8")
                                run_overlapped_multiple_stimulus_phase_targeting_line(screen, "P9")
                        
                        else:
                            logger.info(f"No more insturction page")
                            running = False
                        lock_until = pygame.time.get_ticks() + cfg.MIN_READING_TIME
                        pygame.event.clear()
                    
        show_instruction_page(screen, img_path)
        
        pygame.display.flip()
        clock.tick(60)