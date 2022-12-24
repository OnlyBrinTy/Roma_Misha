<<<<<<< HEAD
import pygame
pygame.init()

text_color = (247, 239, 174)


class Button:
    def __init__(self, position, image, text):
        self.text = text
        self.image = image
        self.rect = self.image.get_rect(topleft=position)   # Прямоугольник картинки

        # Настройка шрифтов и размеров
        font = int(self.rect.width // len(self.text) * 1.5)
        font = pygame.font.Font('assets/pixeboy.ttf', font)
        self.label = font.render(self.text, True, text_color)

        label_width, label_height = font.size(self.text)  # Размеры текста
        # Центрирование текста в кнопке
        self.label_x = self.rect.x + (self.rect.width - label_width) // 2
        self.label_y = self.rect.y + (self.rect.height - label_height) // 2

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        screen.blit(self.label, (self.label_x, self.label_y))

    def __call__(self):
        return self.text
=======
import pygame
pygame.init()

text_color = (247, 239, 174)


class Button:
    def __init__(self, position, image, text):
        self.text = text
        self.image = image
        self.rect = self.image.get_rect(topleft=position)   # Прямоугольник картинки

        # Настройка шрифтов и размеров
        font = int(self.rect.width // len(self.text) * 1.5)
        font = pygame.font.Font('assets/pixeboy.ttf', font)
        self.label = font.render(self.text, True, text_color)

        label_width, label_height = font.size(self.text)  # Размеры текста
        # Центрирование текста в кнопке
        self.label_x = self.rect.x + (self.rect.width - label_width) // 2
        self.label_y = self.rect.y + (self.rect.height - label_height) // 2

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        screen.blit(self.label, (self.label_x, self.label_y))

    def __call__(self):
        return self.text
>>>>>>> 08f8f5a (changed movement system (not made up to end))
