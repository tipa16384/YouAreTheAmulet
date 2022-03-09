import random
from terraintile import TileType, TerrainTileFactory
from spritesheet import SpriteSheet
from staticobject import HasPosition, StaticObject
import pygame
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
        self.layers = None
        self.tiled = None
        self.phrases = None

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
        self.floor_lift = self.tiled['lift']

        layer_list = list(layer for layer in self.layers if layer['type'] == 'tilelayer')

        layer = layer_list[0]['data']

        for flayer in layer_list:
            for sprite_num in set(flayer['data']):
                if sprite_num == 0 or sprite_num in self.floor_tile_cache:
                    continue
                index = sprite_num - self.tiled['firstgid']
                rx = (index % self.tiled['columns']) * self.tiled['tilewidth']
                ry = (index // self.tiled['columns']) * self.tiled['tileheight']
                self.floor_tile_cache[sprite_num] = self.room_sprites.image_at((rx, ry, self.tiled['tilewidth'], self.tiled['tileheight']), colorkey=-1)

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
        
        tint_pos = None

        for actor in actors:
            if actor.getIsPlayer():
                if actor.target:
                    tint_pos = actor.target.getPos()
                    tint_color = (0, 255, 0) if actor.in_range else (255, 0, 0)
                break
        
        for x in range(self.width-1, -1, -1):
            for y in range(self.height):
                sprite_num = layer[(self.width - 1 - x) * self.height + y]
                if sprite_num == 0:
                    continue
                bx, by = self.screen_coords(x, y)

                if tint_pos and x == tint_pos[0] and y == tint_pos[1]:
                    tile_copy = self.floor_tile_cache[sprite_num].copy()
                    tile_copy.fill(tint_color, special_flags=pygame.BLEND_RGB_MULT)
                    surface.blit(tile_copy, (bx+dx, by+dy-self.floor_lift))
                else:
                    surface.blit(self.floor_tile_cache[sprite_num], (bx+dx, by+dy-self.floor_lift))

        ssize = 64

        layer = layer_list[1]['data'] if len(layer_list) > 1 else None

        draw_list = []
        draw_list += actors

        if layer:
            for x in range(self.width-1, -1, -1):
                for y in range(self.height):
                        sprite_num = layer[(self.width - 1 - x) * self.height + y]
                        if sprite_num != 0:
                            hp = HasPosition((x-self.offset, y+self.offset))
                            hp.image = self.floor_tile_cache[sprite_num]
                            draw_list.append(hp)

        sorted_actors = sorted(draw_list)

        for actor in sorted_actors:
            if isinstance(actor, StaticObject):
                sx, sy = self.screen_coords(actor.x, actor.y)
                sprite = actor.get_sprite()
                rects = actor.get_rect()
                surface.blit(
                    sprite, (sx + dx + (ssize-rects[2])//2, sy + dy - rects[3]+ssize//3))
            else:
                bx, by = self.screen_coords(actor.x+self.offset, actor.y-self.offset)
                surface.blit(actor.image, (bx+dx, by+dy-self.floor_lift))

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

