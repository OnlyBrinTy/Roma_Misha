import pygame
pygame.init()


class Button:
    def __init__(self, position, image, text):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.clicked = False

        font = int(self.rect.width // len(text) * 1.5)
        font = pygame.font.Font('assets/pixeboy.ttf', font)
        self.text = font.render(text, True, 'white')

        text_width, text_height = font.size(text)
        self.text_x = self.rect.x + (self.rect.width - text_width) // 2
        self.text_y = self.rect.y + (self.rect.height - text_height) // 2

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        screen.blit(self.text, (self.text_x, self.text_y))



screen = pygame.display.set_mode((1000, 1000))
image = pygame.image.load('assets/button.png')
button = Button((500, 500), image, 'Start Game')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button.rect.collidepoint(event.pos):
                print('yes')
            else:
                print(0)

    button.draw(screen)
    pygame.display.update()
    pygame.time.delay(1000)
