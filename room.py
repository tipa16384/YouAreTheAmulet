from spritesheet import SpriteSheet
import pygame
import random

room_sprites = None
wall_sprites = None
room_sprite_width = 64
room_sprite_height = 32
room_floor_width = 32
room_floor_height = 16
room_floor_sprite_height = 23
wall_height = 3

def init_rooms():
    global room_sprites, wall_sprites, new_room_sprites, floor_64_sprites, outside_64_sprites
    room_sprites = SpriteSheet('small-interior.png')
    wall_sprites = SpriteSheet('tempwalls.png')
    new_room_sprites = SpriteSheet('IsoTacticsTileset_by_SecretHideout_V1.1.png')
    floor_64_sprites = SpriteSheet('iso-64x64-building_3.png')
    outside_64_sprites = SpriteSheet('iso-64x64-outside.png')

def screen_coords(x, y):
    sx = (x+y)*room_sprite_width//2
    sy = (y-x)*room_sprite_height//2
    return (sx, sy)

def screen_floor_coords(x, y):
    sx = (x+y)*room_floor_width//2
    sy = (y-x)*room_floor_height//2
    return (sx, sy)

class Room:
    def __init__(self, width: int, height: int, floor_type: str):
        self.width = width
        self.height = height
        self.floor_type = outside_64_sprites.load_strip((64, 448, 64, 64), 9, colorkey=-1)
        self.wall_type = new_room_sprites.image_at((64, 41, 32, 23), colorkey=-1)
        self.left_wall = wall_sprites.image_at((0, 0, 32, 48), colorkey=-1)
        self.right_wall = pygame.transform.flip(self.left_wall, True, False)
        self.bottom_wall = wall_sprites.image_at((0, 0, 32, 48), colorkey=-1)
        self.bottom_wall.set_alpha(64)
        self.left_bottom_wall = pygame.transform.flip(self.bottom_wall, True, False)
        self.actors = []
        self.seed = random.randint(0, 1000000)
    
    def choose_floor_type(self):
        return self.floor_type[random.randint(0, 8)]
        # roll20 = random.randint(0, 20)
        # if roll20 < 10:
        #     return self.floor_type[0]
        # elif roll20 < 15:
        #     return self.floor_type[1]
        # elif roll20 < 18:
        #     return self.floor_type[2]
        # else:
        #     return self.floor_type[3]

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
        maxx, maxy = screen_floor_coords(self.width*2, self.height*2)
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
                rx, ry = self.rotate(x, y, nrot)
                bx, by = screen_coords(rx, ry)
                surface.blit(self.choose_floor_type(), (bx+dx, by+dy))
        
        ssize = 64

        for actor in sorted(self.actors):
            actor.setRotation(nrot)
            rx, ry = self.rotate(actor.x, actor.y, nrot)
            sx, sy = screen_coords(rx, ry)
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
