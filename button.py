import pygame
pygame.init()


class Button:
    def __init__(self, position, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.clicked = False

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))



# screen = pygame.display.set_mode((1000, 1000))
# image = pygame.image.load('nnnnn.png')
# button = Button((500, 500), image)
#
# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             break
#         elif event.type == pygame.MOUSEBUTTONDOWN:
#             if button.rect.collidepoint(event.pos):
#                 print('yes')
#             else:
#                 print(0)
#
#     button.draw(screen)
#     pygame.display.update()
#     pygame.time.delay(1000)
