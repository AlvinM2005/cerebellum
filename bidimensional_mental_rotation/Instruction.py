import pygame


class Instruction:
    def __init__(self, image_path):
        """
        Initialize an instruction page with its image.
        :param image_path: Path to the instruction image file
        """
        self.file_path = image_path
        self.image = None  # Initialize image as None
        
        try:
            # Load the instruction image
            image = pygame.image.load(image_path)
            # Scale the image to 1515x851 to match Java version
            scaled_image = pygame.transform.scale(image, (1515, 851))
            self.image = scaled_image
        except Exception as e:
            print(f"Error loading instruction image {image_path}: {e}")
            # Create a simple error surface with text
            error_surface = pygame.Surface((1515, 851))
            error_surface.fill((128, 128, 128))  # Gray background
            font = pygame.font.SysFont(None, 48)
            text = font.render(f"Error loading: {image_path}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(1515//2, 851//2))
            error_surface.blit(text, text_rect)
            self.image = error_surface
