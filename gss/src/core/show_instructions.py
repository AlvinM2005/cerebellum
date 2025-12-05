# ./src/core/show_instructions.py
import pygame
from pathlib import Path
import random

import utils.config as cfg
import utils.version_dependent_config as vd_cfg
from utils.logger import get_logger
from core.pygame_setup import toggle_full_screen, show_instruction_page
from core.mapping_practice import run_mapping
from core.stroop_practice import run_stroop
from core.gss_practice import run_gss_practice
from core.gss_main import run_gss_main

logger = get_logger("./src/core/show_instructions")    # create logger

def show_instructions(screen: pygame.Surface) -> None:
    """
    Show instructions
    Insert phases after corresponding instruction page
    """
    running = True
    clock = pygame.time.Clock()
    current_page = 0
    img_path = cfg.INSTRUCTIONS[current_page]
    lock_until = pygame.time.get_ticks() + cfg.MIN_READING_TIME
    logger.info(f"Displaying instruction page 1")

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                raise SystemExit

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    toggle_full_screen(screen)
                    pygame.event.clear()

                elif event.key == pygame.K_SPACE:
                    logger.debug(f"[SPACE] pressed => flip to the next instruction page")
                    now = pygame.time.get_ticks()

                    if now > lock_until:

                        if current_page < cfg.INSTRUCTION_COUNT - 1:
                            current_page += 1
                            img_path = cfg.INSTRUCTIONS[current_page]
                            logger.info(f"Displaying instruction page {current_page + 1}")

                            # Mapping practice
                            if current_page == cfg.MAPPING_INS:
                                run_mapping(screen)
                            
                            # Stroop practice
                            elif current_page == cfg.STROOP_INS:
                                run_stroop(screen)
                            
                            # GSS practice
                            elif current_page == cfg.GSS_PRACTICE_INS:
                                run_gss_practice(screen)
                            
                            # GSS main
                            elif current_page == cfg.GSS_MAIN_SEC1_INS or current_page == cfg.GSS_MAIN_SEC2_INS or current_page == cfg.GSS_MAIN_SEC3_INS:
                                run_gss_main(screen)
                        
                        else:
                            logger.info(f"No more insturction page")
                            running = False

                        lock_until = pygame.time.get_ticks() + cfg.MIN_READING_TIME

                        pygame.event.clear()
                    
        show_instruction_page(screen, img_path)
        
        pygame.display.flip()
        clock.tick(60)