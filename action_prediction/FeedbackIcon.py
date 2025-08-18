import pygame
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class FeedbackIcon:
    def __init__(self):
        """
        Load feedback icons for correct, incorrect, and timeout outcomes.
        """
        try:
            # Define icon paths
            correct_icon_path = os.path.join(SCRIPT_DIR, "stimuli", "feedback_icons", "Correct.png")
            incorrect_icon_path = os.path.join(SCRIPT_DIR, "stimuli", "feedback_icons", "Incorrect.png")
            timeout_icon_path = os.path.join(SCRIPT_DIR, "stimuli", "feedback_icons", "Timeout.jpg")

            # Load and scale images to same size as cognitive control (original size / 5)
            correct_image = pygame.image.load(correct_icon_path)
            self.correct_icon = pygame.transform.scale(correct_image, (
                correct_image.get_width() // 5,
                correct_image.get_height() // 5
            ))

            incorrect_image = pygame.image.load(incorrect_icon_path)
            self.incorrect_icon = pygame.transform.scale(incorrect_image, (
                incorrect_image.get_width() // 5,
                incorrect_image.get_height() // 5
            ))

            timeout_image = pygame.image.load(timeout_icon_path)
            self.timeout_icon = pygame.transform.scale(timeout_image, (
                timeout_image.get_width() // 5,
                timeout_image.get_height() // 5
            ))

        except Exception as e:
            print(f"Error loading feedback icons: {e}")
