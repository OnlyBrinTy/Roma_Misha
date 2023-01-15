from time import *
import pygame

pygame.init()
TEXT_COLOR = (3, 112, 207)


class Weapon:
    def __init__(self, bullets):
        self.bullets = bullets
        self.font = pygame.font.Font('assets/pixeboy.ttf', 35)
        self.timer_start = time()
        self.cooldown = 0.3

    def shoot(self):
        if self.bullets and time() - self.timer_start >= self.cooldown:
            self.bullets -= 1

            self.timer_start = time()

            return True

    def draw(self, screen):
        amo_label = self.font.render(str(self.bullets), True, TEXT_COLOR)
        screen.blit(amo_label, (10, 10))


class CurrentWeapon:
    pass
