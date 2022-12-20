from texture import Texture
import pygame
import os

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
FPS = 60


class Player(pygame.sprite.Sprite, Texture):
    def __init__(self, pos, group):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, pos, 'player.png')

        self.direction = pygame.math.Vector2()
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed = 8

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and self.direction.y != 1:
            if self.speed_y < self.max_speed:
                self.speed_y += 1
            self.direction.y = -1
        elif keys[pygame.K_s] and self.direction.y != -1:
            if self.speed_y < self.max_speed:
                self.speed_y += 1
            self.direction.y = 1
        elif self.speed_y > 0:
            self.speed_y -= 2
        elif self.speed_y < 0:
            self.speed_y = 0
        elif self.speed_y == 0:
            self.direction.y = 0

        if keys[pygame.K_a] and self.direction.x != 1:
            if self.speed_x < self.max_speed:
                self.speed_x += 1
            self.direction.x = -1
        elif keys[pygame.K_d] and self.direction.x != -1:
            if self.speed_x < self.max_speed:
                self.speed_x += 1
            self.direction.x = 1
        elif self.speed_x > 0:
            self.speed_x -= 2
        elif self.speed_x < 0:
            self.speed_x = 0
        elif self.speed_x == 0:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed_y


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):
        self.offset.x = self.sprite.rect.centerx - WIDTH // 2
        self.offset.y = self.sprite.rect.centery - WIDTH // 2

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
        clock = pygame.time.Clock()

        self.camera = Camera()
        self.player = Player((WIDTH // 2, HEIGHT // 2), self.camera)
        self.textures = [Texture((0, 0), 'ground.png'), self.player]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pass

            self.camera.update()
            self.camera.draw(self.textures, self.screen)

            clock.tick(FPS)
