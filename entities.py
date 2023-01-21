from math import sin, cos, radians, atan, degrees
from random import randint, getrandbits
from shapely import LineString, Point
from texture import Texture
from rectangle import Rect
from weapon import Weapon
import numpy as np
import pygame

PLAYER_SPEED = 7
PLAYER_WEAPON_SPECS = (15, 0.3, 1)
ENEMY_WEAPON_SPECS = (30, 0.2, 2)


# класс для любой сущности: игрока, врага, пули
class Entity(pygame.sprite.Sprite, Texture):
    def __init__(self, start_pos, file_name, groups):
        pygame.sprite.Sprite.__init__(self, *groups)  # сущность может быть включена в несколько групп
        Texture.__init__(self, start_pos, pygame.image.load(file_name))

        self.vectors = Vectors()    # вектора движения по x и y
        # Так как персонаж по умолчанию крутится очень странно,
        # чтобы скомпенсировать его странное вращение в нормальное используется отдельный вектор
        self.rect_correction = pygame.Vector2()  # он прибавляется к координате
        # есть _original_image - это вид картинки по умолчанию(без наклона).
        # Нужна на случай, если картинка крутится
        self._original_image = self.image
        # угол к которому сущность будет стремиться и угол, который имеет сущность на данный момент
        self.finite_angle = self.angle = 0
        # вместо встроенного в pygame rect я использую свой аналог.
        # Он отличается тем, что он поддерживает дробные числа в координатах.
        # но обычный rect тоже много где используется
        self.add_rect = Rect(self.rect)
        self.mask = pygame.mask.from_surface(self.image)

    def set_angle(self, slowdown):  # плавный разворот картинки до нужного угла
        diff = self.finite_angle - self.angle   # сколько осталось до нужного угла

        # (1 - int(diff > 0) * 2) - возвращает -1 или 1 в зависимости от того, положительное ли число
        # есть два варианта как крутится: против и по часовой стрелке. Выбираем тот вариант, где меньше путь
        diff = min(diff, (360 - abs(diff)) * (1 - int(diff > 0) * 2), key=abs)
        # если до искомого угла осталось менее 1.5 градуса, то прикрепляем его к финальной виличине
        if abs(diff) < 1.5 * slowdown:  # slowdown я объяснил на 145 строке
            self.angle = self.finite_angle
        else:
            # на сколько градусов подвинуть сущность (вычисляется по графику синусоиды)
            adjust = (20 / (1 + 1.2 ** -(abs(diff) - 20))) * slowdown * (1 - int(diff < 0) * 2)

            self.angle = (self.angle + adjust) % 360    # если угол превысил 360, то обрезаем

        self.image = pygame.transform.rotate(self._original_image, self.angle + 1.5)  # поворот картинки
        self.mask = pygame.mask.from_surface(self.image)  # меняем маску

        self.rect.size = self.image.get_size()  # меняем rect.size на новый, т.к. картинка крутится

        img_half_w = self.image.get_width() / 2
        img_half_h = self.image.get_height() / 2

        # Формула коррекции положения для плавного кручения (вычислил геометрически)
        self.rect_correction.update(self.add_rect.h_width - img_half_w, self.add_rect.h_height - img_half_h)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction  # устанавливаем правильный  topleft

    # группа спрайтов со стенами и check collision, который возвращает True если было столкновение
    def get_wall_collision(self, walls_group, check_collision=False):   # вычисление вхождения в стену
        side = walls_group.cell_size    # размер стороны блока
        last_pixel = side - 1   # последний пиксель с точки зрения массива, где последний индекс меньше на 1
        # массивы куда кладутся уровни выталкивания по осям x и y для каждого блока с которым столкнулись
        x_ps = y_ps = np.empty(0, dtype=np.int8)
        # для оптимизации сдесь только выборка из блоков, соприкосающихся с rect
        for wall in pygame.sprite.spritecollide(self, walls_group, False):
            # если это стена и есть соприкосновение маской
            if wall.kind and pygame.sprite.collide_mask(self, wall):
                if check_collision:
                    return True

                # отступ центра игрока от левого верхнего угла блока (нужно для определения пересечения их масок)
                offset = pygame.Vector2(self.rect.topleft) - wall.rect.topleft
                collide_mask = wall.mask.overlap_mask(self.mask, offset)

                # массив, представляющий из себя пиксели блока. Пиксели где игрок вошла сущность True, остальные False
                bit_array = np.ones(collide_mask.get_size(), dtype=np.bool_)  # создаём пустой массив с размерами блока
                cords = np.where(bit_array)  # все возможные координаты этого массива в виде кортежей в линейном массиве
                # там, где в маске 1, ставим True
                bit_array[cords] = np.array(list(map(collide_mask.get_at, np.array(cords).T)), dtype=np.bool_)
                # если смотреть через дебагер этот масив повёрнут на 90 градусов, но ничего страшного

                # вектор выталкивания может быть как положительным, так и отрицательным
                # в зависимости от того, от куда игрок вошёл в стену.
                # Примеры: (снизу, справа) = (-y, -x), (сверху, слева) = (+y, +x)
                positive_x = positive_y = None  # пока неизвестно в какую сторону выталкивает этот блок, так что None
                y_penetration = x_penetration = 0   # кол-во пикселей выталкивания для x и y

                # Дальше я покажу алгоритм просчёта выталкивания по оси y
                # Для x сделан такой же кусок кода, как и для y. Это сделано для большей оптимизации,
                # так как цикл займёт больше времени. И для цикла нужно будет переопределять все x-овые и y-овые
                # переменные под списки, к которым нужно обращаться по индексу, что есть дополнительное время

                # смысл определять выталкивание по оси y есть, только если есть горизонтальные границы
                if any(wall.bounds[:2]):    # есть ли горизонтальные границы у блока
                    # если верхняя граница есть, а нижней нет и наоборот. Если есть обе границы,
                    # то неизвестно в каком направлении производить выталкивание. Вверх или вниз?
                    # В таком случае positive_y остаётся None
                    if wall.bounds[0] != wall.bounds[1]:
                        positive_y = wall.bounds[0]

                    axis_array = np.where(np.any(bit_array, axis=0))  # оставляем от bit_array только вхождения по оси y

                    # например, если войти в стену сверху на 30 пикселей, то axis_max == 29, а axis_min == 0,
                    # но если войти в стену снизу на 30 пикселей, то axis_max == 0, а axis_min == 20

                    axis_max = np.max(axis_array)  # максимальный индекс
                    axis_min = np.min(axis_array)  # минимальный индекс

                    if positive_y is None:  # если ещё неизвестно с какой стороны выталкиваться
                        if axis_max == last_pixel and axis_min == 0:    # если игрок занял весь блок целиком для оси y
                            positive_y = self.rect.centery < wall.rect.centery  # определяем по тому, где он находится
                        else:
                            # axis_max + 1 и axis_min - side это финальный
                            # вариант выталкивания сверху и снизу соответственно
                            y_penetration = min((axis_max + 1, axis_min - side), key=abs)   # выбираем наименьший из них

                            positive_y = y_penetration > 0  # на основе определяем, куда выталкиваться

                    # Тут происходит самая магия. Как определить, с какой стороны вошёл игрок
                    # даже если positive_y выдаёт неправильное направление выталкивания. Очень просто!
                    # Нужно лишь понять, что игрок никак не может войти в блок по оси y не заденув первый
                    # или последний пиксель (Пример на строке 108). Значит если сущность зашла в блок сверху, то,
                    # гарантированно, axis_min будет 0, а если снизу, то axis_max будет последним индексом блока
                    if positive_y == False and axis_max == last_pixel:
                        # с вычитанием стороны блока выталкивание становится отрицательным, ведь заходили снизу
                        y_penetration = axis_min - side
                    elif positive_y == True and axis_min == 0:
                        # с добавлением единицы 0 индекс делается 1, что даёт выталкивание даже при малейшем касании
                        y_penetration = axis_max + 1

                y_ps = np.append(y_ps, y_penetration)   # добавляем выталкивание в общий спусок для y

                if any(wall.bounds[2:]):
                    if wall.bounds[2] != wall.bounds[3]:
                        positive_x = wall.bounds[2]

                    axis_array = np.where(np.any(bit_array, axis=1))

                    axis_max = np.max(axis_array)
                    axis_min = np.min(axis_array)

                    if positive_x is None:
                        if axis_max == last_pixel and axis_min == 0:
                            positive_x = self.rect.centerx < wall.rect.centerx
                        else:
                            x_penetration = min((axis_max + 1, axis_min - side), key=abs)

                            positive_x = x_penetration > 0

                    if positive_x == False and axis_max == last_pixel:
                        x_penetration = axis_min - side
                    elif positive_x == True and axis_min == 0:
                        x_penetration = axis_max + 1

                x_ps = np.append(x_ps, x_penetration)

                # если в одном блоке есть выталкиваие по x и y одновременно (угловой блок)
                # и разница между силами выталкивания больше 1
                if y_ps[-1] and x_ps[-1] and abs(y_ps[-1] - x_ps[-1]) > 1:
                    # то удаляется наибольший из этих векторов

                    # это сделано для предотвращения резких соскоков с угловых блоков при трении о них
                    # но есть потенциал для обоих векторов если они не сильно разнятся
                    # (это значит, что сущность касается вертикальной и горизонтальной стены в одинакой степени)
                    # и это позволяет реалистично отталкиваться стволом от стены
                    abs_x, abs_y = abs(x_ps[-1]), abs(y_ps[-1])
                    if abs_x > abs_y:
                        x_ps[-1] = 0
                    elif abs_y > abs_x:
                        y_ps[-1] = 0

        if np.any(x_ps) or np.any(y_ps):
            # вохвращаем самые сильные вектора по x и y
            return pygame.Vector2(max(x_ps, key=abs), max(y_ps, key=abs))

    def check_entity_collision(self):
        for ent in self.groups()[0]:
            # если столкнулись с кем-то, но не с пулей
            if self is not ent and ent.__class__.__name__ != 'Bullet' and pygame.sprite.collide_mask(self, ent):
                return ent

    def basic_entity_update(self, delay):
        slowdown = delay / 0.035  # отклонение от стандартного течения времени (1 кадр в 0.035 секунды)

        self.motion(slowdown)  # обрабатываем физику движения и нажатия (если есть)
        self.set_angle(slowdown)  # теперь у кручения тоже есть своя физика


