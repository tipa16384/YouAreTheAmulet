import random
from terraintile import TileType, TerrainTileFactory
from spritesheet import SpriteSheet


class Room:
    def __init__(self, width: int, height: int, floor_type: TileType):
        self.width = width
        self.height = height
        self.floor_type = floor_type
        self.floor_tile = TerrainTileFactory.create_terrain_tile(floor_type)
        self.seed = random.randint(0, 1000000)
        self.exit_ns = SpriteSheet("portals.png").image_at(
            (15, 9, 32, 47), colorkey=-1)
        self.exit_ew = SpriteSheet("portals.png").image_at(
            (54, 9, 32, 48), colorkey=-1)

    def screen_coords(self, x, y):
        sx = (x+y)*self.floor_tile.width//2
        sy = (y-x)*self.floor_tile.surface_height//2
        return (sx, sy)

    def rotate(self, x, y, rotation):
        if rotation == 0:
            return x, y
        elif rotation == 1:
            return self.height - y - 1, x
        elif rotation == 2:
            return self.width - x - 1, self.height - y - 1
        elif rotation == 3:
            return y, self.width - x - 1

    def draw(self, surface, actors, exits):
        screen_width, screen_height = surface.get_size()
        maxx, maxy = self.screen_coords(self.width, self.height)
        dx = (screen_width - maxx) // 2
        dy = (screen_height - maxy) // 2

        random.seed(self.seed)

        ex = self.width // 2
        ey = self.height // 2

        exits_to_draw = [connection for exit in exits for connection in exit.connections if connection[0] == self]

        for exit in exits_to_draw:
            if exit[2] == -1:
                ex = exit[1]
                bx, by = self.screen_coords(ex, -1)
                surface.blit(self.floor_tile.choose_random_image(), (bx+dx, by+dy))
                bx, by = self.screen_coords(ex+1, -1.1)
                surface.blit(self.exit_ns, (bx+dx, by+dy))

            elif exit[1] == self.width:
                ey = exit[2]
                bx, by = self.screen_coords(self.width, ey)
                surface.blit(self.floor_tile.choose_random_image(), (bx+dx, by+dy))
                bx, by = self.screen_coords(self.width+0.6, ey-0.5)
                surface.blit(self.exit_ew, (bx+dx, by+dy))

        for x in range(self.width-1, -1, -1):
            for y in range(self.height):
                bx, by = self.screen_coords(x, y)
                surface.blit(
                    self.floor_tile.choose_random_image(), (bx+dx, by+dy))

        ssize = 64

        for actor in sorted(actors):
            sx, sy = self.screen_coords(actor.x, actor.y)
            sprite = actor.get_sprite()
            rects = actor.get_rect()
            surface.blit(
                sprite, (sx + dx + (ssize-rects[2])//2, sy + dy - rects[3]+ssize//3))

        for exit in exits_to_draw:
            if exit[2] == self.height:
                ex = exit[1]
                bx, by = self.screen_coords(ex, self.height)
                surface.blit(self.floor_tile.choose_random_image(), (bx+dx, by+dy))
                bx, by = self.screen_coords(ex+1, self.height-0.9)
                surface.blit(self.exit_ns, (bx+dx, by+dy))

            elif exit[1] == -1:
                ey = exit[2]
                bx, by = self.screen_coords(-1, ey)
                surface.blit(self.floor_tile.choose_random_image(), (bx+dx, by+dy))
                bx, by = self.screen_coords(0.4, ey-0.5)
                surface.blit(self.exit_ew, (bx+dx, by+dy))
