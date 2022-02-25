from spritesheet import SpriteSheet
import pygame
import heapq
from staticobject import StaticObject
from math import sqrt, pow

__facing_deltas__ = [(0,-1), (1,0), (0,1), (-1,0)]

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def distance(a, b):
    return round(sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2)))

class Actor(StaticObject):
    def __init__(self, sprites, rects, pos, facing=3):
        super().__init__(sprites, rects, pos)
        self.facing = facing
        self.dx = 0
        self.dy = 0
        self.path_start = None
        self.path_end = None
        self.speed = 16
        self.moving = False
        self.move_queue = list()
        self.frame = 0
        self.is_player = False
        self.name = "Actor"

    def getMoving(self):
        return self.moving

    def get_facing_delta(self):
        return __facing_deltas__[self.facing % len(__facing_deltas__)]

    def setIsPlayer(self, is_player):
        self.is_player = is_player
    
    def getIsPlayer(self):
        return self.is_player

    def setFacing(self, facing):
        self.facing = facing
    
    def face_player(self, px, py):
        if not self.moving:
            self.face_at(px, py)

    def face_at(self, px, py):
        dx = px - self.x
        dy = py - self.y

        if (dx == 0 and dy < 0) or (dy < 0 and abs(dx) <= abs(dy)):
            self.facing = 0
        elif (dx == 0 and dy > 0) or (dy > 0 and abs(dx) <= abs(dy)):
            self.facing = 2
        elif (dx > 0 and dy == 0) or (dx > 0 and abs(dx) > abs(dy)):
            self.facing = 1
        else:
            self.facing = 3

    def getFacing(self):
        return self.facing

    def animate(self):
        self.frame += 1

    def getRotatedFacing(self):
        return self.facing % 4

    def get_rect(self):
        return self.rects[self.getRotatedFacing()]

    def get_sprite(self):
        if not self.animated:
            return self.sprites[self.getRotatedFacing()]
        else:
            return self.sprites[self.getRotatedFacing()][self.frame % len(self.sprites[self.getRotatedFacing()])]

    def i_am_at(self):
        if self.moving:
            return [self.path_end, self.path_start]
        else:
            return [self.pos]

    def update(self):
        if self.moving:
            self.move()
        else:
            self.dx = 0
            self.dy = 0
        self.x += self.dx
        self.y += self.dy
        self.pos = (int(self.x), int(self.y))

    def move(self):
        if self.move_queue:
            self.dx, self.dy = self.move_queue.pop(0)
        else:
            self.moving = False
            self.path_end, self.path_start = None, None
            self.x, self.y = int(self.x), int(self.y)
            self.pos = (self.x, self.y)
            self.dx, self.dy = 0, 0
            self.frame = 0

    def move_to(self, x, y, x1, y1):
        self.face_player(x1, y1)
        dx = (x1 - x)/self.speed
        dy = (y1 - y)/self.speed
        while x != x1 or y != y1:
            self.move_queue.append((dx, dy))
            x += dx
            y += dy
            self.moving = True
            self.path_end = (x1, y1)
            self.path_start = (x, y)

    def line_of_sight(self, from_pos, to_pos, bad_spaces):
        dist = manhattan_distance(from_pos, to_pos)
        if dist == 0:
            return True
        
        for i in range(dist):
            x = int(from_pos[0] + (to_pos[0] - from_pos[0])/dist * i)
            y = int(from_pos[1] + (to_pos[1] - from_pos[1])/dist * i)

            if (x, y) != from_pos and (x, y) != to_pos and (x, y) in bad_spaces:
                return False


        return True
        
    def good_pos(self, pos, player_pos, bad_spaces):
        return distance(pos, player_pos) == 4

    def pathfind(self, player, bad_spaces):
        if self.room != player.room or self.moving:
            return

        heap = list()
        heapq.heappush(heap, (0, self.pos, []))
        closed_nodes = set()
        while heap:
            dist, pos, path = heapq.heappop(heap)
            if self.good_pos(pos, player.getPos(), bad_spaces):
                if len(path):
                    self.move_to(*self.pos, *path[0])
                return
            if pos in closed_nodes:
                continue
            closed_nodes.add(pos)
            for dx, dy in __facing_deltas__:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if new_pos in closed_nodes:
                    continue
                if not self.in_room(*new_pos):
                    continue
                if new_pos in bad_spaces:
                    continue
                heapq.heappush(heap, (dist+1, new_pos, path + [new_pos]))

class Babus (Actor):
    def __init__(self, pos):
        sprites = SpriteSheet('babus.png')
        babus_rects = [(12, 42, 32, 48), (54, 42, 32, 48),
                       (96, 42, 32, 48), (138, 42, 32, 48)]
        babus_l = sprites.images_at(babus_rects, colorkey=-1)
        babus_rects = [(12, 106, 32, 48), (54, 106, 32, 48),
                       (96, 106, 32, 48), (138, 106, 32, 48)]
        babus_r = sprites.images_at(babus_rects, colorkey=-1)
        babus_rects = [(12, 170, 32, 48), (54, 170, 32, 48),
                       (96, 170, 32, 48), (138, 170, 32, 48)]
        babus_d = sprites.images_at(babus_rects, colorkey=-1)
        babus_rects = [(12, 234, 32, 48), (54, 234, 32, 48),
                       (96, 234, 32, 48), (138, 234, 32, 48)]
        babus_u = sprites.images_at(babus_rects, colorkey=-1)
        babus_rects = [(208, 192, 32, 60), (250, 192, 32, 60),
                       (292, 192, 32, 60), (334, 192, 32, 60),
                       (376, 192, 32, 60), (418, 192, 32, 60)]
        babus_jump = sprites.images_at(babus_rects, colorkey=-1)
        super().__init__([babus_u, babus_r, babus_d, babus_l, babus_jump], [
            (0, 0, 32, 48), (0, 0, 32, 48), (0, 0, 32, 48), (0, 0, 32, 48), (0, 0, 32, 60)], pos)

