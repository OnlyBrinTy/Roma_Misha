import pygame


class Texture:
    def __init__(self, blit_pos, img_source):
        self._original_image = self.image = pygame.image.load(f'assets/{img_source}').convert_alpha()
        self.rect = self.image.get_rect(topleft=blit_pos)
        self.blit_pos = blit_pos

    def set_angle(self, angle):
        self.image = pygame.transform.rotate(self._original_image, angle)
        half_w = self.image.get_width() // 2
        half_h = self.image.get_height() // 2

        self.blit_pos = self.rect.x - half_w + self.rect.width // 2, self.rect.y - half_h + self.rect.height // 2
