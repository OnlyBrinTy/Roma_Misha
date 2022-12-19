import pygame


class Texture:
    def __init__(self, pos, img_source):
        self.image = pygame.image.load(f'assets/{img_source}').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
