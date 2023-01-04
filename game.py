from entities import AnotherThread, Player
from math import atan, degrees
from map import Map
import weapon
import pygame

BACKGROUND_COLOR = '#71ddee'
WIDTH, HEIGHT = 1280, 720
FPS = 120


class Camera(pygame.sprite.GroupSingle):
    offset = pygame.math.Vector2()

    def camera_centering(self):   # установка сдвига камеры так, чтобы игрок оказался по центру
        self.offset.x = self.sprite.add_rect.center[0] - WIDTH // 2
        self.offset.y = self.sprite.add_rect.center[1] - HEIGHT // 2

    def draw(self, groups, interface, screen):
        self.camera_centering()

        screen.fill(BACKGROUND_COLOR)   # заливка фона
        i = 0
        for group in groups:    # каждый спрайт выводится на экран друг за другом с учётом сдвига камеры
            for sprite in group.sprites():
                screen.blit(sprite.image, sprite.rect.topleft - self.offset)
            # следующие комменты можешь удалить

            # if i:
            #     for sprite in group.sprites():
            #         if sprite.rect.topleft != tuple(map(int, sprite.add_rect.topleft + sprite.rect_correction)):
            #             print(sprite.rect.topleft, tuple(map(int, sprite.add_rect.topleft + sprite.rect_correction)))
            #
            #         screen.blit(sprite.image, sprite.rect.topleft - self.offset)
            # else:
            #     for sprite in group.sprites():
            #         screen.blit(sprite.image, sprite.rect.topleft - self.offset)

            i += 1

        for texture in interface:
            screen.blit(texture.image, texture.blit_pos)

        # следующие комменты можешь удалить

        # pygame.draw.rect(screen, 'purple', (*self.sprite.rect.topleft - self.offset, *self.sprite.rect.size), 1)
        # pygame.draw.rect(screen, 'green', (0, 0, *self.sprite.rect.size), 1)
        #
        # for sprite in groups[0].sprites():
        #     if sprite.kind == 1 and pygame.sprite.collide_mask(self.sprite, sprite):
        #         # colpoint = self.sprite.mask.overlap(sprite.mask, (-10, -10))
        #         x, y = sprite.rect.topleft - pygame.Vector2(self.sprite.rect.topleft)
        #         # if type(colpoint) is tuple:
        #             # pygame.draw.rect(screen, 'blue', (*colpoint, x, y))
        #
        #         colmask = self.sprite.mask.overlap_mask(sprite.mask, (x, y))
        #         screen.blit(colmask.to_surface(), (200, 0))

        # olist = self.sprite.mask.outline()
        # pygame.draw.lines(screen, (200, 150, 150), 1, olist)

        # b_rects = self.sprite.mask.get_bounding_rects()
        #
        # for b_rect in b_rects:
        #     pygame.draw.rect(screen, 'green', (*b_rect.topleft + self.offset, *b_rect.size), 1)

        pygame.display.update()


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)

        self.camera = Camera()  # через камеру происходит отображение всего на экране
        self.entities = pygame.sprite.Group()   # все движущиеся существа в игре (даже пули)
        self.map = Map('test_level.txt')

        self.player = Player((50 * 17, 50 * 5), 'assets/player.png', (self.camera, self.entities))
        self.interface = []
        # в interface лежат текстуры, которые будут затем выводится на экран без учёта сдвига

        self.thread = AnotherThread(self.map, self.camera)
        self.thread.start()

        weap = weapon.BulletAmount()

        clock = pygame.time.Clock()
        running = True

        while running:
            self.thread.update_groups.set()  # делаем запрос на обновление персонажа (устанавливаем флажок на True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.thread.terminated.set()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.screen.blit(weap.get_bullet(), (100, 100))
                elif event.type == pygame.MOUSEMOTION:
                    self.player.set_angle(self.check_angle(event.pos))

            while self.thread.update_groups.is_set():  # ждём пока персонаж не обработает своё положение
                pass

            self.camera.draw((self.map, self.entities), self.interface, self.screen)

            clock.tick(FPS)

    def check_angle(self, mouse_pos):   # определение угла поворота в зависимости от положения мыши
        quarters = {(True, False): 0, (False, False): 1, (False, True): 2, (True, True): 3}

        x_dist, y_dist = mouse_pos - pygame.Vector2(self.player.add_rect.center - self.camera.offset)
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
