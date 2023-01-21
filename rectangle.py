class AddList(list):    # по сути обычный список, но его можно складывать и вычитать
    def __add__(self, other):
        return AddList([mine + addon for mine, addon in zip(self, other)])

    def __sub__(self, other):
        return AddList([mine - addon for mine, addon in zip(self, other)])

    def __iadd__(self, other):
        for i, addition in enumerate(other):
            self[i] += addition

        return self

    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1]

    def __isub__(self, other):
        for i, addition in enumerate(other):
            self[i] -= addition

        return self


class Rect:  # то же что и pygame.rect только с дробными числами
    def __init__(self, rect):
        self.width = rect.width
        self.height = rect.height
        self.h_width = self.width / 2
        self.h_height = self.height / 2
        self.x, self.y = rect.topleft

    @property
    def topleft(self):
        return AddList([self.x, self.y])

    @topleft.setter
    def topleft(self, value):
        self.x, self.y = value

    @property
    def center(self):
        return AddList([self.x + self.h_width, self.y + self.h_height])

    @center.setter
    def center(self, value):
        self.x = value[0] - self.h_width
        self.y = value[1] - self.h_height
