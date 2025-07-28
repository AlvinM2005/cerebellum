import pygame
import os

class FeedbackIcon:
    def __init__(self):
        """
        Load feedback icons for correct, incorrect, and timeout outcomes.
        """
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Define icon paths using absolute paths
            correct_icon_path = os.path.join(script_dir, "stimuli", "feedback_icons", "Correct.jpg")
            incorrect_icon_path = os.path.join(script_dir, "stimuli", "feedback_icons", "Incorrect.jpg")
            timeout_icon_path = os.path.join(script_dir, "stimuli", "feedback_icons", "Timeout.jpg")

            # Load and scale images
            correct_image = pygame.image.load(correct_icon_path)
            self.correct_icon = pygame.transform.scale(correct_image, (200, 200))

            incorrect_image = pygame.image.load(incorrect_icon_path)
            self.incorrect_icon = pygame.transform.scale(incorrect_image, (200, 200))

            timeout_image = pygame.image.load(timeout_icon_path)
            self.timeout_icon = pygame.transform.scale(timeout_image, (200, 200))

        except Exception as e:
            print(f"Error loading feedback icons: {e}")
            print("Using colored rectangles as fallback...")
            
            # Create fallback colored rectangles
            self.correct_icon = pygame.Surface((200, 200))
            self.correct_icon.fill((0, 255, 0))  # Green for correct
            
            self.incorrect_icon = pygame.Surface((200, 200))
            self.incorrect_icon.fill((255, 0, 0))  # Red for incorrect
            
            self.timeout_icon = pygame.Surface((200, 200))
            self.timeout_icon.fill((255, 255, 0))  # Yellow for timeout
