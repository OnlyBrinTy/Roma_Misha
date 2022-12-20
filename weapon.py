import pygame

pygame.init()
text_color = (3, 112, 207)
background_color = (255, 255, 255)


class Weapon:
    def __init__(self):
        self.screen = pygame.display.set_mode((400, 400))
        self.screen.fill((255, 255, 255))
        self.bullet_amo = 10
        self.font = pygame.font.Font('assets/pixeboy.ttf', 35)

        amo_label = self.font.render(str(self.bullet_amo), True, text_color)
        self.screen.blit(amo_label, (10, 10))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.bullet_amo > 0:
                            self.bullet_amo -= 1
                            self.draw(self.screen, self.bullet_amo)

    def draw(self, screen, bullet_amo):
        screen.fill(background_color)
        amo_label = self.font.render(str(bullet_amo), True, text_color)
        screen.blit(amo_label, (10, 10))

        pygame.display.update()


Weapon()