class Actor:    # общий класс для игрока и врагов
    # предыдущее вхождение в стену сохраняется и используется в разных целях
    prev_wall_entrance = real_prev_wall_entrance = pygame.Vector2(0, 0)
    to_shoot = False    # Нужно ли стрелять

    def __init__(self, path):
        self.root_path = path   # стандартная картинка без анимаций
        # есть всего две анимации: получение урона и смерть
        # если нужно включить анимацию устанавливайте её счётчик на количество
        # кадров в анимации. В случае с уроном их всего 5, но нужно ставить 6,
        # ведь значени 1 занято под прекращение анимации, а 0 значит, что она вовсе выключена
        # Это сделано, чтобы каждый кадр не ставить картинку из root_path
        self.animations_state = {'death': 0, 'damage': 0}

    def shoot(self):    # Выстрел
        if self.weapon.shoot():     # если класс оружия одобрил выстрел и вернул True
            # для определения позиции пули нужно построить
            # прямоугольный треугольник с углом angle и известной гипотенузой hypotenuse
            # чтобы пуля вылетала точно из ствола, нужно немного изменить прибавку к углу
            pos_in_radians = radians(self.angle + 88.5)  # по этому углу определяют позицию
            dir_in_radians = radians(self.angle + 90)   # по этому углу определяют направление

            hypotenuse = self.add_rect.h_width + 15  # длина ствола, как гипотенуза

            # сколько нужно прибавить к координате сущности, чтобы вылетало из ствола
            barrel_addition = hypotenuse * sin(pos_in_radians), hypotenuse * cos(pos_in_radians)
            bullet_pos = pygame.Vector2(self.add_rect.center) + barrel_addition  # итоговая позиция

            # направление
            direction = self.add_rect.h_width * sin(dir_in_radians), self.add_rect.h_width * cos(dir_in_radians)

            # создаём пулю. Её никуда сохранять не надо, она добавится в группу entities
            Bullet(bullet_pos, 'assets/bullet.png', (self.groups()[0],), direction, self.angle)

        self.to_shoot = False

    def animation(self):
        for animation_type, state in self.animations_state.items():
            if state:   # есть анимация
                if state > 1:
                    if animation_type == 'damage':
                        path = f'assets/animations/{animation_type}/{self.__class__.__name__}/{state}.png'
                    else:
                        path = f'assets/animations/{animation_type}/{self.__class__.__name__}/dead.png'

                    self._original_image = pygame.image.load(path)

                    self.animations_state[animation_type] -= 1
                elif animation_type == 'death':  # если анимация закончилась и это смерть
                    self.kill()
                else:
                    self._original_image = pygame.image.load(self.root_path)

                break

    def get_adjust(self, slowdown):
        # Есть такая проблема, что если игра идёт медленно и
        # fps падает в 2 раза (и slowdown повышается в 2 раза),
        # то разгон и торможение будут происходить очень медленно,
        # ведь обновление тоже медленное. И это значит, что если вместо
        # 3 кадров загружается 1, то нужно выполнить обновление положения 3 раза

        def formula(speed, depth):  # Тяжёлая артиллерия здесь, в этой казалось бы простой функции
            curr_increase = 2 / 1.15 ** speed   # по формуле вычисляем прибавку к скорости в зависимости от скорости

            if depth:
                # добавляем последующие прибавки к скорости основанные на скоростях,
                # которые мы получили при сложении скорости и нынешней прибавки
                return curr_increase + formula(speed + curr_increase, depth - 1)

            # после округления индекса замедления осталась дробная часть, которая добавляется в самом конце
            return curr_increase * (slowdown % 1)

        # в качестве скаорости подаётся сумма векторов x, y.
        # В качестве глубины рекурсии выбирается округлённый индекс замедления времени
        return formula(sum(self.vectors.velocity), int(slowdown))

    def limit_speed(self, overload):
        # уменьшаем скорость так, чтобы соотношение векторов x, y осталось тем же.
        # В качестве превышения скорости overload
        self.vectors.velocity -= self.vectors.velocity / sum(self.vectors.velocity) * overload

    def basic_actor_update(self, group):    # базовые обновления для игрока и врагов
        collide_entity = self.check_entity_collision()  # проверяем с кем столкнулись

        if collide_entity:
            # делаем выталкивание. Сделать его точным, как со стенами не поучиться,
            # ведь маски игрока и врагов не прямоугольные
            # с какой стороны находится игрок или враг относительного другого
            bottom_right = map(lambda c: c[0] > c[1], zip(self.add_rect.center, collide_entity.add_rect.center))
            self.add_rect.topleft += tuple(map(lambda n: int(n) * 6 - 3, bottom_right))
            self.rect.topleft = self.add_rect.topleft + self.rect_correction

        wall_entrance = self.get_wall_collision(group)  # на сколько пикселей вошли в стену

        if wall_entrance:
            self.add_rect.topleft -= wall_entrance
            self.rect.topleft = self.add_rect.topleft + self.rect_correction

            if not all(wall_entrance):  # вхождение не по всем векторам
                # Во избежание застревания в узких корридорах
                # используется информация о предыдущих выталкиваниях из стены
                # такое случается если поочерёдно сначала положительное выталкивание, затем отрицательное,
                # причём при сложении эти вектора друг друга гасят практически в 0
                if abs(sum(wall_entrance + self.prev_wall_entrance)) < abs(sum(wall_entrance)):
                    # отменяем выталкивание на 290 строке
                    self.add_rect.topleft += wall_entrance
                    self.rect.topleft = self.add_rect.topleft + self.rect_correction
                elif self.get_wall_collision(group, check_collision=True):  # если после выталкивания всё ещё в стене
                    # Такое тоже случается, если мы застряли в корридоре, но уже когда мы простояли некоторое время
                    # и вектор предудущий предыдущего выталкивания почти равен нынешнему.
                    # А так как мы компенсируем выталкивание, как на 300 строке,
                    # открывается возможность для выхода за текстуры.
                    # Для предотвращения этого будем вычитать разницу между новым и старым вектором выталкивание

                    if abs(sum(wall_entrance)) - abs(sum(self.prev_wall_entrance)) > 0:
                        addition = self.prev_wall_entrance
                    else:
                        addition = pygame.Vector2()

                    self.add_rect.topleft += wall_entrance - addition
                    self.rect.topleft = self.add_rect.topleft + self.rect_correction

            self.prev_wall_entrance = wall_entrance  # обновляем предудущее выталкивание

        if self.to_shoot:
            self.shoot()

        if self.hp <= 0 and not self.animations_state['death']:  # если мы технически умерли (уровень жизней упал до 0)
            self.animations_state['death'] = 60

        self.animation()


