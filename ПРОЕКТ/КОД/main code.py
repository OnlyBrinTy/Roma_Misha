import pygame


class App:
    def __init__(self):
        self.velocity_x = 0
        self.velocity_y = 0
        pygame.init()
        size = self.width, self.height = 701, 701  # screen size
        self.screen = pygame.display.set_mode(size)  # creating screen
        self.clock = pygame.time.Clock()  # creating clock
        self.fps = 60  # setting fps
        self.all_sprites = pygame.sprite.Group()  # adding all sprites to one group
        self.running = True  # allowing program to run

    def main(self):
        hero_x = 50
        hero_y = 50

        while self.running:  # main running cycle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # shutting down program if we close main window
                    self.running = False  # shutting program down

            self.screen.fill((0, 0, 0))  # filling screen with black
            pygame.draw.rect(self.screen, (150, 150, 150), (hero_x, hero_y, 50, 50), 5)
            self.all_sprites.draw(self.screen)  # drawing all sprites on the screen
            self.all_sprites.update()  # updating all sprites
            pygame.display.flip()  # flipping screen
            self.clock.tick(self.fps)  # setting clock tick to fps value


class Main_Hero:
    # todo основные харрактеристики персонажа
    # todo например макс скорость или размер инвентаря
    pass


class Npc:
    # todo хранит в себе всех враждебных и мирных npc
    pass


class Field:
    # todo хранит в себе список возможных локаций
    # todo так же их размер и макс кол-во допустимых npc на каждой из локаций
    pass


class Weapons:
    # todo виды разных оружий
    pass


class Bullet:
    # todo виды пуль для разных оружий
    pass


if __name__ == '__main__':
    app = App()
    app.main()
