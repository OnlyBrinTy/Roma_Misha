from math import degrees
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
        self.speed = 5

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed


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
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()
        self.player = Player((0, 0), self.camera)
        self.textures = [Texture((0, 0), 'ground.png'), self.player]

        clock = pygame.time.Clock()
        quarters = {(True, True): 0, (False, True): 1, (False, False): 2, (True, False): 3}

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pass
                elif event.type == pygame.MOUSEMOTION:
                    x_dist, y_dist = event.pos - pygame.Vector2(self.player.rect.center - self.camera.offset)
                    if x_dist == 0 or y_dist == 0:
                        add_angle = 0
                    else:
                        add_angle = degrees(abs(x_dist / y_dist))

                    angle = add_angle + 90 * quarters[(x_dist >= 0, y_dist > 0)]

                    self.player.set_angle(angle)

            self.camera.update()
            self.camera.draw(self.textures, self.screen)

            clock.tick(FPS)


Game()