class Texture:
    def __init__(self, position, image):    # тут и так всё понятно
        self.image = image
        self.rect = self.image.get_rect(center=position)
