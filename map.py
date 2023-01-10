from texture import *
from numpy import *
import pygame
pygame.init()

MAPS_DIRECTORY = 'maps'
CELL_SIZE = pygame.image.load('assets/wall_0.png').get_size()[0]


class Block(pygame.sprite.Sprite, Texture):
    def __init__(self, group, kind, position, bounds):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, position, pygame.image.load(f'assets/wall_{kind}.png'))

        self.kind = int(bool(int(kind)))    # тип - либо стена - 1 либо пол - 0
        self.bounds = array(bounds)     # наличие стен с 4 сторон
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Map(pygame.sprite.Group):  # Класс для создания карт
    def __init__(self, filename):
        super().__init__()

        def get_bounds(y, x, file):
            cords = (y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)

            bounds = [True] * 4
            for i, (bounding_y, bounding_x) in enumerate(cords):
                if 0 <= bounding_y < len(file) and 0 <= bounding_x < len(file[bounding_y]):
                    bounding_block = file[bounding_y][bounding_x]
                    if bounding_block.isdigit():
                        if int(bounding_block):
                            bounds[i] = False

            if not any(bounds):
                return [True] * 4

            return bounds

        # принимает на вход имя файла
        # список спрайтов, по которым можно ходить
        # а так же чекпоинт, до которог нужно дойти
        # тут должен быть словарь спрайтов, но их пока нет, поэтому словарь пуст
        self.sprites_kinds = {0: None, 1: None, 2: None, 3: None, 4: None}
        self.map = []  # создание карты

        with open(f'{MAPS_DIRECTORY}/{filename}') as map_file:  # открываем файл с картой
            map_list = list(map(str.rstrip, map_file.readlines()))

            for i, line in enumerate(map_list):
                row = []
                for j, kind in enumerate(line):
                    if kind != ' ':
                        # записываем данные из файла в список
                        row.append(Block(self, kind, (j * CELL_SIZE, i * CELL_SIZE), get_bounds(i, j, map_list)))

                self.map.append(row)

    def get_sprite_id(self, sprite_position):  # возвращает id спрайта
        return self.map[sprite_position[1]][sprite_position[0]]
