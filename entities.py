from threading import Thread, Event
from texture import Texture
from time import time
import pygame

MAX_SPEED = 10


class Entities(pygame.sprite.Sprite, Texture):
    def __init__(self, blit_pos, file_name, groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        Texture.__init__(self, blit_pos, pygame.image.load(file_name))

    def update(self, delay):
        slowdown = delay / 0.025
        self.motion(slowdown)

        real_direction = self.vectors.direction * slowdown
        self.rect.center += real_direction
        self.blit_pos += real_direction


class Player(Entities):  # Это спрайт для групп camera и entities
    def __init__(self, blit_pos, file_name, groups):
        self.vectors = Vectors()
        Entities.__init__(self, blit_pos, file_name, groups)

    def motion(self, slowdown):
        def formula(speed, depth):
            curr_increase = 2 / 1.15 ** speed

            if depth:
                return curr_increase + formula(speed + curr_increase, depth - 1)

            return curr_increase * (slowdown % 1)

        keys = pygame.key.get_pressed()
        w, a, s, d = keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d]

        boost = formula(sum(self.vectors.velocity), int(slowdown))

        self.vectors.direction += boost * (bool(d) - bool(a)), boost * (bool(s) - bool(w))

        if w == s and a == d and self.vectors.velocity:
            fractions = pygame.Vector2(self.vectors.velocity / sum(self.vectors.velocity))

            self.vectors.velocity -= tuple(map(min, zip(self.vectors.velocity, fractions * boost)))
        elif w == s:
            self.vectors.velocity -= 0, min(self.vectors.velocity.y, boost)
        elif a == d:
            self.vectors.velocity -= min(self.vectors.velocity.x, boost), 0

        if sum(self.vectors.velocity) > MAX_SPEED:
            overload = sum(self.vectors.velocity) - MAX_SPEED

            if w != s and a != d:
                self.vectors.velocity -= self.vectors.velocity / sum(self.vectors.velocity) * overload
            else:
                self.vectors.velocity -= overload * bool(w == s), overload * bool(a == d)


class AnotherThread(Thread):
    def __init__(self, *groups_to_update):
        super().__init__()

        self.groups_to_update = groups_to_update
        self.update_groups = Event()

    def run(self):
        start = time()

        while True:
            if self.update_groups.is_set():
                delay = time() - start
                start = time()

                for group in self.groups_to_update:
                    group.update(delay)

                self.update_groups.clear()


class Vectors:
    direction = pygame.Vector2()

    @property
    def velocity(self):
        return pygame.Vector2(*map(abs, self.direction))

    @velocity.setter
    def velocity(self, value):
        direction_mask = pygame.Vector2(*map(lambda x: bool(x >= 0) * 2 - 1, self.direction))

        self.direction = direction_mask.elementwise() * value
