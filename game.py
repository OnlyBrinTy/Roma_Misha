from math import *
from map import *
from weapon import *
from button import *
from windows import *
import pygame

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
FPS = 120


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):  # установка сдвига камеры так, чтобы игрок оказался по центру
        self.offset.x = self.sprite.add_rect.center[0] - WIDTH // 2
        self.offset.y = self.sprite.add_rect.center[1] - HEIGHT // 2

    def draw(self, groups, interface, screen):
        self.camera_centering()

        screen.fill(BACKGROUND_COLOR)  # заливка фона
        i = 0
        for group in groups:  # каждый спрайт выводится на экран друг за другом с учётом сдвига камеры
            if i:
                for sprite in group.sprites():
                    if sprite.rect.topleft != tuple(map(int, sprite.add_rect.topleft + sprite.rect_correction)):
                        print(sprite.rect.topleft, tuple(map(int, sprite.add_rect.topleft + sprite.rect_correction)))

                    screen.blit(sprite.image, sprite.rect.topleft - self.offset)
            else:
                for sprite in group.sprites():
                    screen.blit(sprite.image, sprite.rect.topleft - self.offset)

            i += 1

        for texture in interface:
            screen.blit(texture.texture_image, texture.blit_pos)

        # olist = self.sprite.mask.outline()
        # pygame.draw.lines(screen, (200, 150, 150), 1, olist)

        pygame.display.update()


class Game:
    button_image = pygame.image.load('assets/button.png')

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()  # через камеру происходит отображение всего на экране
        self.entities = pygame.sprite.Group()
        self.map = Map('test_level.txt')

        self.player = Player((WIDTH // 2, HEIGHT // 2), 'assets/player.png', (self.camera, self.entities))
        self.interface = []
        # В interface лежат текстуры, которые будут затем выводится на экран
        # они лежат в порядке отображения. Сначала рисуем землю и поверх неё рисуем игрока

        self.thread = EntityThread(self.map, self.camera)
        self.thread.start()

        clock = pygame.time.Clock()
        running = True

        while running:
            self.thread.update_groups.set()  # делаем запрос на обновление персонажа

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    SaveGame('test_level.txt', 'rewardsффффф', '10')
                    self.thread.terminated.set()
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.player.set_angle(self.check_angle(event.pos))


            while self.thread.update_groups.is_set():  # ждём пока персонаж не обработает своё положение
                pass

            self.camera.draw((self.map, self.entities), self.interface, self.screen)

            clock.tick(FPS)


    def check_angle(self, mouse_pos):  # определение угла поворота в зависимости от положения мыши
        quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

        x_dist, y_dist = mouse_pos - pygame.Vector2(self.player.add_rect.center - self.camera.offset)
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


class SaveGame:
    def __init__(self, current_checkpoint, rewards, bullet_amount):
        self.checkpoint = current_checkpoint
        self.rewards = rewards
        self.bullet_amount = bullet_amount
        with open('Progress/progress.txt', mode='w', encoding='utf-8') as pg_file:
            pg_file.write(self.checkpoint + '\n')
            pg_file.write(self.rewards + '\n')
            pg_file.write(self.bullet_amount)
            pg_file.close()
