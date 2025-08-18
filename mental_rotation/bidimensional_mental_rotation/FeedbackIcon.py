import pygame
import os

class FeedbackIcon:
    def __init__(self):
        """
        Load feedback icons for correct, incorrect, and timeout outcomes.
        """
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize default values
        self.correct_icon = None
        self.incorrect_icon = None
        self.timeout_icon = None
        
        try:
            # Define icon paths (using absolute paths)
            correct_icon_path = os.path.join(script_dir, "stimuli", "feedback_icons", "Correct.png")
            incorrect_icon_path = os.path.join(script_dir, "stimuli", "feedback_icons", "Incorrect.png")
            timeout_icon_path = os.path.join(script_dir, "stimuli", "feedback_icons", "Timeout.jpg")

            # Load and scale images
            if os.path.exists(correct_icon_path):
                correct_image = pygame.image.load(correct_icon_path)
                self.correct_icon = pygame.transform.scale(correct_image, (102, 102))  # Use same size as action_prediction
            else:
                print(f"Warning: Correct icon not found at {correct_icon_path}")

            if os.path.exists(incorrect_icon_path):
                incorrect_image = pygame.image.load(incorrect_icon_path)
                self.incorrect_icon = pygame.transform.scale(incorrect_image, (102, 102))  # Use same size as action_prediction
            else:
                print(f"Warning: Incorrect icon not found at {incorrect_icon_path}")

            if os.path.exists(timeout_icon_path):
                timeout_image = pygame.image.load(timeout_icon_path)
                self.timeout_icon = pygame.transform.scale(timeout_image, (102, 102))  # Use same size as action_prediction
            else:
                print(f"Warning: Timeout icon not found at {timeout_icon_path}")

            # Create fallback icons if original icons couldn't be loaded
            if self.correct_icon is None:
                self.correct_icon = self._create_fallback_icon((0, 255, 0), "✓")  # Green checkmark
            if self.incorrect_icon is None:
                self.incorrect_icon = self._create_fallback_icon((255, 0, 0), "✗")  # Red X
            if self.timeout_icon is None:
                self.timeout_icon = self._create_fallback_icon((255, 255, 0), "!")  # Yellow exclamation

        except Exception as e:
            print(f"Error loading feedback icons: {e}")
            # Create fallback icons
            self.correct_icon = self._create_fallback_icon((0, 255, 0), "✓")
            self.incorrect_icon = self._create_fallback_icon((255, 0, 0), "✗")
            self.timeout_icon = self._create_fallback_icon((255, 255, 0), "!")

    def _create_fallback_icon(self, color, text):
        """Create a simple fallback icon with colored background and text."""
        icon = pygame.Surface((102, 102))
        icon.fill(color)
        
        # Add text to the icon
        font = pygame.font.SysFont(None, 72)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(51, 51))
        icon.blit(text_surface, text_rect)
        
        return icon
