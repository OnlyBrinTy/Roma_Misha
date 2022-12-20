import pygame


class Texture:
    def __init__(self, pos, img_source):
        self._original_image = self.image = pygame.image.load(f'assets/{img_source}').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

    def set_angle(self, angle):
        self.image = pygame.transform.rotate(self._original_image, angle)
