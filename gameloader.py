import json
from floor import Floor
from room import Room
from exit import Exit
from random import shuffle
from actor import Behavior, Actor
from staticobject import Pillar
from terraintile import TileType
import pygame
from spritesheet import SpriteSheet

json_fn = 'amulet.dat'

def create_map(amulet):
    with open(json_fn, "r") as stream:
        game_yaml = json.load(stream)
    
    amulet.floors = []
    amulet.actors = []

    for floor_yaml in game_yaml:
        floor_room_map = dict()
        floor_room_tiles_map = dict()

        floor = Floor(floor_yaml['floor'])
        amulet.add_floor(floor)

        for room in floor_yaml['rooms']:
            tiletype = eval('TileType.'+room['tileType'])
            froom = Room(room['width'], room['height'], tiletype)
            froom.name = room['room']
            floor.add_room(froom)
            floor_room_map[froom.name] = froom
            all_spaces = [(x, y) for x in range(froom.width)
                    for y in range(froom.height)]
            shuffle(all_spaces)
            floor_room_tiles_map[froom.name] = all_spaces
        
        for exit in floor_yaml['exits']:
            from_room = exit['exit'][0]
            to_room = exit['exit'][1]
            tuple1 = (floor_room_map[from_room['room']], from_room['x'], from_room['y'])
            tuple2 = (floor_room_map[to_room['room']], to_room['x'], to_room['y'])
            floor.exits.append(Exit(tuple1, tuple2))

        room = floor_room_map['Entry Room']
        all_spaces = floor_room_tiles_map['Entry Room']

        load_actors(amulet, floor_yaml, floor_room_map, floor_room_tiles_map)
        for _ in range(4):
            amulet.actors.append(Pillar(all_spaces.pop()))
        for actor in amulet.actors:
            if actor.room is None:
                actor.room = room

def load_actors(amulet, floor_yaml, floor_room_map, floor_room_tiles_map):
    for actor in floor_yaml['actors']:
        room_name = actor['room'] if 'room' in actor else 'Entry Room'
        all_spaces = floor_room_tiles_map[room_name]

        sprites = SpriteSheet(actor['spritesheet'])
        left = sprites.images_at(actor['west'], colorkey=-1)
        if 'south' in actor:
            down = sprites.images_at(actor['south'], colorkey=-1)
        else:
            down = [pygame.transform.flip(archer, True, False) for archer in left]

        up = sprites.images_at(actor['north'], colorkey=-1)
        if 'east' in actor:
            right = sprites.images_at(actor['east'], colorkey=-1)
        else:
            right = [pygame.transform.flip(archer, True, False) for archer in up]

        jump = sprites.images_at(actor['jump'], colorkey=-1)
        p_actor = Actor([up, right, down, left, jump], actor['rects'], all_spaces.pop())
        p_actor.name = actor['actor']
        if 'isplayer' in actor:
            p_actor.setIsPlayer(actor['isplayer'])
        else:
            p_actor.setIsPlayer(False)
        if 'behavior' in actor:
            p_actor.behavior = eval('Behavior.' + actor['behavior'])
        p_actor.room = floor_room_map[room_name]
        amulet.actors.append(p_actor)
