from time import *
import pygame

pygame.init()
TEXT_COLOR = (3, 112, 207)


class Weapon:
    def __init__(self, bullets, magazine, cooldown, reload_time):
        self.magazine = magazine
        self.bullets = min(self.magazine, bullets)
        self.font = pygame.font.Font('assets/pixeboy.ttf', 70)

        self.cooldown = cooldown
        self.reload_time = reload_time

        self.timer_start = time()
        self.reload_timer = time() - self.reload_time

    def shoot(self):
        if self.bullets:
            if time() - self.reload_timer >= self.reload_time and time() - self.timer_start >= self.cooldown:
                self.bullets -= 1

                self.timer_start = time()

                return True
        else:
            self.bullets = self.magazine
            self.reload_timer = time()

            return False

    def draw(self, screen):
        amo_label = self.font.render(str(self.bullets), True, TEXT_COLOR)
        screen.blit(amo_label, (10, 10))
