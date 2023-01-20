from entities import Player, Enemy
from windows import PauseWindow
from interface import Cursor, HpLabel
from math import atan, degrees
from map import Map
from time import time
import pygame

BACKGROUND_COLOR = (33, 33, 33)
GAME_NAME = 'Hotline Fortress'
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
INITIAL_ZOOM = 3
LAST_LEVEL = 3
FPS = 60


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()
    s_inset = pygame.Vector2()
    zoom = INITIAL_ZOOM
    display_surface = pygame.Surface((WIDTH // zoom, HEIGHT // zoom))

    def update_display_surface(self, new_zoom):
        self.zoom = min(4, max(2, self.zoom + new_zoom))
        self.display_surface = pygame.Surface((WIDTH // self.zoom, HEIGHT // self.zoom))

    def camera_centering(self):  # установка сдвига камеры так, чтобы игрок оказался по центру
        self.s_inset.x = self.sprite.add_rect.center[0] - WIDTH // 2
        self.s_inset.y = self.sprite.add_rect.center[1] - HEIGHT // 2

        self.offset.x = self.sprite.add_rect.center[0] - WIDTH // (2 * self.zoom)
        self.offset.y = self.sprite.add_rect.center[1] - HEIGHT // (2 * self.zoom)

    def draw(self, groups, interface, screen):
        self.camera_centering()

        self.display_surface.fill(BACKGROUND_COLOR)

        for group in groups:  # каждый спрайт выводится на экран друг за другом с учётом сдвига камеры
            for sprite in group.sprites():
                self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)

        # точки куда движутся противники (можно удалить)
        # try:
        #     for enemy in groups[1].sprites()[1:4]:
        #         if any(enemy.target_point):
        #             pygame.draw.circle(self.display_surface, 'red', enemy.target_point - self.offset, 10)
        #         if any(enemy.current_target):
        #             pygame.draw.circle(self.display_surface, 'green', enemy.current_target - self.offset, 10)
        # except AttributeError:
        #     pass

        pygame.transform.scale(self.display_surface, (WIDTH, HEIGHT), screen)

        for element in interface:
            element.draw(screen)

        pygame.display.update()


class Game:
    # new_game - новая ли игра, difficulty - сложность от 1 до 3, level - номер уровня, score - накопленные очки
    def start(self, new_game, difficulty=None, level=None, score=0):
        pygame.init()

        pygame.display.set_caption(GAME_NAME)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN, vsync=True)

        label_surf = pygame.font.Font('assets/pixeboy.ttf', 90).render('Loading...', True, 'white')
        self.screen.blit(label_surf, label_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.update()

        self.level, self.difficulty, self.saves_left, player_init, enemies_init = load_game(new_game, level, difficulty)

        self.camera = Camera()  # через камеру происходит отображение всего на экране
        self.entities = pygame.sprite.Group()  # все движущиеся существа в игре (даже пули)
        self.map = Map(self.level)  # создаём карту уровня
        shape_adjust = pygame.Vector2((self.map.cell_size / 2,) * 2)
        self.player = Player(*player_init, 'assets/player.png', (self.entities, self.camera))
        self.enemies = [Enemy(*init, 'assets/enemy.png', shape_adjust, (self.entities,)) for init in enemies_init]
        # эти классы отображаются без учёта сдвига камеры
        self.interface = [self.player.weapon, Cursor(), HpLabel(self.player)]
        self.timer_start = time() - 1 / FPS

        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # сохраняем игру перед выходом
                    self.save_game()
                    exit()
                elif event.type == pygame.MOUSEMOTION and not self.player.animations_state['death']:
                    self.player.finite_angle = check_angle(self.player.add_rect.center, event.pos + self.camera.s_inset)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.to_shoot = True
                if event.type == pygame.MOUSEWHEEL:
                    self.camera.update_display_surface(event.y / 10)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    PauseWindow(self)
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN, vsync=True)
                    self.timer_start = time() - 1 / FPS

            self.update_entities()

            if not self.player.alive():
                pygame.display.quit()
                return 'You died!', score
            elif not self.enemies:
                pygame.display.quit()
                next_level = int(self.level[6]) + 1
                if next_level <= 3:
                    return Game().start(True, difficulty, next_level, score + self.player.hp)

                return 'Congratulations!', score + self.player.hp

            self.camera.draw((self.map, self.entities), self.interface, self.screen)

            clock.tick(FPS)

    def update_entities(self):
        for enemy in self.enemies:
            if enemy.alive():
                if not enemy.animations_state['death']:  # задаём противникам направление и угол разворота
                    enemy.check_the_player(self.map.wall_shape, self.player.add_rect.center)
                    if enemy.see_player:
                        enemy.finite_angle = check_angle(enemy.add_rect.center, self.player.add_rect.center)
                        enemy.to_shoot = abs(enemy.angle - enemy.finite_angle) < 5
                    elif not any(enemy.target_point):
                        enemy.find_random_route(self.map.wall_shape)
            else:
                self.enemies.remove(enemy)

        delay = time() - self.timer_start
        self.timer_start = time()

        self.entities.update(delay, self.map)

    def save_game(self):  # запись прогресса в файл
        if self.saves_left:
            p_init = self.player.rect.center, self.player.weapon.bullets, self.player.hp
            enemies = []
            for enemy in self.enemies:
                enemies.append((enemy.rect.center, enemy.weapon.bullets, enemy.hp, enemy.max_speed))

            with open('progress/progress.txt', mode='w', encoding='utf-8') as pg_file:
                pg_file.write(self.level + '\n')     # запись названия уровня
                pg_file.write(str(self.difficulty) + '\n')   # запись уровня сложности
                pg_file.write(str(self.saves_left - 1) + '\n')
                pg_file.write(' '.join(map(str, (p_init[0][0], p_init[0][1], p_init[1], p_init[2]))) + '\n')
                # запись игрока (координаты, кол-во патронов, кол-во жизней)
                pg_file.write('|'.join(map(lambda t: ' '.join(map(str, (t[0][0], t[0][1], t[1], t[2], t[3]))), enemies)))
                # запись уровня сложности
                pg_file.close()

        self.saves_left = max(0, self.saves_left - 1)


def load_game(new_game, level, difficulty=None):   # считывание прогресса из файла
    if new_game:    # это новая игра
        with open(f'progress/level_{level}_info.txt', mode='r') as file:
            level, player, enemies = tuple(map(lambda s: s.replace('\n', ''), file.readlines()))

        saves_left = 6 // difficulty
    else:   # продолжили игру
        with open('progress/progress.txt', mode='r') as file:
            level, difficulty, saves_left, player, enemies = tuple(map(lambda s: s.replace('\n', ''), file.readlines()))

    file.close()
    p_x, p_y, p_bullets, p_hp = tuple(map(int, player.split()))
    enemies = list(map(lambda s: tuple(map(int, s.split())), enemies.split('|')))

    for i, (x, y, bullets, hp, speed) in enumerate(enemies):
        enemies[i] = (x, y), bullets, hp * int(difficulty), speed + int(difficulty)

    return level, difficulty, int(saves_left), ((p_x, p_y), p_bullets, p_hp), enemies


def check_angle(entity_pos, point_pos):   # определение угла поворота в зависимости от положения мыши
    #   двумерная плоскость всегда делится на 4 части. Это проходится в школе
    quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

    x_dist, y_dist = point_pos - pygame.Vector2(entity_pos)  # расстояние от курсора до точки
    quart_num = quarters[(x_dist > 0, y_dist > 0)]  # вычисляем, в каком из 4 секторов лежит прямая

    if x_dist == 0 or y_dist == 0:  # при нулевых координатах нельзя высчитать сектор угла, так что определяем вручную
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
        add_angle = degrees(atan(x_dist / y_dist))  # считаем угол внутри сектора

        if quart_num in (0, 2):
            add_angle += 90

    return add_angle + 90 * quart_num   # итоговый угол
