# ./src/core/test_flow.py
import pygame
import random
from typing import Tuple

import utils.config as cfg
from utils.logger import get_logger
from utils.pygame_setup import toggle_full_screen
from ui.ied_ui import show_ied_ui, place_image
from utils.show_feedback import show_feedback
from utils.saves import update_save


logger = get_logger("./src/core/test_flow") # create logger


def _roll_place_ind_for_stimuli() -> tuple[int, int]:
    """
    Randomly select places for stimuli
    Must be different
    """
    correct_ind, incorrect_ind = random.sample((1, 2, 3, 4), 2)
    return (correct_ind, incorrect_ind)


def _load_stimuli_for_phase(screen: pygame.Surface, phase: int, correct_ind: int, incorrect_ind: int) -> None:
    """
    Select the stimuli paths from the assignd phase
    Load and place corresponding stimuli images
    """
    show_ied_ui(screen)
    
    # Place stimuli to target location
    correct_img = getattr(cfg, f"P{phase}_CORRECT")
    incorrect_img = getattr(cfg, f"P{phase}_INCORRECT")

    place_image(screen, correct_img, correct_ind)
    place_image(screen, incorrect_img, incorrect_ind)


def run_test_phase(screen: pygame.Surface, phase: int) -> None:
    """
    Run one phase (round) of test
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
    cfg.correct_count = 0   # clear correct count at the beginning of each phase
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
                        cfg.correct_count += 1  # count 1 correct answer if answered correctly
                        cfg.trial_count += 1    # count 1 trial made
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0   # clear correct count if made a mistake (ensure consecutive correct responses)
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
                
                # If participant selects ⬇️
                if event.key == pygame.K_DOWN:
                    if cfg.correct_ind == 2:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
                
                # If participant selects ⬅️
                if event.key == pygame.K_LEFT:
                    if cfg.correct_ind == 3:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
                
                # If participant selects ➡️
                if event.key == pygame.K_RIGHT:
                    if cfg.correct_ind == 4:
                        feedback_is_correct = True
                        cfg.correct_count += 1
                        cfg.trial_count += 1
                        logger.info(f"Correct response -> current correct count: {cfg.correct_count}, need: {cfg.CORRECT_REQUIREMENT}")
                        update_save(phase, 1)
                    else:
                        feedback_is_correct = False
                        cfg.correct_count = 0
                        cfg.trial_count += 1
                        logger.info(f"Incorrect response -> reset correct count to 0")
                        update_save(phase, 0)
                    feedback_until = pygame.time.get_ticks() + cfg.FB_DURATION
                    waiting = False
        
        _load_stimuli_for_phase(screen, phase, correct_ind, incorrect_ind)

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

                if cfg.correct_count >= cfg.CORRECT_REQUIREMENT:
                    logger.info(f"Passed phase {phase}")
                    running = False

                elif cfg.trial_count >= cfg.FORCE_QUIT_LIMIT:
                    logger.info(f"Trial count: {cfg.trial_count} -> force quit limit reached")
                    running = False
                    cfg.force_quit = True

        pygame.display.flip()
        clock.tick(60)