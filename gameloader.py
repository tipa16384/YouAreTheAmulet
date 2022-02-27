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
from item import Item

json_fn = 'amulet.dat'

def create_map(amulet):
    with open(json_fn, "r") as stream:
        game_yaml = json.load(stream)
    
    amulet.floors = []
    amulet.actors = []

    library_map = dict()
    for actor in game_yaml['library']:
        library_map[actor['actor']] = actor
    amulet.library = library_map

    weapon_map = dict()
    for weapon in game_yaml['weapons']:
        weapon_map[weapon['item']] = weapon
    amulet.weapons = weapon_map

    for floor_yaml in game_yaml['floors']:
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
        template = amulet.library[actor['actor']]

        sprites = SpriteSheet(template['spritesheet'])
        left = sprites.images_at(template['west'], colorkey=-1)
        if 'south' in template:
            down = sprites.images_at(template['south'], colorkey=-1)
        else:
            down = [pygame.transform.flip(archer, True, False) for archer in left]

        up = sprites.images_at(template['north'], colorkey=-1)
        if 'east' in template:
            right = sprites.images_at(template['east'], colorkey=-1)
        else:
            right = [pygame.transform.flip(archer, True, False) for archer in up]

        jump = sprites.images_at(template['jump'], colorkey=-1)
        p_actor = Actor([up, right, down, left, jump], template['rects'], all_spaces.pop())
        p_actor.name = actor['actor']
        if 'isplayer' in actor:
            p_actor.setIsPlayer(actor['isplayer'])
        else:
            p_actor.setIsPlayer(False)

        for item in actor['inventory']:
            pitem = Item(amulet.weapons[item['item']])
            pitem.identified = True
            p_actor.inventory.append(pitem)

        wieldable_items = [item for item in p_actor.inventory if item.can_wield()]
        if wieldable_items:
            wieldable_items[0].wield()

        p_actor.room = floor_room_map[room_name]
        amulet.actors.append(p_actor)
