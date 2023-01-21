import pygame


class Cursor:   # класс для отрисовки прицела
    image = pygame.image.load('assets/cursor.png')
    offset = pygame.Vector2(image.get_size()) // 2

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos:   # если мышь в окне
            screen.blit(self.image, mouse_pos - self.offset)
            pygame.mouse.set_visible(0)  # делаем курсор невидимым
        else:
            pygame.mouse.set_visible(1)  # делаем курсор видимым


class HpLabel:  # для отображения кол-ва жизней
    font = pygame.font.Font('assets/pixeboy.ttf', 70)

    def __init__(self, player):
        self.player = player

    def draw(self, screen):
        screen.blit(self.font.render(str(self.player.hp), True, 'red'), (10, 60))
