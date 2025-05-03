import pygame

class FeedbackIcon:
    def __init__(self):
        """
        Load feedback icons for correct, incorrect, and timeout outcomes.
        """
        try:
            # Define icon paths
            correct_icon_path = "./stimuli/feedback_icons/Correct.jpg"
            incorrect_icon_path = "./stimuli/feedback_icons/Incorrect.jpg"
            timeout_icon_path = "./stimuli/feedback_icons/Timeout.jpg"

            # Load and scale images
            correct_image = pygame.image.load(correct_icon_path)
            self.correct_icon = pygame.transform.scale(correct_image, (200, 200))

            incorrect_image = pygame.image.load(incorrect_icon_path)
            self.incorrect_icon = pygame.transform.scale(incorrect_image, (200, 200))

            timeout_image = pygame.image.load(timeout_icon_path)
            self.timeout_icon = pygame.transform.scale(timeout_image, (200, 200))

        except Exception as e:
            print(f"Error loading feedback icons: {e}")
