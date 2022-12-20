from math import atan, degrees
from texture import Texture
import pygame
import os

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
FPS = 60


class Player(pygame.sprite.Sprite, Texture):    # Это спрайт для группы  camera
    def __init__(self, pos, group):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, pos, 'player.png')

        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.math.Vector2()
        self.speed_x = 0
        self.speed_y = 0
        self.result_speed = 0
        self.max_speed = 4

    def input(self):
        keys = pygame.key.get_pressed()
        self.result_speed = 0

        if keys[pygame.K_a] and self.direction.x != 1:
            if self.speed_x < self.max_speed:
                self.speed_x += 0.1
            self.direction.x = -1
        elif keys[pygame.K_d] and self.direction.x != -1:
            if self.speed_x < self.max_speed:
                self.speed_x += 0.1
            self.direction.x = 1
        elif self.speed_x > 0:
            self.speed_x -= 0.2
        elif self.speed_x < 0:
            self.speed_x = 0
        elif self.speed_x == 0:
            self.direction.x = 0

        if keys[pygame.K_w] and self.direction.y != 1:
            if self.speed_y < self.max_speed:
                self.speed_y += 0.2
            self.direction.y = -1
        elif keys[pygame.K_s] and self.direction.y != -1:
            if self.speed_y < self.max_speed:
                self.speed_y += 0.2
            self.direction.y = 1
        elif self.speed_y > 0:
            self.speed_y -= 0.2
        elif self.speed_y < 0:
            self.speed_y = 0
        elif self.speed_y == 0:
            self.direction.y = 0

        self.result_speed = int(max(self.speed_x, self.speed_y))

    def update(self):
        self.input()
        self.rect.center += self.direction * self.result_speed


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):
        self.offset.x = self.sprite.rect.centerx - WIDTH // 2
        self.offset.y = self.sprite.rect.centery - HEIGHT // 2

    def draw(self, textures, screen):
        self.camera_centering()

        screen.fill(BACKGROUND_COLOR)

        for texture in textures:
            display_position = texture.rect.topleft - self.offset
            screen.blit(texture.image, display_position)

        pygame.display.update()


class Game:
    def __init__(self):
        running = True
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()
        self.player = Player((WIDTH // 2, HEIGHT // 2), self.camera)
        self.textures = [Texture((0, 0), 'ground.png'), self.player]

        clock = pygame.time.Clock()
        quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pass
                elif event.type == pygame.MOUSEMOTION:
                    x_dist, y_dist = event.pos - pygame.Vector2(self.player.rect.center - self.camera.offset)

                    quart_num = quarters[(x_dist >= 0, y_dist >= 0)]
                    if x_dist == 0 or y_dist == 0:
                        add_angle = 0
                    else:
                        add_angle = degrees(atan(x_dist / y_dist))

                        if quart_num in (0, 2):
                            add_angle += 90

                    angle = add_angle + 90 * quart_num

                    self.player.set_angle(angle)

            self.camera.update()
            self.camera.draw(self.textures, self.screen)

            clock.tick(FPS)
