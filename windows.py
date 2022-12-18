from button import Button
import pygame
pygame.init()

WIDTH, HEIGHT = 1400, 1000
EXTRA_WIDTH, EXTRA_HEIGHT = 600, 400


class ExtraWindow:
    screen = pygame.display.set_mode((EXTRA_WIDTH, EXTRA_HEIGHT))
    button_image = pygame.image.load('assets/button.png')

    def __init__(self):
        img_rect = self.button_image.get_rect()  # Размеры картинки
        center_x = (EXTRA_WIDTH - img_rect.width) // 2  # координата х для центрального расположения

        self.start_button = Button((center_x, 50), self.button_image, 'Start Game')
        self.continue_button = Button((center_x, 250), self.button_image, 'Continue Game')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.rect.collidepoint(event.pos):
                        print('begin')
                    elif self.continue_button.rect.collidepoint(event.pos):
                        print('continue')

            self.draw()

    def draw(self):
        self.screen.fill('white')
        self.start_button.draw(self.screen)
        self.continue_button.draw(self.screen)

        pygame.display.update()


if __name__ == '__main__':
    ExtraWindow()
