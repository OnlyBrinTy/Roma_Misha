from texture import *
from numpy import *
import pygame

pygame.init()

MAPS_DIRECTORY = 'maps'
CELL_SIZE = pygame.image.load('assets/walls/floor.png').get_size()[0]
sprites_kinds = {0: 'floor', 1: 'wall_1', 2: 'wall_1_1', 3: 'wall_1_2_angle',
                 4: 'wall_1_2_parallel', 5: 'wall_1_3', 6: 'wall_1_4'}
walls_kind = {'floor': 0, 'wall_1': 1, 'wall_1_1': 2, 'wall_1_2_angle': 3,
              'wall_1_2_parallel': 4, 'wall_1_3': 5, 'wall_1_4': 6}


class Block(pygame.sprite.Sprite, Texture):
    def __init__(self, group, kind, position, bounds, rotation_angle):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, position,
                         pygame.transform.rotate(pygame.image.load(f'assets/walls/{kind}.png'), 90 * rotation_angle))

        self.kind = walls_kind[kind]  # тип - либо стена - 1 либо пол - 0
        self.bounds = array(bounds)  # наличие стен с 4 сторон
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
        self.map = []  # создание карты

        with open(f'{MAPS_DIRECTORY}/{filename}') as map_file:  # открываем файл с картой
            map_list = list(map(str.rstrip, map_file.readlines()))

            for i, line in enumerate(map_list):
                row = []
                for j, kind in enumerate(line):
                    if kind != ' ':
                        # записываем данные из файла в список
                        block_kind = sprites_kinds[int(kind)]
                        rotation_angle = 0

                        if kind == '1' and i < len(map_list) - 1 and j < len(map_list[0]) - 1:
                            if map_list[i][j + 1] == '0':
                                block_kind = sprites_kinds[2]
                                rotation_angle = -1
                            elif map_list[i][j - 1] == '0':
                                block_kind = sprites_kinds[2]
                                rotation_angle = 1
                            elif map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[2]
                                rotation_angle = 2
                            elif map_list[i - 1][j] == '0':
                                block_kind = sprites_kinds[2]
                                rotation_angle = 0

                            if map_list[i][j + 1] == '0' and map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[3]
                                rotation_angle = -1
                            elif map_list[i][j + 1] == '0' and map_list[i - 1][j] == '0':
                                block_kind = sprites_kinds[3]
                                rotation_angle = 0
                            elif map_list[i][j - 1] == '0' and map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[3]
                                rotation_angle = 2
                            elif map_list[i][j - 1] == '0' and map_list[i - 1][j] == '0':
                                block_kind = sprites_kinds[3]
                                rotation_angle = 1

                            if map_list[i][j - 1] == '0' and map_list[i][j + 1] == '0':
                                block_kind = sprites_kinds[4]
                                rotation_angle = 1
                            elif map_list[i - 1][j] == '0' and map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[4]
                                rotation_angle = 0

                            if map_list[i][j - 1] == '0' and map_list[i][j + 1] == '0' and map_list[i - 1][j] == '0':
                                block_kind = sprites_kinds[5]
                                rotation_angle = 0
                            elif map_list[i][j - 1] == '0' and map_list[i][j + 1] == '0' and map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[5]
                                rotation_angle = 2
                            elif map_list[i][j - 1] == '0' and map_list[i - 1][j] == '0' and map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[5]
                                rotation_angle = 1
                            elif map_list[i][j + 1] == '0' and map_list[i - 1][j] == '0' and map_list[i + 1][j] == '0':
                                block_kind = sprites_kinds[5]
                                rotation_angle = -1

                            if map_list[i][j + 1] == '0' and map_list[i][j - 1] == '0' and \
                                    map_list[i + 1][j] == '0' and map_list[i - 1][j] == '0':
                                block_kind = sprites_kinds[6]
                                rotation_angle = 0

                        elif kind == '1' and i == len(map_list) - 1 and j < len(map_list[0]) - 1:
                            if map_list[i - 1][j] == '0':
                                block_kind = sprites_kinds[2]
                                rotation_angle = 0
                        elif kind == '1' and j == len(map_list[0]) - 1 and i < len(map_list) - 1:
                            if map_list[i][j - 1] == '0':
                                block_kind = sprites_kinds[2]
                                rotation_angle = 1
                        row.append(Block(self, block_kind, (j * CELL_SIZE, i * CELL_SIZE),
                                         get_bounds(i, j, map_list), rotation_angle))

                self.map.append(row)
            map_file.close()

    def get_sprite_id(self, sprite_position):  # возвращает id спрайта
        return self.map[sprite_position[1]][sprite_position[0]]
