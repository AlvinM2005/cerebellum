import pygame


class Instruction:
    def __init__(self, image_path):
        """
        Initialize an instruction page with its image.
        :param image_path: Path to the instruction image file
        """
        try:
            # Load the instruction image
            image = pygame.image.load(image_path)
            # Scale the image to 1515x851 to match Java version
            scaled_image = pygame.transform.scale(image, (1515, 851))

            # Save attributes
            self.file_path = image_path
            self.image = scaled_image
        except Exception as e:
            print(f"Error loading instruction image {image_path}: {e}")
            # Create a fallback image with error message
            self.image = pygame.Surface((1515, 851))
            self.image.fill((50, 50, 50))  # Dark gray background
            
            # Add error text
            font = pygame.font.SysFont(None, 48)
            error_text = font.render(f"Error loading: {image_path}", True, (255, 255, 255))
            text_rect = error_text.get_rect(center=(1515//2, 851//2))
            self.image.blit(error_text, text_rect)
            
            self.file_path = image_path
