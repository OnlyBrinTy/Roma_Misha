from threading import Thread, Event
from texture import Texture
from rectangle import Rect
import numpy as np
from math import sqrt
from time import time
import pygame

# argmax, argmin, any, array, bool_, where, ones, max_


class Entity(pygame.sprite.Sprite, Texture):
    def __init__(self, start_pos, file_name, groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        Texture.__init__(self, start_pos, pygame.image.load(file_name))

        self.vectors = Vectors()
        # Так как персонаж по умолчанию крутится очень странно,
        # чтобы скомпенсировать его странное вращение в нормальное используется отдельный вектор
        self.rect_correction = pygame.Vector2()
        # есть _original_image - это вид картинки по умолчанию(без наклона).
        # Нужна на случай, если картинка крутится
        self._original_image = self.image
        # вместо встроенного в pygame rect я использую свой аналог.
        self.finite_angle = self.angle = 0
        # угол наклона картинки
        # Он отличается тем, что он поддерживает дробные числа в координатах.
        self.add_rect = Rect(self.rect)
        self.mask = pygame.mask.from_surface(self.image)

        self.half_w = self.rect.width / 2
        self.half_h = self.rect.height / 2

    def set_angle(self, slowdown):
        diff = self.finite_angle - self.angle
        if not diff:
            return

        diff = min(diff, (360 - abs(diff)) * (1 - int(diff > 0) * 2), key=abs)
        if abs(diff) < 1.5:
            self.angle = self.finite_angle
        else:
            adjust = (20 / (1 + 1.2 ** -(abs(diff) - 20))) * slowdown * (1 - int(diff < 0) * 2)

            self.angle = (self.angle + adjust) % 360

        self.image = pygame.transform.rotate(self._original_image, self.angle)   # поворот картинки
        self.mask = pygame.mask.from_surface(self.image)    # меняем маску
        self.rect.size = self.image.get_size()  # меняем rect.size на новый

        img_half_w = self.image.get_width() / 2
        img_half_h = self.image.get_height() / 2

        self.rect_correction.update(self.half_w - img_half_w, self.half_h - img_half_h)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction    # устанавливаем правильный  topleft

    def get_collision(self, group, check_collision=False):
        def limit(num, if_num, then_num):
            if num >= 0:
                num += 1
            else:
                num -= 1

            if abs(num) == if_num:
                return then_num

            return num

        positive_x, positive_y = None, None
        x_ps, y_ps = [], []
        total_bounds = np.zeros(4, dtype=np.bool_)
        for sprite in group.sprites():
            if sprite.kind == 1 and pygame.sprite.collide_mask(self, sprite):   # если столкнулись с красным блоком
                total_bounds += sprite.bounds

                offset = pygame.Vector2(self.rect.topleft) - sprite.rect.topleft
                collide_mask = sprite.mask.overlap_mask(self.mask, offset)
                width, height = collide_mask.get_size()

                bit_array = np.ones(collide_mask.get_size(), dtype=np.bool_)
                cords = np.where(bit_array)
                bit_array[cords] = np.array(list(map(collide_mask.get_at, np.array(cords).T)), dtype=np.bool_)

                y_array = np.where(np.any(bit_array, axis=0))
                top_penetration = limit(np.max(y_array), height, 0)
                bottom_penetration = limit(np.min(y_array), 1, height + 1) - height - 1

                if positive_y or not(top_penetration and bottom_penetration):
                    if not sprite.bounds[0] or positive_y is False:
                        top_penetration = 0
                    if not sprite.bounds[1] or positive_y is True:
                        bottom_penetration = 0

                    y_ps.append(max(bottom_penetration, top_penetration, key=abs))
                    if not positive_y:
                        if y_ps[0]:
                            positive_y = y_ps[0] > 0
                        else:
                            positive_y = self.rect.centery - sprite.rect.centery < 0

                        if check_collision:
                            return True

                x_array = np.where(np.any(bit_array, axis=1))
                left_penetration = limit(np.max(x_array), width, 0)
                right_penetration = limit(np.min(x_array), 1, width + 1) - width - 1

                if positive_x or not (left_penetration and right_penetration):
                    if not sprite.bounds[2] or positive_x is False:
                        left_penetration = 0
                    if not sprite.bounds[3] or positive_x is True:
                        right_penetration = 0

                    x_ps.append(max(right_penetration, left_penetration, key=abs))
                    if not positive_x:
                        if x_ps[0]:
                            positive_x = x_ps[0] > 0
                        else:
                            positive_x = self.rect.centerx - sprite.rect.centerx < 0

                        if check_collision:
                            return True

        if x_ps or y_ps:
            return [max(x_ps + [0], key=abs), max(y_ps + [0], key=abs)]

    def update(self, delay, group):
        slowdown = delay / 0.035    # отклонение от стандартного течения времени (1 кадр в 0.035 секунды)

        self.motion(slowdown)   # обрабатываем физику и нажатия (если есть)
        self.set_angle(slowdown)    # теперь у кручения тоже есть своя физика

        wall_entrance = self.get_collision(group)   # на сколько пикселей вошёл в стену
        x_used, y_used = 0, 0

        if wall_entrance:
            x_used = 1
            self.add_rect.x -= wall_entrance[0]   # пробуем вытолкнуться по оси x
            print(wall_entrance[0], end=' ')
            self.rect.topleft = self.add_rect.topleft + self.rect_correction

        if self.get_collision(group, check_collision=True):  # если мы до сих пор в стене
            y_used = 1
            self.add_rect.y -= wall_entrance[1]   # пробуем вытолкнуться по оси y
            print(wall_entrance[1])
            self.rect.topleft = self.add_rect.topleft + self.rect_correction

        if wall_entrance:   # если произошло столкновение
            # делаем отскок от стены
            self.vectors.direction = pygame.Vector2(wall_entrance).elementwise() * (x_used, y_used) * -0.01
            self.vectors.velocity.update(*map(sqrt, self.vectors.velocity))

            overload = sum(self.vectors.velocity) - self.max_speed

            if overload:
                self.vectors.velocity -= self.vectors.velocity / sum(self.vectors.velocity) * overload


class Player(Entity):  # Это спрайт для групп camera и entities
    def __init__(self, start_pos, file_name, groups):
        self.vectors = Vectors()
        Entity.__init__(self, start_pos, file_name, groups)
        
        self.max_speed = 10

    def motion(self, slowdown):
        def formula(speed, depth):
            curr_increase = 2 / 1.15 ** speed

            if depth:
                return curr_increase + formula(speed + curr_increase, depth - 1)

            return curr_increase * (slowdown % 1)

        keys = pygame.key.get_pressed()
        w, a, s, d = keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d]
        boost = formula(sum(self.vectors.velocity), min(10, int(slowdown)))

        self.vectors.direction += boost * (bool(d) - bool(a)), boost * (bool(s) - bool(w))

        if w == s and a == d and self.vectors.velocity:
            fractions = pygame.Vector2(self.vectors.velocity / sum(self.vectors.velocity))

            self.vectors.velocity -= tuple(map(min, zip(self.vectors.velocity, fractions * boost)))
        elif w == s:
            self.vectors.velocity -= 0, min(self.vectors.velocity.y, boost)
        elif a == d:
            self.vectors.velocity -= min(self.vectors.velocity.x, boost), 0

        if sum(self.vectors.velocity) > self.max_speed:
            overload = sum(self.vectors.velocity) - self.max_speed

            if w != s and a != d:
                self.vectors.velocity -= self.vectors.velocity / sum(self.vectors.velocity) * overload
            else:
                self.vectors.velocity -= overload * bool(w == s), overload * bool(a == d)

        # для компенсации слишком редкого/частого обновления персонажа
        # скорость умножается на коэффициент замедления времени
        #   add_rect отображает положение игрока в пространстве без учёта кручения в дробных числах и не меняет размер
        self.add_rect.topleft += self.vectors.direction * slowdown
        #   обычный rect нужен для отображения картинки, его размеры зависят от разворота картинки,
        #   а topleft всегда изменяется в зависимости от разворота картинки (чтобы не болтало, как это было раньше)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction


class AnotherThread(Thread):    # обработка сущностей вынесена в отдельный поток
    def __init__(self, group, *groups_to_update):
        super().__init__()

        self.groups_to_update = groups_to_update    # группы, которые будем обновлять (возможно не только entities)
        self.update_groups = Event()    # флажок означающий, что надо обновить группы
        self.terminated = Event()   # флажок означающий, жив или мёртв этот поток (так можно убить извне)
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
