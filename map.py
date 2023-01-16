from shapely import Polygon, unary_union
from texture import Texture
from numpy import array
import pygame
pygame.init()

MAPS_DIRECTORY = 'maps'
sprites_kinds = {0: 'wall_0', 1: 'wall_1', 2: 'wall_1_1', 3: 'wall_1_2_angle',
                 4: 'wall_1_2_parallel', 5: 'wall_1_3', 6: 'wall_1_4'}
walls_kind = {'wall_0': 0, 'wall_1': 1, 'wall_1_1': 2, 'wall_1_2_angle': 3,
              'wall_1_2_parallel': 4, 'wall_1_3': 5, 'wall_1_4': 6}


class Block(pygame.sprite.Sprite, Texture):
    def __init__(self, group, kind, position, bounds, rotation_angle):
        pygame.sprite.Sprite.__init__(self, group)

        image = pygame.transform.rotate(pygame.image.load(f'assets/walls/{kind}.png'), 90 * rotation_angle)
        Texture.__init__(self, position, image)

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

            return bounds

        self.cell_size = pygame.image.load('assets/walls/wall_0.png').get_size()[0]
        # это карта в виде полигона. Пригодится в классе Enemy при проверке видимости игрока
        self.wall_shape = []
        self.map = []  # создание карты

        with open(f'{MAPS_DIRECTORY}/{filename}') as map_file:  # открываем файл с картой
            map_list = list(map(str.rstrip, map_file.readlines()))

            for i, line in enumerate(map_list):
                row = []
                for j, kind in enumerate(line):
                    if kind != ' ':
                        x, y = j * self.cell_size, i * self.cell_size
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
                        row.append(Block(self, block_kind, (j * self.cell_size, i * self.cell_size),
                                         get_bounds(i, j, map_list), rotation_angle))

                        if int(kind):
                            far_x, far_y = x + self.cell_size, y + self.cell_size
                            #  добавляем форму в ряд
                            self.wall_shape.append(Polygon(((x, y), (far_x, y), (far_x, far_y), (x, far_y))))

                self.map.append(row)
            map_file.close()

        self.wall_shape = unary_union(self.wall_shape)
