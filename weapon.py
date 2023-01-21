from time import *
import pygame

pygame.init()
TEXT_COLOR = (3, 112, 207)


class Weapon:   # класс оружия
    def __init__(self, bullets, magazine, cooldown, reload_time):
        self.magazine = magazine    # объём магазина
        self.bullets = min(self.magazine, bullets)  # кол-во патронов
        self.font = pygame.font.Font('assets/pixeboy.ttf', 70)  # шрифт надписи кол-ва патронов в левом верхнем углу

        self.cooldown = cooldown    # время между выстрелами
        self.reload_time = reload_time  # время перезарядки

        self.timer_start = time()   # таймер для стрельбы
        self.reload_timer = time() - self.reload_time   # таймер для перезарядки

    def shoot(self):
        if self.bullets:
            # если таймер для стрельбы и перезарядки вышел
            if time() - self.reload_timer >= self.reload_time and time() - self.timer_start >= self.cooldown:
                self.bullets -= 1

                self.timer_start = time()

                return True
        else:
            self.bullets = self.magazine
            self.reload_timer = time()

    def draw(self, screen):
        amo_label = self.font.render(str(self.bullets), True, TEXT_COLOR)
        screen.blit(amo_label, (10, 10))
