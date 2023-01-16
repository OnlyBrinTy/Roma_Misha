from entities import EntityThread, Player, Enemy
from math import atan, degrees
from map import Map
import pygame

WIDTH, HEIGHT = 1280, 720
ENEMIES_POSITION = {'test': ((40 * 50, 30 * 50), (40 * 50, 35 * 50))}
FPS = 120


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):  # установка сдвига камеры так, чтобы игрок оказался по центру
        self.offset.x = self.sprite.add_rect.center[0] - WIDTH // 2
        self.offset.y = self.sprite.add_rect.center[1] - HEIGHT // 2

    def draw(self, groups, interface, screen):
        self.camera_centering()

        i = 0
        for group in groups:  # каждый спрайт выводится на экран друг за другом с учётом сдвига камеры
            for sprite in group.sprites():
                screen.blit(sprite.image, sprite.rect.topleft - self.offset)

            i += 1

        for texture in interface:
            screen.blit(texture.image, texture.blit_pos)

        # точки куда движутся противники (можно удалить)
        # for enemy in groups[1].sprites()[1:3]:
        #     if any(enemy.target_point):
        #         pygame.draw.circle(screen, 'red', enemy.target_point - self.offset, 10)
        #     if any(enemy.current_target):
        #         pygame.draw.circle(screen, 'green', enemy.current_target - self.offset, 10)

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
        self.enemies = [Enemy(pos, 'assets/player.png', (self.entities,)) for pos in ENEMIES_POSITION['test']]

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
                    self.save_game(self.level, 'rewards', 10, 1000,
                                   self.player.rect.center, self.enemy.rect.center, self.enemy_amount)
                    self.thread.terminated.set()
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.player.finite_angle = check_angle(self.player.add_rect.center, event.pos + self.camera.offset)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.to_shoot = True

            for enemy in self.enemies:
                enemy.check_the_point(self.map.wall_shape, self.player.add_rect.center)
                if enemy.see_player:
                    enemy.finite_angle = check_angle(enemy.add_rect.center, self.player.add_rect.center)
                    enemy.to_shoot = abs(enemy.angle - enemy.finite_angle) < 5
                elif not any(enemy.target_point):
                    enemy.find_random_route(self.map.wall_shape)



            while self.thread.update_groups.is_set():  # ждём пока персонаж не обработает своё положение
                pass

            self.camera.draw((self.map, self.entities), self.interface, self.screen)

            clock.tick(FPS)


def check_angle(entity_pos, point_pos):   # определение угла поворота в зависимости от положения мыши
    quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

    x_dist, y_dist = point_pos - pygame.Vector2(entity_pos)
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
                level, rewards, player_bullets, enemy_bullets, player_pos, enemy_pos, enemy_amount = pg_file.readlines()
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
