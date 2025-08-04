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
