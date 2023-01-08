from threading import *
from rectangle import *
from time import *
from random import *
from field import *
import pygame

MAX_SPEED = 10


class Entity(pygame.sprite.Sprite, Texture):
    def __init__(self, start_pos, file_name, groups):
        pygame.sprite.Sprite.__init__(self, groups)
        Texture.__init__(self, start_pos, pygame.image.load(file_name))

        self.vectors = Vectors()
        # Так как персонаж по умолчанию крутится очень странно,
        # чтобы скомпенсировать его странное вращение в нормальное используется отдельный вектор
        self.rect_correction = pygame.Vector2()
        # _original_image - это вид картинки по умолчанию(без наклона).
        # Нужна на случай, если картинка крутится
        self._original_image = self.image
        # Bместо встроенного в pygame rect я использую свой аналог.
        # Он отличается тем, что он поддерживает дробные числа в координатах.
        self.add_rect = Rect(self.rect)  # Создаем объект класса Rect, куда передаем self.rect из Texture
        self.mask = pygame.mask.from_surface(self.image)  # Создаем маску изображения для обработки столкновений

        self.half_w = self.rect.width / 2  # Половина ширины и высоты нашего объекта self.rect
        self.half_h = self.rect.height / 2

    def set_angle(self, angle):
        self.image = pygame.transform.rotate(self._original_image, angle)  # поворот картинки
        self.mask = pygame.mask.from_surface(self.image)  # меняем маску
        self.rect.size = self.image.get_size()  # меняем rect.size на новый

        img_half_w = self.image.get_width() / 2 # Половина ширины и высоты self.image
        img_half_h = self.image.get_height() / 2

        self.rect_correction.update(self.half_w - img_half_w, self.half_h - img_half_h)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction  # устанавливаем правильный  topleft

    def update(self, delay, group):
        slowdown = delay / 0.035  # отклонение от стандартного течения времени (1 кадр в 0.035 секунды)
        self.motion(slowdown)  # обрабатываем физику и нажатия (если есть)

        # для компенсации слишком редкого/частого обновления персонажа
        # скорость умножается на коэффициент замедления времени
        real_direction = self.vectors.direction * slowdown
        #   add_rect отображает положение игрока в пространстве без учёта кручения в дробных числах и не меняет размер
        self.add_rect.topleft += real_direction
        #   обычный rect нужен для отображения картинки, его размеры зависят от разворота картинки,
        #   а topleft всегда изменяется в зависимости от разворота картинки (чтобы не болтало, как это было раньше)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction

        for sprite in group.sprites():
            if sprite.kind == 1 and pygame.sprite.collide_mask(self, sprite):  # если столкнулись с красным блоком
                pass


class Player(Entity):  # Это спрайт для групп camera и entities
    def __init__(self, start_pos, file_name, groups):
        self.vectors = Vectors()
        self.start_pos = start_pos
        Entity.__init__(self, start_pos, file_name, groups)

    def motion(self, slowdown):
        def formula(speed, depth):
            curr_increase = 2 / 1.15 ** speed

            if depth:
                return curr_increase + formula(speed + curr_increase, depth - 1)

            return curr_increase * (slowdown % 1)

        keys = pygame.key.get_pressed()
        w, a, s, d, ctrl = keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_LCTRL]

        boost = formula(sum(self.vectors.velocity), int(slowdown))

        self.vectors.direction += boost * (bool(d) - bool(a)), boost * (bool(s) - bool(w))

        if w == s and a == d and self.vectors.velocity:
            fractions = pygame.Vector2(self.vectors.velocity / sum(self.vectors.velocity))

            self.vectors.velocity -= tuple(map(min, zip(self.vectors.velocity, fractions * boost)))
        elif w == s:
            self.vectors.velocity -= 0, min(self.vectors.velocity.y, boost)
        elif a == d:
            self.vectors.velocity -= min(self.vectors.velocity.x, boost), 0

        if sum(self.vectors.velocity) > MAX_SPEED:
            overload = sum(self.vectors.velocity) - MAX_SPEED

            if w != s and a != d:
                self.vectors.velocity -= self.vectors.velocity / sum(self.vectors.velocity) * overload
            else:
                self.vectors.velocity -= overload * bool(w == s), overload * bool(a == d)


class Enemies(Entity):  # Это спрайт для групп camera и entities
    def __init__(self, start_pos, file_name, groups):
        self.vectors = Vectors()
        self.start_pos = start_pos
        Entity.__init__(self, start_pos, file_name, groups)

    def motion(self, slowdown):
        self.vectors.velocity = randrange(-5, 5), randrange(-5, 5)




class EntityThread(Thread):  # обработка сущностей вынесена в отдельный поток
    def __init__(self, group, *groups_to_update):
        super().__init__()

        self.groups_to_update = groups_to_update  # группы, которые будем обновлять (возможно не только entities)
        self.update_groups = Event()  # флажок означающий, что надо обновить группы
        self.terminated = Event()  # флажок означающий, жив или мёртв этот поток (так можно убить извне)
        self.collide_group = group  # група со спрайтами, с которыми будет происходить столкновение

    def run(self):
        start = time()

        while not self.terminated.is_set():
            if self.update_groups.is_set():
                delay = time() - start  # считаем задержку между запросами на обновление
                start = time()

                for group in self.groups_to_update:
                    group.update(delay, self.collide_group)

                self.update_groups.clear()  # ставим флажок обновления на False


class Vectors:  # содержит direction (пример [5.5, -4.5]) и его аналог velocity, но под модулем (пример [5.5, 4.5])
    direction = pygame.Vector2()

    @property
    def velocity(self):
        return pygame.Vector2(*map(abs, self.direction))

    @velocity.setter
    def velocity(self, value):
        direction_mask = pygame.Vector2(*map(lambda x: bool(x >= 0) * 2 - 1, self.direction))

        self.direction = direction_mask.elementwise() * value
