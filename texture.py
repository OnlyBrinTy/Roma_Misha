class Texture:
    def __init__(self, blit_pos, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=blit_pos)
        self.blit_pos = blit_pos
