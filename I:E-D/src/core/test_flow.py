# ./src/core/test_flow.py
import pygame
import random
from typing import Tuple
from pathlib import Path

import utils.config as cfg
from utils.logger import get_logger
from core.pygame_setup import toggle_full_screen
from ui.ied_ui import show_ied_ui, place_single_image, place_overlapped_images, place_side_by_side_images
from core.show_feedback import show_feedback
from core.saves import update_save


logger = get_logger("./src/core/test_flow") # create logger


def _roll_place_ind_for_stimuli() -> tuple[int, int]:
    """
    Randomly select places for stimuli
    Must be different
    """
    correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
    return (correct_ind, incorrect_ind)


def _load_stimulus_for_practice(screen: pygame.Surface, phase: int, correct_ind: int, incorrect_ind: int) -> None:
    """
    Select target stimulus path from the assignd phase
    Load and placetarget stimulus
    """
    show_ied_ui(screen)
    
    # Place stimuli to target location
    correct_img = getattr(cfg, f"{phase}_CORRECT")
    incorrect_img = getattr(cfg, f"{phase}_INCORRECT")

    place_single_image(screen, correct_img, correct_ind)
    place_single_image(screen, incorrect_img, incorrect_ind)


def run_practice(screen: pygame.Surface, phase: str) -> None:
    """
    Run one practice phase (Practice1 / Practice2)
    Automatically quit when make cfg.CORRECT_REQUIRMENT correct choices consecutively
    """
    running = True  # whether the test phase runs
    waiting = True  # whether hearing keyboard inputs
    clock = pygame.time.Clock()
    feedback_until = 0
    feedback_is_correct = None
    correct_ind, incorrect_ind = _roll_place_ind_for_stimuli()
    cfg.correct_ind = correct_ind
    logger.info(f"Correct ind is set to {cfg.correct_ind}")
    cfg.trial_count = 0     # clear trial count at the beginning of each phase
    
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cfg.force_quit = True
            elif waiting and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_full_screen(screen)
                
                # If participant selects ⬆️
                if event.key == pygame.K_UP:
                    if cfg.correct_ind == 1:
                        feedback_is_correct = True
                        cfg.trial_count += 1    # count 1 trial made
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
                
                # If participant selects ⬇️
                if event.key == pygame.K_DOWN:
                    if cfg.correct_ind == 2:
                        feedback_is_correct = True
                        cfg.trial_count += 1
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
                
                # If participant selects ⬅️
                if event.key == pygame.K_LEFT:
                    if cfg.correct_ind == 3:
                        feedback_is_correct = True
                        cfg.trial_count += 1
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
                
                # If participant selects ➡️
                if event.key == pygame.K_RIGHT:
                    if cfg.correct_ind == 4:
                        feedback_is_correct = True
                        cfg.trial_count += 1
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
        
        _load_stimulus_for_practice(screen, phase, correct_ind, incorrect_ind)

        # Show feedback & update stimuli (proceed to next trial)
        now = pygame.time.get_ticks()
        if feedback_is_correct is not None:
            if now < feedback_until:
                show_feedback(screen, feedback_is_correct)
            else:
                feedback_is_correct = None
                screen.fill(cfg.GRAY_RGB)
                pygame.display.flip()
                pygame.time.wait(cfg.ISI_MS)
                pygame.event.clear()
                correct_ind, incorrect_ind = _roll_place_ind_for_stimuli()
                cfg.correct_ind = correct_ind
                logger.info(f"Correct ind is set to {cfg.correct_ind}")
                waiting = True

                if cfg.trial_count >= cfg.PRACTICE_TRIAL_REQUIREMENT:
                    if pygame.time.get_ticks() >= feedback_until:
                        logger.info(f"Passed phase {phase}")
                        running = False

        pygame.display.flip()
        clock.tick(60)


def _load_single_stimulus(screen: pygame.Surface, phase: int, correct_ind: int, incorrect_ind: int) -> None:
    """
    Select target stimulus path from the assignd phase
    Load and place target stimulus
    """
    show_ied_ui(screen)
    
    # Place stimuli to target location
    correct_img = getattr(cfg, f"{phase}_CORRECT")
    incorrect_img = getattr(cfg, f"{phase}_INCORRECT")

    place_single_image(screen, correct_img, correct_ind)
    place_single_image(screen, incorrect_img, incorrect_ind)


