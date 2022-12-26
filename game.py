from threading import Thread
from math import atan, degrees
from texture import Texture
import weapon
import pygame

MAX_SPEED = 7
BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1600, 900
FPS = 120


class MovingThread(Thread):
    def __init__(self, *groups_to_update):
        super().__init__()

        self.groups_to_update = groups_to_update

    def run(self):
        while True:
            for group in self.groups_to_update:
                group.update()

            pygame.time.delay(25)


class Player(pygame.sprite.Sprite, Texture):  # Это спрайт для группы  camera
    def __init__(self, blit_pos, group):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, blit_pos, 'player.png')

        self.direction = pygame.math.Vector2()

    def input(self):
        def formula(x, y):
            return max(0.1, (abs(x) + abs(y)) ** 0.125)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = max(-MAX_SPEED, self.direction.y - formula(*self.direction))
        elif keys[pygame.K_s]:
            self.direction.y = min(MAX_SPEED, self.direction.y + formula(*self.direction))
        else:
            self.direction.y *= 0.7

        if keys[pygame.K_a]:
            self.direction.x = max(-MAX_SPEED, self.direction.x - formula(*self.direction))
        elif keys[pygame.K_d]:
            self.direction.x = min(MAX_SPEED, self.direction.x + formula(*self.direction))
        else:
            self.direction.x *= 0.7

    def update(self):
        self.input()

        self.rect.center += self.direction
        self.blit_pos += self.direction


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):
        self.offset.x = self.sprite.rect.center[0] - WIDTH // 2
        self.offset.y = self.sprite.rect.center[1] - HEIGHT // 2

    def draw(self, textures, screen):
        self.camera_centering()

        screen.fill(BACKGROUND_COLOR)

        for texture in textures:
            display_position = texture.blit_pos - self.offset
            screen.blit(texture.image, display_position)

        pygame.display.update()


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()
        self.player = Player((WIDTH // 2, HEIGHT // 2), self.camera)
        self.textures = [Texture((0, 0), 'ground.png'), self.player]

        self.thread = MovingThread(self.camera)
        self.thread.start()
        weap = weapon.BulletAmount()

        clock = pygame.time.Clock()
        running = True

        while running:
            self.camera.draw(self.textures, self.screen)

            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.screen.blit(weap.get_bullet(), (100, 100))
                elif event.type == pygame.MOUSEMOTION:
                    self.player.set_angle(self.check_angle(event.pos))

            pygame.display.update()

    def check_angle(self, mouse_pos):
        quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

        x_dist, y_dist = mouse_pos - pygame.Vector2(self.player.rect.center - self.camera.offset)
        quart_num = quarters[(x_dist > 0, y_dist > 0)]

        if x_dist == 0 or y_dist == 0:
            add_angle = 0

            if x_dist == 0:
                if y_dist > 0:
                    quart_num = 3
                else:
                    quart_num = 1
            else:
                if x_dist > 0:
                    quart_num = 0
                else:
                    quart_num = 2
        else:
            add_angle = degrees(atan(x_dist / y_dist))

            if quart_num in (0, 2):
                add_angle += 90

        return add_angle + 90 * quart_num
