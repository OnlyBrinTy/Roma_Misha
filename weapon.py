import pygame

pygame.init()
text_color = (3, 112, 207)
background_color = (255, 255, 255)


class Weapon:
    def __init__(self, screen):
        self.screen = screen
        bullet = BulletAmount()
        bullet_amo = bullet.get_bullet()
        self.font = pygame.font.Font('assets/pixeboy.ttf', 35)

        amo_label = self.font.render(str(bullet_amo), True, text_color)
        self.screen.blit(amo_label, (10, 10))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if bullet_amo > 0:
                            self.draw(bullet_amo)

    def draw(self, bullet_amo):
        amo_label = self.font.render(str(bullet_amo), True, text_color)
        self.screen.blit(amo_label, (10, 10))


class CurrentWeapon:
    pass


class Bullet(pygame.sprite.Sprite):
    pass


class BulletAmount:
    def __init__(self):
        self.bullet = 10
        self.font = pygame.font.Font('assets/pixeboy.ttf', 35)

    def get_bullet(self):
        self.bullet -= 1
        amo_label = self.font.render(str(self.bullet), True, text_color)

        return amo_label
