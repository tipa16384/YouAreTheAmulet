from abc import abstractmethod
from spritesheet import SpriteSheet
import random
from enum import Enum

class TileType(Enum):
    FLOOR = 0
    WALL = 1
    OUTSIDE = 2
    ROOM = 3,
    GRASS = 4

class TerrainTileFactory:
    def create_terrain_tile(tileType: TileType):
        if tileType == TileType.OUTSIDE:
            return OutsideTile()
        elif tileType == TileType.ROOM:
            return RoomTile()
        elif tileType == TileType.GRASS:
            return GrassTile()
        else:
            raise Exception("Invalid tile type")

class TerrainTile:
    def __init__(self, width, full_height, surface_height):
        self.width = width
        self.full_height = full_height
        self.surface_height = surface_height
        self.images = []
    
    @abstractmethod
    def choose_random_image(self):
        pass

class OutsideTile(TerrainTile):
    def __init__(self):
        super().__init__(64, 64, 32)
        outside_64_sprites = SpriteSheet('iso-64x64-outside.png')
        self.images = outside_64_sprites.load_strip((64, 448, 64, 64), 9, colorkey=-1)
        self.images += outside_64_sprites.load_strip((0, 384, 64, 64), 6, colorkey=-1)
    
    def choose_random_image(self):
        if (random.randint(0, 15) == 0):
            return self.images[random.randint(9, len(self.images)-1)]
        return self.images[random.randint(0, 8)]

class GrassTile(TerrainTile):
    def __init__(self):
        super().__init__(64, 51, 32)
        outside_64_sprites = SpriteSheet('iso-64x64-outside.png')
        self.images = [outside_64_sprites.image_at((256, 718, 64, 51), colorkey=-1)]
    
    def choose_random_image(self):
        return self.images[0]

class RoomTile(TerrainTile):
    def __init__(self):
        super().__init__(64, 64, 32)
        inside_sprites = SpriteSheet('iso-64x64-building_3.png')
        self.images = [inside_sprites.image_at((0, 0, 64, 64), colorkey=-1)]
    
    def choose_random_image(self):
        return self.images[0]

