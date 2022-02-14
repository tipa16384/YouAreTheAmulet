from spritesheet import SpriteSheet
import pygame
from actor import Babus, Archer

room_sprites = None
wall_sprites = None
room_sprite_width = 64
room_sprite_height = 32
wall_height = 4

def init_rooms():
    global room_sprites, wall_sprites
    room_sprites = SpriteSheet('.\\small-floor-tiles\\Interior\\small-interior.png')
    wall_sprites = SpriteSheet('.\\small-floor-tiles\\Interior\\tempwalls.png')

def screen_coords(x, y):
    sx = (x+y)*room_sprite_width//2
    sy = (y-x)*room_sprite_height//2
    return (sx, sy)

class Room:
    def __init__(self, width: int, height: int, floor_type: str):
        self.width = width
        self.height = height
        x = int(floor_type[0]) * room_sprite_width
        y = int(floor_type[1]) * room_sprite_height
        self.floor_type = room_sprites.image_at((x, y, room_sprite_width, room_sprite_height), colorkey=-1)
        self.first_floor_type = room_sprites.image_at((room_sprite_width, y, room_sprite_width, room_sprite_height), colorkey=-1)
        self.left_wall = wall_sprites.image_at((0, 0, 32, 48), colorkey=-1)
        self.right_wall = pygame.transform.flip(self.left_wall, True, False)
        self.actors = [Babus((1,3)), Archer((2,3))]

        self.actors[0].setFacing(1)
        self.actors[1].setFacing(-1)
    
    def rotate(self, x, y, rotation):
        if rotation == 0:
            return x, y
        elif rotation == 1:
            return self.height - y - 1, x
        elif rotation == 2:
            return self.width - x - 1, self.height - y - 1
        elif rotation == 3:
            return y, self.width - x - 1

    def draw(self, surface, rotation=0):
        nrot = rotation % 4
        screen_width, screen_height = surface.get_size()
        maxx, maxy = screen_coords(self.width, self.height)
        dx = (screen_width - maxx) // 2
        dy = (screen_height - maxy) // 2

        for x in range(self.width):
            for y in range(self.height):
                rx, ry = self.rotate(x, y, nrot)
                bx, by = screen_coords(rx, ry)
                surface.blit(self.first_floor_type if (x,y) == (2,0) else self.floor_type, (bx+dx, by+dy))
        
        for x in range(self.height if nrot & 1 else self.width):
            bx, by = screen_coords(x, 0)
            for wy in range(wall_height):
                surface.blit(self.left_wall, (bx+dx, by+dy-32-32*wy))
        
        for y in range(self.width if nrot & 1 else self.height):
            bx, by = screen_coords((self.height if nrot & 1 else self.width)-1, y)
            for wy in range(wall_height):
                surface.blit(self.right_wall, (bx+dx+32, by+dy-32-32*wy))
        
        ssize = 64

        for actor in sorted(self.actors):
            actor.setRotation(nrot)
            rx, ry = self.rotate(actor.x, actor.y, nrot)
            sx, sy = screen_coords(rx, ry)
            sprite = actor.get_sprite()
            rects = actor.get_rect()
            surface.blit(
                sprite, (sx + dx + (ssize-rects[2])//2, sy + dy - rects[3]+ssize//3))