class Archer (Actor):
    def __init__(self, pos):
        sprites = SpriteSheet('archer.png')
        archer_rects = [(214, 18, 32, 60), (248, 18, 32, 60),
                        (214, 18, 32, 60), (180, 18, 32, 60)]
        archer_l = sprites.images_at(archer_rects, colorkey=-1)
        archer_d = [pygame.transform.flip(
            archer, True, False) for archer in archer_l]
        archer_rects = [(212, 84, 32, 60), (248, 82, 32, 60),
                        (212, 84, 32, 60), (178, 84, 32, 60)]
        archer_u = sprites.images_at(archer_rects, colorkey=-1)
        archer_r = [pygame.transform.flip(
            archer, True, False) for archer in archer_u]
        archer_rects = [(184, 286, 32, 62), (218, 286, 32, 62),
                        (252, 286, 32, 62), (218, 286, 32, 62),
                        (184, 286, 32, 62)]
        archer_jump = [pygame.transform.flip(
            archer, True, False) for archer in sprites.images_at(archer_rects, colorkey=-1)]
        super().__init__([archer_u, archer_r, archer_d, archer_l, archer_jump], [
            (0, 0, 32, 60), (0, 0, 32, 60), (0, 0, 32, 60), (0, 0, 32, 60), (0, 0, 32, 62)], pos)
        
    def good_pos(self, pos, player_pos, bad_spaces):
        dist = manhattan_distance(pos, player_pos)
        return self.line_of_sight(pos, player_pos, bad_spaces) and dist >= 3 and dist <= 5

class Templar (Actor):
    def __init__(self, pos):
        sprites = SpriteSheet('templar.png')
        templar_rects = [(12, 34, 32, 56), (54, 34, 32, 56),
                         (96, 34, 32, 56), (138, 34, 32, 56)]
        templar_l = sprites.images_at(templar_rects, colorkey=-1)
        templar_rects = [(12, 98, 32, 56), (54, 98, 32, 56),
                         (96, 98, 32, 56), (138, 98, 32, 56)]
        templar_r = sprites.images_at(templar_rects, colorkey=-1)
        templar_rects = [(12, 162, 32, 56), (54, 162, 32, 56),
                         (96, 162, 32, 56), (138, 162, 32, 56)]
        templar_d = sprites.images_at(templar_rects, colorkey=-1)
        templar_rects = [(12, 226, 32, 56), (54, 226, 32, 56),
                         (96, 226, 32, 56), (138, 226, 32, 56)]
        templar_u = sprites.images_at(templar_rects, colorkey=-1)
        templar_rects = [(478, 186, 34, 66), (520, 186, 34, 66),
                         (559, 186, 34, 66), (520, 186, 34, 66), (478, 186, 34, 66)]
        templar_jump = sprites.images_at(templar_rects, colorkey=-1)
        super().__init__([templar_u, templar_r, templar_d, templar_l, templar_jump], [
            (0, 0, 32, 56), (0, 0, 32, 56), (0, 0, 32, 56), (0, 0, 32, 56), (0, 0, 34, 66)], pos)
        
    def good_pos(self, pos, player_pos, bad_spaces):
        dist = distance(pos, player_pos)
        return dist == 1

class Mog (Actor):
    def __init__(self, pos):
        sprites = SpriteSheet('mog.png')
        mog_rects = [(198, 152, 32, 58), (240, 152, 32, 58),
                     (198, 152, 32, 58), (156, 152, 32, 58)]
        mog_l = sprites.images_at(mog_rects, colorkey=-1)
        mog_d = [pygame.transform.flip(mog, True, False) for mog in mog_l]
        mog_rects = [(198, 56, 32, 58), (238, 56, 32, 58),
                     (198, 56, 32, 58), (158, 56, 32, 58)]
        mog_u = sprites.images_at(mog_rects, colorkey=-1)
        mog_r = [pygame.transform.flip(mog, True, False) for mog in mog_u]
        mog_rects = [(1044, 142, 32, 68), (1084, 142, 32, 68),
                     (1124, 142, 32, 68), (1084, 142, 32, 68),
                     (1044, 142, 32, 68)]
        mog_jump = [pygame.transform.flip(
            mog, True, False) for mog in sprites.images_at(mog_rects, colorkey=-1)]
        super().__init__([mog_u, mog_r, mog_d, mog_l, mog_jump], [
            (0, 0, 32, 56), (0, 0, 32, 56), (0, 0, 32, 56), (0, 0, 32, 56), (0, 0, 32, 68)], pos)
        
    def good_pos(self, pos, player_pos, bad_spaces):
        return self.line_of_sight(pos, player_pos, bad_spaces) and (pos[0] == player_pos[0] or pos[1] == player_pos[1])


def find_actor(actors: list, move) -> Actor:
    for actor in actors:
        if actor.pos == (move[0], move[1]):
            return actor
    return None
