import pygame
from entities import *
from texture import Texture
from rectangle import *

pygame.init()
TEXT_COLOR = (3, 112, 207)


class Weapon:
    pass


class CurrentWeapon:
    pass


class Bullet(Entity):
    def __init__(self, start_pos, finish_pos, file_name, group, screen_size):
        self.MAX_SPEED = 50
        # bullets = pygame.sprite.Group()
        self.image = pygame.image.load(file_name)
        self.rect = self.image.get_rect(topleft=start_pos)
        self.final_pos = finish_pos[0] - screen_size[0] // 2, finish_pos[1] - screen_size[1] // 2
        self.velocity_x, self.velocity_y = self.final_pos[0] // 10, self.final_pos[1] // 10
        Entity.__init__(self, start_pos, file_name, group)

    def motion(self, slowdown):
        self.add_rect = Rect(self.rect)

    def get_final_pos(self):
        return self.final_pos


class BulletAmount:
    pass