def run_single_stimulus_phase(screen: pygame.Surface, phase: str, show_FE_FB: bool) -> None:
    """
    Run one phase with only one stimulus image (P1/P2)
    Automatically quit when making cfg.CORRECT_REQUIREMENT correct choices consecutively
    """
    running = True  # whether the test phase runs
    waiting = True  # whether hearing keyboard inputs
    clock = pygame.time.Clock()
    feedback_until = 0
    fe_feedback_until = -1
    feedback_is_correct = None

    correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
    cfg.correct_ind = correct_ind
    logger.info(f"Correct ind is set to {cfg.correct_ind}")

    cfg.correct_count = 0  # clear correct count at the beginning of each phase
    cfg.trial_count = 0    # clear trial count at the beginning of each phase

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cfg.force_quit = True

            elif waiting and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_full_screen(screen)

                # ⬆️
                if event.key == pygame.K_UP:
                    if cfg.correct_ind == 1:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    if show_FE_FB:
                        fe_feedback_until = pygame.time.get_ticks() + cfg.FE_FB_DURATION
                    waiting = False

                # ⬇️
                if event.key == pygame.K_DOWN:
                    if cfg.correct_ind == 2:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    if show_FE_FB:
                        fe_feedback_until = pygame.time.get_ticks() + cfg.FE_FB_DURATION
                    waiting = False

                # ⬅️
                if event.key == pygame.K_LEFT:
                    if cfg.correct_ind == 3:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    if show_FE_FB:
                        fe_feedback_until = pygame.time.get_ticks() + cfg.FE_FB_DURATION
                    waiting = False

                # ➡️
                if event.key == pygame.K_RIGHT:
                    if cfg.correct_ind == 4:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    if show_FE_FB:
                        fe_feedback_until = pygame.time.get_ticks() + cfg.FE_FB_DURATION
                    waiting = False

        _load_single_stimulus(screen, phase, correct_ind, incorrect_ind)

        # Show feedback & update stimuli
        now = pygame.time.get_ticks()
        if feedback_is_correct is not None:
            # Display note: "Remember, the rules might change"
            if not feedback_is_correct and now < fe_feedback_until:
                show_feedback(screen, feedback_is_correct)
                font = pygame.font.SysFont(None, cfg.FONT_SIZE)
                text_surface = font.render("Remember, the rules might change", True, cfg.BLACK_RGB)
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2, int(screen.get_height() * 0.9)))
                screen.blit(text_surface, text_rect)
                show_FE_FB = False

            # Display normal feedback
            elif now < feedback_until:
                show_feedback(screen, feedback_is_correct)
            else:
                feedback_is_correct = None
                screen.fill(cfg.GRAY_RGB)
                pygame.display.flip()
                pygame.time.wait(cfg.ISI_MS)
                pygame.event.clear()

                correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
                cfg.correct_ind = correct_ind
                logger.info(f"Correct ind is set to {cfg.correct_ind}")
                waiting = True

        if cfg.correct_count >= cfg.CORRECT_REQUIREMENT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Passed phase {phase}")
                running = False
        elif cfg.trial_count >= cfg.FORCE_QUIT_LIMIT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Trial count: {cfg.trial_count} -> force quit limit reached")
                running = False
                cfg.force_quit = True

        pygame.display.flip()
        clock.tick(60)


def _load_side_by_side_multiple_stimulus(screen: pygame.Surface, phase: int, correct_ind: int, incorrect_ind: int, buffer1_img: Path, buffer2_img: Path) -> None:
    """
    Select target stimulus path from the assignd phase
    Load and place target stimulus
    """
    show_ied_ui(screen)
    
    # Place stimuli to target location
    correct_img = getattr(cfg, f"{phase}_CORRECT")
    incorrect_img = getattr(cfg, f"{phase}_INCORRECT")

    place_side_by_side_images(screen, correct_img, buffer1_img, correct_ind)
    place_side_by_side_images(screen, incorrect_img, buffer2_img, incorrect_ind)


