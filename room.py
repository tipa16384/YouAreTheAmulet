import random
from terraintile import TileType, TerrainTileFactory

wall_height = 3

def init_rooms():
    pass

class Room:
    def __init__(self, width: int, height: int, floor_type: str):
        self.width = width
        self.height = height
        self.floor_type = TerrainTileFactory.create_terrain_tile(TileType.OUTSIDE)
        self.seed = random.randint(0, 1000000)
    
    def screen_coords(self, x, y):
        sx = (x+y)*self.floor_type.width//2
        sy = (y-x)*self.floor_type.surface_height//2
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

    def draw(self, surface, actors):
        screen_width, screen_height = surface.get_size()
        maxx, maxy = self.screen_coords(self.width, self.height)
        dx = (screen_width - maxx) // 2
        dy = (screen_height - maxy) // 2
        
        # for x in range(self.width*2, -2, -1):
        #     bx, by = screen_floor_coords(x, -1)
        #     for wy in range(-wall_height, 0):
        #         surface.blit(self.wall_type, (bx+dx, by+dy-(room_floor_sprite_height - room_floor_height)*wy))
        
        # for y in range(self.height * 2):
        #     bx, by = screen_floor_coords(self.width * 2, y)
        #     for wy in range(-wall_height, 0):
        #         surface.blit(self.wall_type, (bx+dx, by+dy-(room_floor_sprite_height - room_floor_height)*wy))

        random.seed(self.seed)

        for x in range(self.width-1, -1, -1):
            for y in range(self.height):
                bx, by = self.screen_coords(x, y)
                surface.blit(self.floor_type.choose_random_image(), (bx+dx, by+dy))
        
        ssize = 64

        for actor in sorted(actors):
            sx, sy = self.screen_coords(actor.x, actor.y)
            sprite = actor.get_sprite()
            rects = actor.get_rect()
            surface.blit(
                sprite, (sx + dx + (ssize-rects[2])//2, sy + dy - rects[3]+ssize//3))
        
        # for y in range(self.height * 2):
        #     bx, by = screen_floor_coords(-1, y)
        #     for wy in range(-wall_height, 0):
        #         surface.blit(self.wall_type, (bx+dx, by+dy-(room_floor_sprite_height - room_floor_height)*wy))

        # for x in range(self.width*2, -2, -1):
        #     bx, by = screen_floor_coords(x, self.height * 2)
        #     for wy in range(-wall_height, 0):
        #         surface.blit(self.wall_type, (bx+dx, by+dy-(room_floor_sprite_height - room_floor_height)*wy))
