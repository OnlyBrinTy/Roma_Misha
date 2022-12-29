from rectangle import Rect
import pygame


class Texture:
    def __init__(self, blit_pos, image):
        # есть _original_image - это вид картинки по умолчанию(без наклона).
        # Нужна на случай, если картинка крутится
        # image это конечный вариант картинки. Возможно с разворотом
        self._original_image = self.image = image
        # вместо встроенного в pygame rect я использую свой аналог.
        # Он отличается тем, что он поддерживает дробные числа в координатах.
        self.rect = Rect(self.image, topleft=blit_pos)
        self.blit_pos = blit_pos    # координаты для отрисовки в Camera.

    def set_angle(self, angle):
        self.image = pygame.transform.rotate(self._original_image, angle)
        half_w = self.image.get_width() // 2
        half_h = self.image.get_height() // 2

        self.blit_pos = self.rect.x - half_w + self.rect.width // 2, self.rect.y - half_h + self.rect.height // 2
