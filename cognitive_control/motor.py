import pygame
from stimuli import *
from meta_parameters import *
from generate_trials import *
from feedback import *
from framework import *
from save_results import *
from instructions import *
from datetime import datetime

# General key input / response function 
def key_logging(time_allowed, screen, current_image=None, is_fixation=False, condition="motor"):
    """
    Enhanced key logging with fullscreen toggle support and screen redraw
    current_image: the current image being displayed (for redraw after toggle)
    is_fixation: whether we're currently showing fixation or stimulus
    condition: task condition to determine which fixation to use
    """
    start_time = pygame.time.get_ticks()
    key_response = None
    reaction_time = 0

    while pygame.time.get_ticks() - start_time < time_allowed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Handle window close button (X) - graceful exit
                print("=== QUIT EVENT DETECTED - EXITING GRACEFULLY ===")
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Handle ESC key for fullscreen toggle
                    from framework import toggle_fullscreen
                    screen = toggle_fullscreen(screen)  # Update screen reference
                    
                    # Redraw the current screen after toggle
                    screen.fill(GRAY_RGB)  # Clear screen first
                    screen_rect = screen.get_rect()
                    
                    if current_image is not None:
                        # Redraw the current image with new scaling
                        if is_fixation:
                            # Redraw fixation
                            if condition in ["motor", "sensorimotor"]:
                                fixation_scaled = get_scaled_stimulus(FIXATION, screen)
                                fixation_rect = fixation_scaled.get_rect(center=screen_rect.center)
                                screen.blit(fixation_scaled, fixation_rect)
                            else:
                                contextual_fixation_scaled = get_scaled_stimulus(CONTEXTUAL_FIXATION, screen)
                                contextual_fixation_rect = contextual_fixation_scaled.get_rect(center=screen_rect.center)
                                screen.blit(contextual_fixation_scaled, contextual_fixation_rect)
                        else:
                            # Redraw stimulus
                            stimulus_scaled = get_scaled_stimulus(current_image, screen)
                            stimulus_rect = stimulus_scaled.get_rect(center=screen_rect.center)
                            screen.blit(stimulus_scaled, stimulus_rect)
                    
                    pygame.display.flip()
                    
                elif key_response is None and event.key in [pygame.K_d, pygame.K_k]:
                    # Only accept D and K keys as valid responses
                    key_response = event.key
                    reaction_time = pygame.time.get_ticks() - start_time
                    # Break immediately after getting a valid response
                    break
                # Ignore all other keys (no feedback, no action)
        
        # Break the outer loop if we got a response
        if key_response is not None:
            break
        
        # Small delay to prevent high CPU usage
        pygame.time.delay(1)

    pygame.event.clear()
    return key_response, reaction_time

# Read information from trials
def read_motor_trial(trial):
    fixation_time, stimulus_image, phase = trial
    if stimulus_image == BLUE:
        key_correct = pygame.K_d
        type = "actual"
    elif stimulus_image == RED:
        key_correct = pygame.K_k
        type = "actual"
    elif stimulus_image == NOGO:
        key_correct = None
        type = "no_go"
    return fixation_time, stimulus_image, type, phase, key_correct