def run_side_by_side_multiple_stimulus_phase(screen: pygame.Surface, phase: str) -> None:
    """
    Run one phase with two overlapped stimuli images (P3).
    Automatically quit when making cfg.CORRECT_REQUIREMENT correct choices consecutively
    """
    running = True  # whether the test phase runs
    waiting = True  # whether hearing keyboard inputs
    clock = pygame.time.Clock()
    feedback_until = 0
    fe_feedback_until = -1
    feedback_is_correct = None

    buffer1_img, buffer2_img = random.sample([getattr(cfg, f"{phase}_BUFFER1"), getattr(cfg, f"{phase}_BUFFER2")], 2)

    correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
    cfg.correct_ind = correct_ind
    logger.info(f"Correct ind is set to {cfg.correct_ind}")

    cfg.correct_count = 0  # clear correct count at the beginning of each phase
    cfg.trial_count = 0    # clear trial count at the beginning of each phase

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cfg.force_quit = True

            elif waiting and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_full_screen(screen)

                # ⬆️
                if event.key == pygame.K_UP:
                    if cfg.correct_ind == 1:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ⬇️
                if event.key == pygame.K_DOWN:
                    if cfg.correct_ind == 2:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ⬅️
                if event.key == pygame.K_LEFT:
                    if cfg.correct_ind == 3:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ➡️
                if event.key == pygame.K_RIGHT:
                    if cfg.correct_ind == 4:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

        _load_side_by_side_multiple_stimulus(screen, phase, correct_ind, incorrect_ind, buffer1_img, buffer2_img)

        # Show feedback & update stimuli
        now = pygame.time.get_ticks()
        if feedback_is_correct is not None:
            # Display normal feedback
            if now < feedback_until:
                show_feedback(screen, feedback_is_correct)
            else:
                feedback_is_correct = None
                screen.fill(cfg.GRAY_RGB)
                pygame.display.flip()
                pygame.time.wait(cfg.ISI_MS)
                pygame.event.clear()

                correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
                cfg.correct_ind = correct_ind
                logger.info(f"Correct ind is set to {cfg.correct_ind}")

                buffer1_img, buffer2_img = random.sample([getattr(cfg, f"{phase}_BUFFER1"), getattr(cfg, f"{phase}_BUFFER2")], 2)

                waiting = True

        if cfg.correct_count >= cfg.CORRECT_REQUIREMENT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Passed phase {phase}")
                running = False
        elif cfg.trial_count >= cfg.FORCE_QUIT_LIMIT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Trial count: {cfg.trial_count} -> force quit limit reached")
                running = False
                cfg.force_quit = True

        pygame.display.flip()
        clock.tick(60)


def _load_overlapped_multiple_stimulus_targeting_shape(screen: pygame.Surface, phase: int, correct_ind: int, incorrect_ind: int, buffer1_img: Path, buffer2_img: Path) -> None:
    """
    Select target stimulus path from the assignd phase
    Load and place target stimulus
    """
    show_ied_ui(screen)
    
    # Place stimuli to target location
    correct_img = getattr(cfg, f"{phase}_CORRECT")
    incorrect_img = getattr(cfg, f"{phase}_INCORRECT")

    place_overlapped_images(screen, correct_img, buffer1_img, correct_ind)
    place_overlapped_images(screen, incorrect_img, buffer2_img, incorrect_ind)


def run_overlapped_multiple_stimulus_phase_targeting_shape(screen: pygame.Surface, phase: str) -> None:
    """
    Run one phase with two overlapped stimuli (target = shape) images (P4-P7).
    Automatically quit when making cfg.CORRECT_REQUIREMENT correct choices consecutively
    """
    running = True  # whether the test phase runs
    waiting = True  # whether hearing keyboard inputs
    clock = pygame.time.Clock()
    feedback_until = 0
    fe_feedback_until = -1
    feedback_is_correct = None

    buffer1_img, buffer2_img = random.sample([getattr(cfg, f"{phase}_BUFFER1"), getattr(cfg, f"{phase}_BUFFER2")], 2)

    correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
    cfg.correct_ind = correct_ind
    logger.info(f"Correct ind is set to {cfg.correct_ind}")

    cfg.correct_count = 0  # clear correct count at the beginning of each phase
    cfg.trial_count = 0    # clear trial count at the beginning of each phase

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cfg.force_quit = True

            elif waiting and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_full_screen(screen)

                # ⬆️
                if event.key == pygame.K_UP:
                    if cfg.correct_ind == 1:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ⬇️
                if event.key == pygame.K_DOWN:
                    if cfg.correct_ind == 2:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ⬅️
                if event.key == pygame.K_LEFT:
                    if cfg.correct_ind == 3:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ➡️
                if event.key == pygame.K_RIGHT:
                    if cfg.correct_ind == 4:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

        _load_overlapped_multiple_stimulus_targeting_shape(screen, phase, correct_ind, incorrect_ind, buffer1_img, buffer2_img)

        # Show feedback & update stimuli
        now = pygame.time.get_ticks()
        if feedback_is_correct is not None:
            # Display normal feedback
            if now < feedback_until:
                show_feedback(screen, feedback_is_correct)
            else:
                feedback_is_correct = None
                screen.fill(cfg.GRAY_RGB)
                pygame.display.flip()
                pygame.time.wait(cfg.ISI_MS)
                pygame.event.clear()

                correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
                cfg.correct_ind = correct_ind
                logger.info(f"Correct ind is set to {cfg.correct_ind}")

                buffer1_img, buffer2_img = random.sample([getattr(cfg, f"{phase}_BUFFER1"), getattr(cfg, f"{phase}_BUFFER2")], 2)

                waiting = True

        if cfg.correct_count >= cfg.CORRECT_REQUIREMENT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Passed phase {phase}")
                running = False
        elif cfg.trial_count >= cfg.FORCE_QUIT_LIMIT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Trial count: {cfg.trial_count} -> force quit limit reached")
                running = False
                cfg.force_quit = True

        pygame.display.flip()
        clock.tick(60)


