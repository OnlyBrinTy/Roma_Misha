from texture import Texture
import pygame
pygame.init()

MAPS_DIRECTORY = 'maps'
CELL_SIZE = 50


class Block(pygame.sprite.Sprite, Texture):
    def __init__(self, group, kind, position):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, position, pygame.image.load(f'assets/wall_{kind}.png'))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Map(pygame.sprite.Group):  # Класс для создания карт
    def __init__(self, filename):
        super().__init__()
        # принимает на вход имя файла
        # список спрайтов, по которым можно ходить
        # а так же чекпоинт, до которог нужно дойти
        # тут должен быть словарь спрайтов, но их пока нет, поэтому словарь пуст
        self.sprites_kinds = {0: None, 1: None, 2: None, 3: None, 4: None}
        self.map = []  # создание карты

        with open(f'{MAPS_DIRECTORY}/{filename}') as map_file:  # открываем файл с картой
            for y, line in enumerate(map_file):
                row = []
                for x, kind in enumerate(line.replace('\n', '')):
                    if kind != ' ':
                        row.append(Block(self, kind, (x * CELL_SIZE, y * CELL_SIZE)))    # записываем данные из файла в список

                self.map.append(row)

        self.map_height = len(self.map)  # высота карты
        self.map_width = len(self.map[0])  # ширина карты

    def get_sprite_id(self, sprite_position):  # возвращает id спрайта
        return self.map[sprite_position[1]][sprite_position[0]]
