class AddList(list):
    def __add__(self, other):
        return AddList([mine + addon for mine, addon in zip(self, other)])

    def __iadd__(self, other):
        for i, addition in enumerate(other):
            self[i] += addition

        return self


class Rect:
    def __init__(self, image, **kwargs):
        self._rect = image.get_rect(**kwargs)

        self.width = self._rect.width
        self.height = self._rect.height
        self.h_width = self.width / 2
        self.h_height = self.height / 2
        self.x, self.y = self._rect.topleft

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