# Run trials
def run_trials(trials, response_time, isi_time, condition, read_trial, screen):
    total_trials = 0
    correct_count = 0
    results = []

    for trial in trials:
        print(f"=== STARTING TRIAL - Participant ID: {GetParticipantId()} ===")
        startTime = datetime.now().strftime("%y/%m/%d %H:%M:%S")

        fixation_time, stimulus_image, type, phase, key_correct = read_trial(trial)

        # Fixation - centered on screen with appropriate scaling
        screen_rect = screen.get_rect()
        if (condition == "motor"
            or condition == "sensorimotor"):
            fixation_scaled = get_scaled_stimulus(FIXATION, screen)
            fixation_rect = fixation_scaled.get_rect(center=screen_rect.center)
            screen.blit(fixation_scaled, fixation_rect)
            pygame.display.flip()
            fixation_key_response, fixation_reaction_time = key_logging(fixation_time, screen, FIXATION, True, condition)
        else:
            contextual_fixation_scaled = get_scaled_stimulus(CONTEXTUAL_FIXATION, screen)
            contextual_fixation_rect = contextual_fixation_scaled.get_rect(center=screen_rect.center)
            screen.blit(contextual_fixation_scaled, contextual_fixation_rect)
            pygame.display.flip()
            fixation_key_response, fixation_reaction_time = key_logging(fixation_time, screen, CONTEXTUAL_FIXATION, True, condition)

        # Stimulus - centered on screen with appropriate scaling
        screen.fill(GRAY_RGB)  # Clear screen before showing stimulus
        stimulus_scaled = get_scaled_stimulus(stimulus_image, screen)
        stimulus_rect = stimulus_scaled.get_rect(center=screen_rect.center)
        screen.blit(stimulus_scaled, stimulus_rect)
        pygame.display.flip()
        stimulus_key_response, stimulus_reaction_time = key_logging(response_time, screen, stimulus_image, False, condition)

        if phase.startswith("practice"):
            if type == "no_go":
                correct = 1 if (fixation_key_response is None and stimulus_key_response is None) else 0
                timeout = False
            else:
                correct = 1 if (stimulus_key_response == key_correct) else 0
                timeout = (fixation_key_response is None and stimulus_key_response is None)
            show_feedback(screen, correct, timeout, stimulus_image)

        # ISI
        screen.fill(GRAY_RGB)
        pygame.display.flip()
        isi_key_response, isi_reaction_time = key_logging(isi_time, screen, None, False, condition)

        # Determine error type
        error_type = None
        if stimulus_key_response != key_correct:
            if type == "no_go":
                if stimulus_key_response is not None:
                    error_type = "no_go_error"
                elif isi_key_response is not None:
                    error_type = "no_go_delay_error"
            else:
                if stimulus_key_response is None:
                    if isi_key_response is not None:
                        error_type = "delay_error"
                    else:
                        error_type = "no_response"

        avg_fixation_time = (
            M_AVG_FIXATION_TIME if condition == "motor"
            else C_AVG_FIXATION_TIME if condition == "contextual"
            else SM_AVG_FIXATION_TIME  # fallback
        )
        correct = 1 if (error_type is None) else 0

        endTime = datetime.now().strftime("%y/%m/%d %H:%M:%S")

        partResult = {
            "block": phase,
            "type": type,
            "fixation_time": fixation_time,
            "condition": condition,
            "difficulty": abs(fixation_time - avg_fixation_time),
            "key_correct": key_correct,
            "fixation_key_response": fixation_key_response,
            "fixation_reaction_time_ms": fixation_reaction_time,
            "stimulus_key_response": stimulus_key_response,
            "stimulus_reaction_time_ms": stimulus_reaction_time,
            "isi_key_response": isi_key_response,
            "isi_reaction_time_ms": isi_reaction_time,
            "correct": correct,
            "error_type": error_type
        }
        print("=== TRIAL COMPLETE - SAVING DATA ===")
        print("record part result, participateID=", GetParticipantId())
        print("Trial data:", partResult)
        print("Start time:", startTime, "End time:", endTime)
        try:
            SaveResultsToCsv("results.csv", GetParticipantId(), partResult, startTime, endTime)
            print("=== DATA SAVED SUCCESSFULLY ===")
        except Exception as e:
            print("=== ERROR SAVING DATA ===")
            print("Error:", str(e))
            import traceback
            traceback.print_exc()

        total_trials += 1
        if correct:
            correct_count += 1

    accuracy = correct_count / total_trials
    return results, accuracy

def practice1_1(screen):
    return run_trials(practice1_1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def practice1_2(screen):
    return run_trials(practice1_2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def block1(screen):
    return run_trials(block1_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

def block2(screen):
    return run_trials(block2_trials, M_RESPONSE_TIME, M_ISI_TIME, "motor", read_motor_trial, screen)

# Segment 1 practice 1-1 + practice 1-2
def run_m_segment1(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(0, PRACTICE1_2_PAGE):            
        if i == PRACTICE1_1_PAGE - 1:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))
            instruction_flow.append(("practice", practice1_1))
        elif i == PRACTICE1_2_PAGE - 1:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))
            instruction_flow.append(("practice", practice1_2))
        else:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))

    run_instruction_flow(screen, instruction_flow, all_results, all_acc, next_segment_func)

# Segment 3 block 1
def run_m_segment3(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(PRACTICE1_2_PAGE, BLOCK1_PAGE):
        if i == BLOCK1_PAGE - 1:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))
            instruction_flow.append(("block", block1))
        else:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))

    run_instruction_flow(screen, instruction_flow, all_results, all_acc, next_segment_func)

# Segment 5 block 2
def run_m_segment5(screen, all_results, all_acc, next_segment_func):
    instruction_flow = []
    for i in range(BLOCK1_PAGE, BLOCK2_PAGE):
        if i == BLOCK2_PAGE - 1:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))
            instruction_flow.append(("block", block2))
        else:
            instruction_flow.append(("instruction", M_ALL_INSTRUCTIONS[i]))

    run_instruction_flow(screen, instruction_flow, all_results, all_acc, next_segment_func)