class Player(Entity, Actor):  # Это спрайт для групп camera и entities одновременно
    def __init__(self, start_pos, bullets, hp, file_name, groups):
        Entity.__init__(self, start_pos, file_name, groups)
        Actor.__init__(self, file_name)

        self.max_speed = PLAYER_SPEED
        self.weapon = Weapon(bullets, *PLAYER_WEAPON_SPECS)
        self.hp = hp

    def motion(self, slowdown):  # обработка движений
        keys = pygame.key.get_pressed()
        if not self.animations_state['death']:  # при анимации смерти нельзя двидаться
            w, a, s, d = keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d]
        else:
            w, a, s, d = (False,) * 4

        boost = self.get_adjust(slowdown)   # получаем ускорение для текущей скорости

        # очень элегантно ускорение умножается на 0 если не нажата никакая или обе клавиши движения
        self.vectors.direction += boost * (bool(d) - bool(a)), boost * (bool(s) - bool(w))

        if w == s and a == d and self.vectors.velocity:  # торможение по всем осям
            # каждый вектор замедляется по разному в зависимости от того, какую часть от общей скорости он имеет
            fractions = pygame.Vector2(self.vectors.velocity / sum(self.vectors.velocity))

            self.vectors.velocity -= tuple(map(min, zip(self.vectors.velocity, fractions * boost)))
        elif w == s:    # вычитаем ускорение по оси y
            self.vectors.velocity -= 0, min(self.vectors.velocity.y, boost)
        elif a == d:    # вычитаем ускорение по оси x
            self.vectors.velocity -= min(self.vectors.velocity.x, boost), 0

        if sum(self.vectors.velocity) > self.max_speed:  # если скорость превышена
            overload = sum(self.vectors.velocity) - self.max_speed

            if w != s and a != d:   # нажата клавиша для x и для y
                self.limit_speed(overload)  # ограничиваем скорость распределительно
            else:
                # ограничиваем скорость той оси, на которую не нажата клавиша которая
                self.vectors.velocity -= overload * bool(w == s), overload * bool(a == d)

        # для компенсации слишком редкого/частого обновления персонажа
        # скорость умножается на коэффициент замедления времени
        # add_rect отображает положение игрока в пространстве без учёта кручения в дробных числах и не меняет размер
        self.add_rect.topleft += self.vectors.direction * slowdown
        # обычный rect нужен для отображения картинки, его размеры зависят от разворота картинки,
        # а topleft всегда изменяется в зависимости от разворота картинки (чтобы не болтало при кручении)
        self.rect.topleft = self.add_rect.topleft + self.rect_correction

    def update(self, delay, group):
        self.basic_entity_update(delay)
        self.basic_actor_update(group)


