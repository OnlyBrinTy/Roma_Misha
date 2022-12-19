from button import Button
from game import Game
import pygame

WIDTH, HEIGHT = 1400, 1000
EXTRA_WIDTH, EXTRA_HEIGHT = 600, 400
background_color = (41, 52, 80)


class ExtraWindow:
    button_image = pygame.image.load('assets/button.png')

    def __init__(self, buttons=(), labels=()):
        pygame.init()

        self.screen = pygame.display.set_mode((EXTRA_WIDTH, EXTRA_HEIGHT))

        self.labels = labels
        self.buttons = buttons

        while True:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons:
                            if button.rect.collidepoint(event.pos):
                                self.action(button())


class SettingsWindow(ExtraWindow):
    def __init__(self):
        img_rect = self.button_image.get_rect()  # Размеры картинки
        center_x = (EXTRA_WIDTH - img_rect.width) // 2  # координата х для центрального расположения

        easy_button = Button((center_x, 30), self.button_image, 'easy')  # Кнопка для легкой сложности
        medium_button = Button((center_x, 154), self.button_image, 'medium')  # Кнопка для средней сложности
        hard_button = Button((center_x, 278), self.button_image, 'hard')  # Кнопка для хардкора

        super().__init__((easy_button, medium_button, hard_button))

    @staticmethod
    def action(button_text):
        pygame.display.quit()

        difficulty = {'easy': 1, 'medium': 2, 'hard': 3}[button_text]

        Game()

    def draw(self):
        self.screen.fill(background_color)

        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.update()


class StartWindow(ExtraWindow):
    def __init__(self):
        img_rect = self.button_image.get_rect()  # Размеры картинки
        center_x = (EXTRA_WIDTH - img_rect.width) // 2  # координата х для центрального расположения

        start_button = Button((center_x, 69), self.button_image, 'start')
        continue_button = Button((center_x, 232), self.button_image, 'continue')

        super().__init__((start_button, continue_button))

    @staticmethod
    def action(button_text):
        pygame.display.quit()

        if button_text == 'start':  # Обработка нажатия на кнопку start
            SettingsWindow()
        elif button_text == 'continue':  # Обработка нажатия на кнопку continue
            pass

    def draw(self):
        self.screen.fill(background_color)

        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.update()


class MenuWindow(ExtraWindow):
    pass


class UpgradeWindow(ExtraWindow):
    pass


if __name__ == '__main__':
    StartWindow()
