from spritesheet import SpriteSheet


class StaticObject:
    def __init__(self, sprites, rects, pos):
        self.sprites = sprites
        self.pos = pos
        self.rects = rects
        self.x, self.y = pos
        self.animated = type(sprites[0]) == list
        self.room = None

    def getPos(self):
        return self.pos

    def setPos(self, pos):
        self.x, self.y = pos
        self.pos = pos

    def get_sprite(self):
        return self.sprites[0]

    def i_am_at(self):
        return [self.pos]

    def draw(self, screen):
        print (f"This doesn't really get called, does it?")
        screen.blit(self.sprite, self.rect)

    def get_real_pos(self):
        sx = self.x + self.y
        sy = self.y - self.x
        return (sy, sx)

    def in_room(self, x, y):
        if x < 0 or y < 0:
            return False
        if x >= self.room.width or y >= self.room.height:
            return False
        return (x, y) in self.room.good_spaces

    def get_rect(self):
        return self.rect

    def __lt__(self, other):
        return self.get_real_pos() < other.get_real_pos()


class Pillar(StaticObject):
    def __init__(self, pos):
        sprites = SpriteSheet(
            "iso-64x64-outside.png").load_strip((202, 811, 41, 71), 1, colorkey=-1)
        super().__init__(sprites, None, pos)
        self.sprite = sprites[0]
        self.rect = (0, 0, 41, 71)
        self.room = None
