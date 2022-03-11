import heapq
from staticobject import StaticObject
from math import sqrt, pow
from enum import Enum

__facing_deltas__ = [(0, -1), (1, 0), (0, 1), (-1, 0)]


class Behavior(Enum):
    MAGIC = 0
    ARCHER = 1
    MELEE = 2
    CHARGE = 3
    DUMMY = 4


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def distance(a, b):
    return sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))


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
        self.inventory = list()
        self.max_health = 10
        self.health = self.max_health
        self.alive = True
        self.dead_sprites = list()
        self.target = None
        self.in_range = False

    def get_wielded(self):
        for item in self.inventory:
            if item.can_attack():
                return item
        return None

    def get_behavior(self):
        item = self.get_wielded()
        if item and 'behavior' in item.template:
            return eval('Behavior.' + item.template['behavior'])
        return Behavior.MELEE

    def needs_to_wield(self):
        if not self.get_wielded():
            for item in self.inventory:
                if item.can_wield():
                    item.wield()
                    return True
        return False

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
        if self.alive:
            return self.rects[self.getRotatedFacing()]
        else:
            drect = self.dead_sprites[self.getRotatedFacing()].get_rect()
            return (0, 0, drect[2], drect[3])

    def get_sprite(self):
        if not self.alive:
            return self.dead_sprites[self.getRotatedFacing()]
        elif not self.animated:
            return self.sprites[self.getRotatedFacing()]
        else:
            return self.sprites[self.getRotatedFacing()][self.frame % len(self.sprites[self.getRotatedFacing()])]

    def i_am_at(self):
        if self.moving:
            return [self.path_end, self.path_start]
        else:
            return [self.pos]
    
    def kill(self):
        self.alive = False
        self.health = 0

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

        for i in range(int(dist)):
            x = int(from_pos[0] + (to_pos[0] - from_pos[0])/dist * i)
            y = int(from_pos[1] + (to_pos[1] - from_pos[1])/dist * i)
            if (x, y) != from_pos and (x, y) != to_pos and (x, y) in bad_spaces:
                return False

        return True

    def good_pos(self, pos, player_pos, bad_spaces):
        behavior = self.get_behavior()
        if behavior == Behavior.MAGIC:
            dist = distance(pos, player_pos)
            return self.line_of_sight(pos, player_pos, bad_spaces) and dist <= 6.0
        elif behavior == Behavior.ARCHER:
            dist = distance(pos, player_pos)
            return self.line_of_sight(pos, player_pos, bad_spaces) and dist >= 3 and dist <= 5
        elif behavior == Behavior.MELEE:
            dist = distance(pos, player_pos)
            return dist < 2.0
        elif behavior == Behavior.CHARGE:
            dist = distance(pos, player_pos)
            return self.line_of_sight(pos, player_pos, bad_spaces) and dist <= 2.0
        elif behavior == Behavior.DUMMY:
            return False
        dist = distance(pos, player_pos)
        return dist > 3.0 and dist <= 4.0
    
    def present_tense(self, verb):
        if verb.endswith('e'):
            return verb + 's'
        elif verb.endswith('y'):
            return verb[:-1] + 'ies'
        elif verb.endswith('o') or verb.endswith('ch') or verb.endswith('sh') or verb.endswith('x') or verb.endswith('z') or verb.endswith('s'):
            return verb + 'es'
        else:
            return verb + 's'

    def pronoun_subject(self, verb='attack'):
        return 'You ' + verb if self.is_player else self.name + ' ' + self.present_tense(verb)

    def pronoun_object(self):
        return 'you' if self.is_player else self.name

    def wielding(self):
        item = self.get_wielded()
        return str(item) if item else "martial arts"

    def pathfind(self, player, bad_spaces):
        "return True if the actor was already in a good spot."

        if self.room != player.room or self.moving:
            return False

        player_pos = player.pos if not player.moving else player.path_end

        heap = list()
        heapq.heappush(heap, (0, self.pos, []))
        closed_nodes = set()
        while heap:
            dist, pos, path = heapq.heappop(heap)
            if self.good_pos(pos, player_pos, bad_spaces):
                if len(path):
                    self.move_to(*self.pos, *path[0])
                return len(path) == 0
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
        
        # there was no path to the player. let's just move to the player.

        heap = list()
        for dx, dy in __facing_deltas__:
            new_pos = (self.pos[0] + dx, self.pos[1] + dy)
            if not self.in_room(*new_pos) or new_pos in bad_spaces:
                continue
            dist = distance(new_pos, player_pos)
            heapq.heappush(heap, (dist, new_pos))

        if heap:
            dist, new_pos = heapq.heappop(heap)
            ndist = distance(self.pos, player_pos)
            if dist < ndist:
                self.move_to(*self.pos, *new_pos)

        return False