def _load_overlapped_multiple_stimulus_targeting_line(screen: pygame.Surface, phase: int, correct_ind: int, incorrect_ind: int, buffer1_img: Path, buffer2_img: Path) -> None:
    """
    Select target stimulus path from the assignd phase
    Load and place target stimulus
    """
    show_ied_ui(screen)
    
    # Place stimuli to target location
    correct_img = getattr(cfg, f"{phase}_CORRECT")
    incorrect_img = getattr(cfg, f"{phase}_INCORRECT")

    place_overlapped_images(screen, buffer1_img, correct_img, correct_ind)
    place_overlapped_images(screen, buffer2_img, incorrect_img, incorrect_ind)


def run_overlapped_multiple_stimulus_phase_targeting_line(screen: pygame.Surface, phase: str) -> None:
    """
    Run one phase with two overlapped stimuli (target = line) images (P8/P9).
    Automatically quit when making cfg.CORRECT_REQUIREMENT correct choices consecutively
    """
    running = True  # whether the test phase runs
    waiting = True  # whether hearing keyboard inputs
    clock = pygame.time.Clock()
    feedback_until = 0
    fe_feedback_until = -1
    feedback_is_correct = None

    buffer1_img, buffer2_img = random.sample([getattr(cfg, f"{phase}_BUFFER1"), getattr(cfg, f"{phase}_BUFFER2")], 2)

    correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
    cfg.correct_ind = correct_ind
    logger.info(f"Correct ind is set to {cfg.correct_ind}")

    cfg.correct_count = 0  # clear correct count at the beginning of each phase
    cfg.trial_count = 0    # clear trial count at the beginning of each phase

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cfg.force_quit = True

            elif waiting and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    toggle_full_screen(screen)

                # ⬆️
                if event.key == pygame.K_UP:
                    if cfg.correct_ind == 1:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ⬇️
                if event.key == pygame.K_DOWN:
                    if cfg.correct_ind == 2:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ⬅️
                if event.key == pygame.K_LEFT:
                    if cfg.correct_ind == 3:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

                # ➡️
                if event.key == pygame.K_RIGHT:
                    if cfg.correct_ind == 4:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(
                            f"Correct response -> current correct count: {cfg.correct_count}, "
                            f"need: {cfg.CORRECT_REQUIREMENT}"
                        )
                        update_save(f"{phase}", 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info("Incorrect response -> reset correct count to 0")
                        update_save(f"{phase}", 0)

                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False

        _load_overlapped_multiple_stimulus_targeting_line(screen, phase, correct_ind, incorrect_ind, buffer1_img, buffer2_img)

        # Show feedback & update stimuli
        now = pygame.time.get_ticks()
        if feedback_is_correct is not None:
            # Display normal feedback
            if now < feedback_until:
                show_feedback(screen, feedback_is_correct)
            else:
                feedback_is_correct = None
                screen.fill(cfg.GRAY_RGB)
                pygame.display.flip()
                pygame.time.wait(cfg.ISI_MS)
                pygame.event.clear()

                correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
                cfg.correct_ind = correct_ind
                logger.info(f"Correct ind is set to {cfg.correct_ind}")

                buffer1_img, buffer2_img = random.sample([getattr(cfg, f"{phase}_BUFFER1"), getattr(cfg, f"{phase}_BUFFER2")], 2)

                waiting = True

        if cfg.correct_count >= cfg.CORRECT_REQUIREMENT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Passed phase {phase}")
                running = False
        elif cfg.trial_count >= cfg.FORCE_QUIT_LIMIT:
            if pygame.time.get_ticks() >= feedback_until:
                logger.info(f"Trial count: {cfg.trial_count} -> force quit limit reached")
                running = False
                cfg.force_quit = True

        pygame.display.flip()
        clock.tick(60)