class Enemy(Entity, Actor):
    def __init__(self, start_pos, bullets, hp, speed, file_name, shape_adjust, groups):
        Entity.__init__(self, start_pos, file_name, groups)
        Actor.__init__(self, file_name)

        self.wanted_way = pygame.Vector2()  # направление, к которому стремится враг
        # stuck_timer каждые 5 кадров проверяет, не застрял ли враг
        # waiting_timer нжен, чтобы несколько секунд просто ничего не делать.
        # Сделано для более реалистичного поведения
        self.stuck_timer = self.waiting_timer = 0
        # каждые 5 кадров записывается позиция,
        # чтобы проверить как далеко от неё уйдёт через 5 кадров
        self.previous_pos = pygame.Vector2(self.rect.center)
        self.shape_adjust = shape_adjust    # технический отступ game 93
        self.see_player = False  # виден ли противник
        self.target_point = None, None  # точка, в которую нужно дойти
        self.current_target = 0, 0  # точка, которая может отклонятся от target_point для избужания застреваний

        self.max_speed = speed
        self.hp = hp
        self.weapon = Weapon(bullets, *ENEMY_WEAPON_SPECS)

    def motion(self, slowdown):
        boost = self.get_adjust(slowdown)

        self.vectors.direction += self.wanted_way * boost   # ускорение

        if not self.wanted_way and self.vectors.direction:  #замедление
            fractions = pygame.Vector2(self.vectors.velocity / sum(self.vectors.velocity))

            self.vectors.velocity -= tuple(map(min, zip(self.vectors.velocity, fractions * boost)))
        else:   # превышение скорости
            overload = sum(self.vectors.velocity) - self.max_speed
            if overload > 0:
                self.limit_speed(overload)

        self.add_rect.topleft += self.vectors.direction * slowdown
        self.rect.topleft = self.add_rect.topleft + self.rect_correction

    def get_crossing(self, wall_shape, point):  # проверить, видит ли враг эту точку
        # с помощью библиотеки shapely создаётся линия от головы до точки
        # и если она не пересекается со стенами, то враг её видит
        view_line = LineString((self.add_rect.center + self.shape_adjust, point + self.shape_adjust))

        return view_line.intersects(wall_shape)

    def check_the_player(self, wall_shape, point):
        self.see_player = not self.get_crossing(wall_shape, point)
        if self.see_player:     # видит врага
            self.target_point = point   # истанавливаем его как точку, куда нужно идти

    def go_to_point(self, point):   # идти в точку
        dist = pygame.Vector2(point) - self.add_rect.center  # расстояние до точки
        total_dist = sum(set(map(abs, dist)))   # сумма модулей скоростей

        if total_dist > 30:  # более чем в 30 пикселях до цели
            self.wanted_way = dist / total_dist
        elif point == self.target_point:    # если точка является основной целью
            self.wanted_way.update(0, 0)
            self.target_point = None, None

    def find_random_route(self, wall_shape):    # находит случайную точку
        def random_margin():    # точка ищется случайно в радиусе от 20 до 300 пикселей
            return randint(20, 300) * (getrandbits(1) * 2 - 1)

        while True:
            rand_point = self.rect.center + pygame.Vector2(random_margin(), random_margin())    # случайная точка
            if not self.get_crossing(wall_shape, rand_point):   # враг видит эту точку
                self.current_target = self.target_point = rand_point
                break

        if not self.waiting_timer:  # устанавливаем таймер на случайное количество времени
            self.waiting_timer = randint(1, 21)

    def routing(self, delay):   # определяем маршрут
        if any(self.target_point):  # если есть основная цель
            if not self.stuck_timer:    # если истёк период в 5 кадров
                # проверка, как далеко мы ушли от позиции 5 кадров назад
                total_difference = sum(set(map(abs, self.rect.center - self.previous_pos)))
                # почти не сдвинулись с места за 5 кадров и зафиксировано столкновение со стеной
                if total_difference < 60 * self.max_speed * delay and self.prev_wall_entrance:
                    self.current_target -= self.prev_wall_entrance
                else:   # если всё нормально
                    self.current_target = self.target_point     # устанавливаем текущей целью главную

                self.stuck_timer = 5
                self.previous_pos.update(self.rect.center)

            self.go_to_point(self.current_target)
            self.stuck_timer -= 1

    # Чтобы выглядеть натурально, враг должен смотреть в сторону, куда движется
    def rotate_to_path(self):   # направление в сторону движения
        # не видно игрока (при виде игрока враг автоматически напрвляется на него), но есть направление
        if not self.see_player and self.wanted_way:
            if self.wanted_way[1]:  # во избежания деления на 0
                add_angle = degrees(atan(self.wanted_way[0] / self.wanted_way[1]))  # через тангенс вычисляем угол
            else:
                add_angle = 0

            if add_angle < 0:
                add_angle += 90

            x, y = tuple(map(lambda c: int(c > 0), self.wanted_way))    # если (-x, +y), то (False, True)
            # при вычислении угла использовалась формула операции XOR
            self.finite_angle = 180 * y + 90 * (1 - y - x + 2 * x * y) + add_angle

    def update(self, delay, group):
        if self.animations_state['death']:  # если мертвы, пропускаем кадр
            self.waiting_timer = 1

        self.basic_entity_update(delay)
        self.basic_actor_update(group)

        if self.waiting_timer:  # если таймер ожидания
            self.wanted_way.update(0, 0)
        else:
            self.rotate_to_path()
            self.routing(delay)

        self.waiting_timer = max(0, self.waiting_timer - 1)


