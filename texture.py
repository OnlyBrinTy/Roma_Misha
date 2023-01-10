class Texture:
    def __init__(self, blit_pos, image):    # тут и так всё понятно
        self.image = image
        self.rect = self.image.get_rect(center=blit_pos)
