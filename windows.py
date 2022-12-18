from button import Button
import pygame

WIDTH, HEIGHT = 1400, 1000
EXTRA_WIDTH, EXTRA_HEIGHT = 600, 400


class ExtraWindow:
    screen = pygame.display.set_mode((EXTRA_WIDTH, EXTRA_HEIGHT))
    button_image = pygame.image.load('assets/button.png')

    def __init__(self, buttons=(), labels=()):
        pygame.init()

        self.labels = labels
        self.buttons = buttons

        self.running = True
        while self.running:
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

        easy_button = Button((center_x, 25), self.button_image, 'easy')
        medium_button = Button((center_x, 150), self.button_image, 'medium')
        hard_button = Button((center_x, 275), self.button_image, 'hard')

        super().__init__((easy_button, medium_button, hard_button))

    def action(self, button_text):
        self.running = False
        if button_text == 'easy':
            pass
        elif button_text == 'medium':
            pass
        elif button_text == 'hard':
            pass

    def draw(self):
        self.screen.fill('white')

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

    def action(self, button_text):
        self.running = False

        if button_text == 'start game':
            SettingsWindow()
        elif button_text == 'continue game':
            pass

    def draw(self):
        self.screen.fill('white')

        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.update()


if __name__ == '__main__':
    StartWindow()
