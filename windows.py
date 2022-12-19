from button import Button
from game import Game
import pygame

EXTRA_WIDTH, EXTRA_HEIGHT = 600, 400
background_color = (255, 255, 255)


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

        easy_button = Button((center_x, 25), self.button_image, 'easy')
        medium_button = Button((center_x, 150), self.button_image, 'medium')
        hard_button = Button((center_x, 275), self.button_image, 'hard')

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

        start_button = Button((center_x, 50), self.button_image, 'start game')
        continue_button = Button((center_x, 250), self.button_image, 'continue game')

        super().__init__((start_button, continue_button))

    @staticmethod
    def action(button_text):
        pygame.display.quit()

        if button_text == 'start game':
            SettingsWindow()
        elif button_text == 'continue game':
            pass

    def draw(self):
        self.screen.fill(background_color)

        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.update()


if __name__ == '__main__':
    StartWindow()
