from entities import *
from math import *
from map import *
from random import *
import pygame

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
CELL_SIZE = pygame.image.load('assets/walls/wall_0.png').get_size()[0]
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
            for sprite in group.sprites():
                screen.blit(sprite.image, sprite.rect.topleft - self.offset)

            i += 1

        for texture in interface:
            screen.blit(texture.image, texture.blit_pos)

        pygame.display.update()


class Game:
    def __init__(self, new_game):
        pygame.init()

        self.level, self.rewards, self.player_bullets, \
            self.enemy_bullets, self.player_pos, self.enemy_pos, self.enemy_amount = self.start_game(new_game)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)
        self.camera = Camera()  # через камеру происходит отображение всего на экране
        self.entities = pygame.sprite.Group()  # все движущиеся существа в игре (даже пули)
        self.map = Map(self.level)
        self.player = Player((self.player_pos[0], self.player_pos[1]),
                             'assets/player.png', (self.entities, self.camera), self.player_bullets)
        for i in range(self.enemy_amount):
            pos_x, pos_y = self.enemy_pos[randint(1, 5)]
            self.enemy = Enemy((CELL_SIZE * pos_x, CELL_SIZE * pos_y), 'assets/scientist.png', self.entities, self.enemy_bullets, self.enemy_amount)
        # в interface лежат текстуры, которые будут затем выводится на экран без учёта сдвига
        self.interface = []
        # В interface лежат текстуры, которые будут затем выводится на экран
        # они лежат в порядке отображения. Сначала рисуем землю и поверх неё рисуем игрока

        self.thread = EntityThread(self.map, self.entities)
        self.thread.start()

        clock = pygame.time.Clock()
        running = True

        while running:
            self.thread.update_groups.set()  # делаем запрос на обновление персонажа (устанавливаем флажок на True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.save_game('test_level.txt', 'rewards', 10, 1000,
                                   self.player.rect.center, self.enemy.rect.center, self.enemy_amount)
                    self.thread.terminated.set()
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.player.finite_angle = self.check_angle(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.to_shoot = True

            while self.thread.update_groups.is_set():  # ждём пока персонаж не обработает своё положение
                pass

            self.camera.draw((self.map, self.entities), self.interface, self.screen)

            clock.tick(FPS)

    def check_angle(self, point_pos):  # определение угла поворота в зависимости от положения мыши
        quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

        x_dist, y_dist = point_pos - pygame.Vector2(self.player.add_rect.center - self.camera.offset)
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

    @staticmethod
    def save_game(current_level, rewards, bullet_amount, enemy_bullets_amount, player_pos, enemy_pos, enemy_amount):
        with open('progress/progress.txt', mode='w', encoding='utf-8') as pg_file:
            pg_file.write(current_level + '\n')
            pg_file.write(rewards + '\n')
            pg_file.write(str(bullet_amount) + '\n')
            pg_file.write(str(enemy_bullets_amount) + '\n')
            pg_file.write(f'{player_pos[0]} {player_pos[1]}' + '\n')
            pg_file.write(f'{enemy_pos[0]} {enemy_pos[1]}' + '\n')
            pg_file.write(str(enemy_amount))
        pg_file.close()


    def start_game(self, new_game):
        if new_game:
            with open('progress/start_file.txt', mode='r', encoding='utf-8') as pg_file:
                level, rewards, player_bullets, enemy_bullets, player_pos, enemy_amount = pg_file.readlines()
        else:
            with open('progress/progress.txt', mode='r', encoding='utf-8') as pg_file:
                level, rewards, player_bullets, enemy_bullets, player_pos, enemy_amount = pg_file.readlines()
        pg_file.close()
        level = level[:-1]
        player_bullets = int(player_bullets)
        enemy_bullets = int(enemy_bullets)
        player_pos = list(map(int, player_pos.split()))
        enemy_amount = int(enemy_amount)
        enemy_pos = []
        with open(f'maps/{level}', mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            x_ind = 0
            for y in lines[1:-1]:
                for x in y[1:-1]:
                    x_ind += 1
                    if x == '0':
                        enemy_pos.append((x_ind, lines.index(y)))
        return level, rewards, player_bullets, enemy_bullets, player_pos, enemy_pos, enemy_amount
