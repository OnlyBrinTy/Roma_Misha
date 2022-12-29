from actor import AnotherThread, Player
from math import atan, degrees
from texture import Texture
import weapon
import pygame

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
FPS = 120
maps_directory = 'maps'
sprite_size = 64


class Map:  # Класс для создания карт
    def __init__(self, filename, free_sprites, checkpoint):
        # принимает на вход имя файла
        # список спрайтов, по которым можно ходить
        # а так же чекпоинт, до которог нужно дойти
        self.map = []  # создание карты

        with open(f'{maps_directory}/{filename}') as map_file:  # открываем файл с картой
            for line in map_file:
                self.map.append(list(map(int, line.split())))  # записываем данные из файла в список

        self.map_height = len(self.map)  # высота карты
        self.map_width = len(self.map[0])  # ширина карты
        self.sprite_size = sprite_size  # размер 1 клетки
        self.free_sprites = free_sprites  # свобоные клетки
        self.checkpoint = checkpoint  # чекпоинт

    def map_render(self, screen):  # рендер карты для отображения на экране
        sprites = {}  # тут должен быть словарь спрайтов, но их пока нет, поэтому словарь пуст
        for y in range(self.map_height):  # проходимся циклом по карте
            for x in range(self.map_width):
                sprite = None  # получаем значение спрайта из словаря
                screen.blit()  # отображаем наш спрайт на экране

    def get_sprite_id(self, sprite_position):  # возвращает id спрайта
        return self.map[sprite_position[1]][sprite_position[0]]

    def if_sprite_free(self, sprite_position):  # проверяет, можно ли ходить по этому спрайту
        return self.get_sprite_id(sprite_position) in self.free_sprites


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):   # установка сдвига камеры так, чтобы игрок оказался по центру
        self.offset.x = self.sprite.rect.center[0] - WIDTH // 2
        self.offset.y = self.sprite.rect.center[1] - HEIGHT // 2

    def draw(self, textures, screen):
        self.camera_centering()

        screen.fill(BACKGROUND_COLOR)   # заливка фона

        for texture in textures:  # каждая текстура выводятся на экран друг за другом с учётом сдвига камеры
            display_position = texture.blit_pos - self.offset
            screen.blit(texture.image, display_position)

        pygame.display.update()


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()  # через камеру происходит отображение всего на экране
        self.player = Player((WIDTH // 2, HEIGHT // 2), self.camera)
        self.textures = [Texture((0, 0), 'ground.png'), self.player]
        # в textures лежат текстуры, которые будут затем выводится на экран
        # они лежат в порядке отображения. Сначала рисуем землю и поверх неё рисуем игрока

        self.thread = AnotherThread(self.camera)
        self.thread.start()
        weap = weapon.BulletAmount()

        clock = pygame.time.Clock()
        running = True

        while running:
            self.thread.update_groups.set()  # делаем запрос на обновление персонажа

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.screen.blit(weap.get_bullet(), (100, 100))
                elif event.type == pygame.MOUSEMOTION:
                    self.player.set_angle(self.check_angle(event.pos))

            while self.thread.update_groups.is_set():    # ждём пока персонаж не обработает своё положение
                pass

            self.camera.draw(self.textures, self.screen)
            pygame.display.update()

            clock.tick(FPS)

    def check_angle(self, mouse_pos):   # определение угла поворота в зависимости от положение мыши
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
