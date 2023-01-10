from threading import Thread, Event
from math import sin, cos, radians
from texture import Texture
from rectangle import Rect
from weapon import Weapon
from math import sqrt
from time import time
import numpy as np
import pygame


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
        self.to_shoot = False
        # угол наклона картинки
        # Он отличается тем, что он поддерживает дробные числа в координатах.
        self.add_rect = Rect(self.rect)
        self.mask = pygame.mask.from_surface(self.image)

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

        self.image = pygame.transform.rotate(self._original_image, self.angle + 1)  # поворот картинки
        self.mask = pygame.mask.from_surface(self.image)  # меняем маску
        self.rect.size = self.image.get_size()  # меняем rect.size на новый

        img_half_w = self.image.get_width() / 2
        img_half_h = self.image.get_height() / 2

        self.rect_correction.update(self.add_rect.h_width - img_half_w, self.add_rect.h_height - img_half_h)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction  # устанавливаем правильный  topleft

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
        for sprite in group.sprites():
            if sprite.kind and pygame.sprite.collide_mask(self, sprite):  # если столкнулись с красным блоком
                if check_collision:
                    return True

                offset = pygame.Vector2(self.rect.topleft) - sprite.rect.topleft
                collide_mask = sprite.mask.overlap_mask(self.mask, offset)
                width, height = collide_mask.get_size()

                bit_array = np.ones(collide_mask.get_size(), dtype=np.bool_)
                cords = np.where(bit_array)
                bit_array[cords] = np.array(list(map(collide_mask.get_at, np.array(cords).T)), dtype=np.bool_)

                y_array = np.where(np.any(bit_array, axis=0))
                top_penetration = limit(np.max(y_array), height, 0)
                bottom_penetration = limit(np.min(y_array), 1, height + 1) - height - 1

                if not positive_y and top_penetration and bottom_penetration:
                    top_penetration = bottom_penetration = 0
                else:
                    if not sprite.bounds[0] or positive_y is False:
                        top_penetration = 0
                    if not sprite.bounds[1] or positive_y is True:
                        bottom_penetration = 0

                y_ps.append(max(bottom_penetration, top_penetration, key=abs))
                if not positive_y:
                    if y_ps[0]:
                        positive_y = y_ps[0] > 0
                    else:
                        positive_y = self.rect.centery < sprite.rect.centery

                x_array = np.where(np.any(bit_array, axis=1))
                left_penetration = limit(np.max(x_array), width, 0)
                right_penetration = limit(np.min(x_array), 1, width + 1) - width - 1

                if not positive_x and left_penetration and right_penetration:
                    left_penetration = right_penetration = 0
                else:
                    if not sprite.bounds[2] or positive_x is False:
                        left_penetration = 0
                    if not sprite.bounds[3] or positive_x is True:
                        right_penetration = 0

                x_ps.append(max(right_penetration, left_penetration, key=abs))
                if not positive_x:
                    if x_ps[0]:
                        positive_x = x_ps[0] > 0
                    else:
                        positive_x = self.rect.centerx < sprite.rect.centerx

                if y_ps[-1] and x_ps[-1]:
                    difference = abs(y_ps[-1] - x_ps[-1])

                    if difference > 1:
                        abs_x, abs_y = abs(x_ps[-1]), abs(y_ps[-1])
                        if abs_x > abs_y:
                            x_ps[-1] = 0
                        elif abs_y > abs_x:
                            y_ps[-1] = 0

        if x_ps or y_ps:
            return [max(x_ps, key=abs), max(y_ps, key=abs)]

    def basic_update(self, delay):
        slowdown = delay / 0.035  # отклонение от стандартного течения времени (1 кадр в 0.035 секунды)

        self.motion(slowdown)  # обрабатываем физику и нажатия (если есть)
        self.set_angle(slowdown)  # теперь у кручения тоже есть своя физика


class Player(Entity):  # Это спрайт для групп camera и entities
    def __init__(self, start_pos, file_name, groups):
        Entity.__init__(self, start_pos, file_name, groups)

        self.max_speed = 10
        self.weapon = Weapon(30)

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

    def shoot(self):
        if self.weapon.shoot():
            pos_in_radians = radians(self.angle + 87)
            dir_in_radians = radians(self.angle + 90)

            barrel_addition = self.add_rect.h_width * sin(pos_in_radians), self.add_rect.h_width * cos(pos_in_radians)
            bullet_pos = pygame.Vector2(self.rect.center) + barrel_addition

            direction = self.add_rect.h_width * sin(dir_in_radians), self.add_rect.h_width * cos(dir_in_radians)

            Bullet(bullet_pos, 'assets/bullet.png', (self.groups()[0],), direction, self.angle)

            self.to_shoot = False

    def update(self, delay, group):
        self.basic_update(delay)

        wall_entrance = self.get_collision(group)  # на сколько пикселей вошёл в стену
        # x_used, y_used = 0, 0

        if wall_entrance:
            # x_used = 1
            self.add_rect.x -= wall_entrance[0]  # пробуем вытолкнуться по оси x
            self.rect.topleft = self.add_rect.topleft + self.rect_correction

        if self.get_collision(group, check_collision=True):  # если мы до сих пор в стене
            # y_used = 1
            self.add_rect.y -= wall_entrance[1]  # пробуем вытолкнуться по оси y
            self.rect.topleft = self.add_rect.topleft + self.rect_correction

        # if wall_entrance:  # если произошло столкновение
        #     # делаем отскок от стены
        #     self.vectors.direction = pygame.Vector2(wall_entrance).elementwise() * (x_used, y_used) * -2
        #     self.vectors.velocity = pygame.Vector2(*map(sqrt, self.vectors.velocity))
        #
        #     overload = sum(self.vectors.velocity) - self.max_speed  # уменьшаем скорость если превышена
        #
        #     if overload > 0:
        #         self.vectors.velocity -= self.vectors.velocity / sum(self.vectors.velocity) * overload

        if self.to_shoot:
            self.shoot()


class Bullet(Entity):
    def __init__(self, start_pos, file_name, groups, direction, angle):
        Entity.__init__(self, start_pos, file_name, groups)

        self.vectors.direction.update(direction)
        self.vectors.direction /= 5

        self.finite_angle, self.angle = angle, angle + 1
        self.set_angle(None)

    def motion(self, slowdown):
        self.add_rect.topleft += self.vectors.direction * slowdown
        self.rect.topleft = self.add_rect.topleft + self.rect_correction

    def update(self, delay, group):
        self.basic_update(delay)

        if self.get_collision(group, check_collision=True):
            self.kill()


class EntityThread(Thread):  # обработка сущностей вынесена в отдельный поток
    def __init__(self, walls_group, *groups_to_update):
        super().__init__()

        self.groups_to_update = groups_to_update  # группы, которые будем обновлять (возможно не только entities)
        self.collide_group = walls_group  # група со спрайтами, с которыми будет происходить столкновение

        self.update_groups = Event()  # флажок означающий, что надо обновить группы
        self.terminated = Event()  # флажок означающий, жив или мёртв этот поток (так можно убить извне)

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
    def __init__(self):
        self.direction = pygame.Vector2()

    @property
    def velocity(self):
        return pygame.Vector2(*map(abs, self.direction))

    @velocity.setter
    def velocity(self, value):
        direction_mask = pygame.Vector2(*map(lambda x: bool(x >= 0) * 2 - 1, self.direction))

        self.direction = direction_mask.elementwise() * value
