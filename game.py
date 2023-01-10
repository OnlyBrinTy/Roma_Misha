from entities import EntityThread, Player, Enemy
from math import atan, degrees
from map import Map
import pygame

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
ENEMIES_POSITION = {'test': ((10 * 50, 5 * 50), (10 * 50, 15 * 50))}
FPS = 120


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):  # установка сдвига камеры так, чтобы игрок оказался по центру
        self.offset.x = self.sprite.add_rect.center[0] - WIDTH // 2
        self.offset.y = self.sprite.add_rect.center[1] - HEIGHT // 2

    def draw(self, groups, interface, screen):
        self.camera_centering()

        screen.fill(BACKGROUND_COLOR)   # заливка фона
        i = 0
        for group in groups:  # каждый спрайт выводится на экран друг за другом с учётом сдвига камеры
            for sprite in group.sprites():
                screen.blit(sprite.image, sprite.rect.topleft - self.offset)

            i += 1

        for texture in interface:
            screen.blit(texture.image, texture.blit_pos)

        pygame.display.update()


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()  # через камеру происходит отображение всего на экране
        self.entities = pygame.sprite.Group()   # все движущиеся существа в игре (даже пули)
        self.level = 'test'
        self.map = Map(f'{self.level}_level.txt')

        self.player = Player((50 * 27, 50 * 5), 'assets/player.png', (self.entities, self.camera))
        self.enemies = [Enemy(pos, 'assets/player.png', (self.entities,)) for pos in ENEMIES_POSITION[self.level]]
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
                    SaveGame('test_level.txt', 'rewards', '10')
                    self.thread.terminated.set()
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.player.finite_angle = check_angle(self.player.add_rect.center, event.pos + self.camera.offset)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.to_shoot = True

            for enemy in self.enemies:
                if enemy.check_player(self.map.shapes_map):
                    enemy.first_noticing = True
                    enemy.finite_angle = check_angle(enemy.add_rect.center, self.player.add_rect.center)
                    enemy.to_shoot = abs(enemy.angle - enemy.finite_angle) < 5

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


class SaveGame:
    def __init__(self, current_checkpoint, rewards, bullet_amount):
        self.checkpoint = current_checkpoint
        self.rewards = rewards
        self.bullet_amount = bullet_amount
        with open('progress/progress.txt', mode='w', encoding='utf-8') as pg_file:
            pg_file.write(self.checkpoint + '\n')
            pg_file.write(self.rewards + '\n')
            pg_file.write(self.bullet_amount)
            pg_file.close()
