import pygame


class TrialConditions:
    def __init__(self, image_path, mirrored):
        """
        Initialize a trial condition with image and mirrored status.
        :param image_path: Path to the image file
        :param mirrored: Boolean indicating whether the image is mirrored
        """
        try:
            # Load the image
            image = pygame.image.load(image_path)
            # Scale the image to 400x400
            scaled_image = pygame.transform.scale(image, (400, 400))

            # Save attributes
            self.file_path = image_path
            self.image = scaled_image
            self.mirrored = mirrored
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
