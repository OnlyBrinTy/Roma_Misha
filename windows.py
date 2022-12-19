from button import Button
import pygame

WIDTH, HEIGHT = 1400, 1000
EXTRA_WIDTH, EXTRA_HEIGHT = 600, 400
background_color = (41, 52, 80)


class ExtraWindow:
    screen = pygame.display.set_mode((EXTRA_WIDTH, EXTRA_HEIGHT))  # Создание экрана с заданными рамерами
    button_image = pygame.image.load('assets/button.png')  # Загрузка заднего фона кнопки

    def __init__(self, buttons=(), labels=()):
        pygame.init()

        self.labels = labels
        self.buttons = buttons

        self.running = True
        while self.running:  # Игровой цикл
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
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

    def action(self, button_text):  # Обработка нажатий на кнопки
        self.running = False
        if button_text == 'easy':
            pass
        elif button_text == 'medium':
            pass
        elif button_text == 'hard':
            pass

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

    def action(self, button_text):
        self.running = False

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
