from shapely import Polygon, unary_union
from texture import Texture
from numpy import array
import pygame
pygame.init()

MAPS_DIRECTORY = 'maps'


class Block(pygame.sprite.Sprite, Texture):
    def __init__(self, group, kind, position, bounds):
        pygame.sprite.Sprite.__init__(self, group)
        Texture.__init__(self, position, pygame.image.load(f'assets/wall_{kind}.png'))

        self.kind = int(bool(int(kind)))  # тип - либо стена - 1 либо пол - 0
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

            if not any(bounds) and False:
                return [True] * 4

            return bounds

        self.cell_size = pygame.image.load('assets/wall_0.png').get_size()[0]
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
                        row.append(Block(self, kind, (x, y), get_bounds(i, j, map_list)))

                        if int(kind):
                            far_x, far_y = x + self.cell_size, y + self.cell_size
                            #  добавляем форму в ряд
                            self.wall_shape.append(Polygon(((x, y), (far_x, y), (far_x, far_y), (x, far_y))))

                self.map.append(row)

        self.wall_shape = unary_union(self.wall_shape)