class Bullet(Entity):   # класс пули
    def __init__(self, start_pos, file_name, groups, direction, angle):
        Entity.__init__(self, start_pos, file_name, groups)

        self.vectors.direction.update(direction)
        self.vectors.direction /= 5  # уменьшение скорости в 5 раз

        self.finite_angle, self.angle = angle, angle + 1  # устанавливаем угол
        self.damage = 1  # урон
        self.set_angle(1)  # разворачиваем пулю

    def motion(self, slowdown):
        self.add_rect.topleft += self.vectors.direction * slowdown
        self.rect.topleft = self.add_rect.topleft + self.rect_correction

    def update(self, delay, group):
        self.basic_entity_update(delay)

        if self.get_wall_collision(group, check_collision=True):    # столкнулись со стеной
            self.kill()
        else:
            shot_actor = self.check_entity_collision()  # в кого прилетела пуля

            if shot_actor:
                shot_actor.hp = max(0, shot_actor.hp - self.damage)  # вычитаем очки здоровья
                shot_actor.animations_state['damage'] = 6   # начинаем ему анимацию урона

                self.kill()


class Vectors:  # содержит direction (пример [5.5, -4.5]) и его аналог velocity, но под модулем (пример [5.5, 4.5])
    def __init__(self, direction=()):
        self.direction = pygame.Vector2(*direction)

    @property
    def velocity(self):
        return pygame.Vector2(*map(abs, self.direction))

    @velocity.setter
    def velocity(self, value):
        direction_mask = pygame.Vector2(*map(lambda x: bool(x >= 0) * 2 - 1, self.direction))

        self.direction = direction_mask.elementwise() * value
