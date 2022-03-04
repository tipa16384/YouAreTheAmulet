import random
from terraintile import TileType, TerrainTileFactory
from spritesheet import SpriteSheet

class TileObject(object):
    pass
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
        self.name = "Room"
        self.floor_tile_cache = dict()

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
        
    def draw_tiled(self, surface, actors, exits):
        self.floor_tile = TileObject()
        self.floor_tile.width = self.tiled['tilewidth']
        self.floor_tile.height = self.tiled['tileheight']
        self.floor_tile.surface_height = self.tiled['displayheight']

        layer = self.layers[0]['data']

        for flayer in self.layers:
            for sprite_num in set(flayer['data']):
                if sprite_num == 0 or sprite_num in self.floor_tile_cache:
                    continue
                index = sprite_num - self.tiled['firstgid']
                rx = (index % self.tiled['columns']) * self.tiled['tilewidth']
                ry = (index // self.tiled['columns']) * self.tiled['tileheight']
                self.floor_tile_cache[sprite_num] = self.room_sprites.image_at((rx, ry, self.tiled['tilewidth'], self.tiled['tileheight']), colorkey=-1)
                print (f"Cached {sprite_num}")

        screen_width, screen_height = surface.get_size()
        maxx, maxy = self.screen_coords(self.width, self.height)
        dx = (screen_width - maxx) // 2
        dy = (screen_height - maxy) // 2

        ex = self.width // 2
        ey = self.height // 2

        exits_to_draw = [connection for exit in exits for connection in exit.connections if connection[0] == self]

        random.seed(self.seed)

        random_image = self.floor_tile_cache[max(layer)]

        for exit in exits_to_draw:
            if exit[2] == -1:
                ex = exit[1]
                bx, by = self.screen_coords(ex, -1)
                surface.blit(random_image, (bx+dx, by+dy))
                bx, by = self.screen_coords(ex+1, -1.1)
                surface.blit(self.exit_ns, (bx+dx, by+dy))

            elif exit[1] == self.width:
                ey = exit[2]
                bx, by = self.screen_coords(self.width, ey)
                surface.blit(random_image, (bx+dx, by+dy))
                bx, by = self.screen_coords(self.width+0.6, ey-0.5)
                surface.blit(self.exit_ew, (bx+dx, by+dy))
        
        for x in range(self.width-1, -1, -1):
            for y in range(self.height):
                sprite_num = layer[(self.width - 1 - x) * self.height + y]
                if sprite_num == 0:
                    continue
                bx, by = self.screen_coords(x, y)
                surface.blit(self.floor_tile_cache[sprite_num], (bx+dx, by+dy))

        ssize = 64

        layer = self.layers[1]['data'] if len(self.layers) > 1 else None

        sorted_actors = sorted(actors)

        for x in range(self.width-1, -1, -1):
            for y in range(self.height):
                if layer:
                    sprite_num = layer[(self.width - 1 - x) * self.height + y]
                    if sprite_num != 0:
                        bx, by = self.screen_coords(x, y)
                        surface.blit(self.floor_tile_cache[sprite_num], (bx+dx, by+dy))
                for actor in sorted_actors:
                    if actor.x >= x and actor.x < x + 1 and actor.y >= y and actor.y < y + 1:
                        sx, sy = self.screen_coords(actor.x, actor.y)
                        sprite = actor.get_sprite()
                        rects = actor.get_rect()
                        surface.blit(
                            sprite, (sx + dx + (ssize-rects[2])//2, sy + dy - rects[3]+ssize//3))

        for exit in exits_to_draw:
            if exit[2] == self.height:
                ex = exit[1]
                bx, by = self.screen_coords(ex, self.height)
                surface.blit(random_image, (bx+dx, by+dy))
                bx, by = self.screen_coords(ex+1, self.height-0.9)
                surface.blit(self.exit_ns, (bx+dx, by+dy))

            elif exit[1] == -1:
                ey = exit[2]
                bx, by = self.screen_coords(-1, ey)
                surface.blit(random_image, (bx+dx, by+dy))
                bx, by = self.screen_coords(0.4, ey-0.5)
                surface.blit(self.exit_ew, (bx+dx, by+dy))

    def draw(self, surface, actors, exits):
        if self.tiled:
            self.draw_tiled(surface, actors, exits)
            return

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
