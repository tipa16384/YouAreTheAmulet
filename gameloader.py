import json
from floor import Floor
from room import Room
from exit import Exit
from random import shuffle
from actor import Behavior, Actor
from staticobject import StaticObject
from terraintile import TileType
import pygame
from spritesheet import SpriteSheet
from item import Item
from math import ceil, floor

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
    for weapon in game_yaml['items']:
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
            froom.bad_spaces = set()
            froom.good_spaces = set(all_spaces)
            froom.tiled = None
            froom.phrases = [] if not 'phrases' in room or not room['phrases'] else room['phrases'].split('\n')

            if 'tiled' in room:
                froom.tiled = room['tiled']
                froom.room_sprites = SpriteSheet(froom.tiled['spritesheet'])
                with open(froom.tiled['tiles'], "r") as stream:
                    tiled_room = json.load(stream)
                froom.height = tiled_room['width']
                froom.width = tiled_room['height']
                froom.layers = tiled_room['layers']
                froom.offset = froom.tiled['offset']
                for layer_no, layer in enumerate(layer for layer in tiled_room['layers'] if layer['type'] == 'tilelayer'):
                    if layer_no == 0:
                        froom.good_spaces = set((x, y) for y in range(froom.height) for x in range(froom.width) if layer['data'][(froom.width - 1 - x) * froom.height + y] != 0)
                    elif layer_no == 1:
                        froom.bad_spaces = set((x-froom.offset, y+froom.offset) for y in range(froom.height) for x in range(froom.width) if layer['data'][(froom.width - 1 - x) * froom.height + y] != 0)
                        print (f"Bad spaces: {froom.name} {froom.offset} {froom.bad_spaces}")

                all_spaces = list(froom.good_spaces - froom.bad_spaces)
                froom.good_spaces = set(all_spaces)

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
        load_items(amulet, floor_yaml, floor_room_map)

        for actor in amulet.actors:
            if actor.room is None:
                actor.room = room

def load_items(amulet, floor_yaml, floor_room_map):
    for item in floor_yaml['items']:
        room_name = item['room'] if 'room' in item else 'Entry Room'
        template = amulet.library[item['item']]
        sprite_rect = template['sprite']
        sprites = SpriteSheet(template['spritesheet']).load_strip(sprite_rect, 1, colorkey=-1)
        room = floor_room_map[room_name]

        pos = item['position'] if 'position' in item else None

        print (f"Position of {item['item']} is {pos}")

        p_item = StaticObject(sprites, None, pos)
        p_item.sprite = sprites[0]
        p_item.rect = (0, 0, sprite_rect[2] - sprite_rect[0], sprite_rect[3] - sprite_rect[1])
        p_item.room = room
        p_item.phrases = item['phrases'].split('\n') if 'phrases' in item else None
        p_item.ontop = item['ontop'] if 'ontop' in item else None
        p_item.name = item['item']

        pos, _ = p_item.get_initial_space(room)

        print (f"Alternate positioning for {p_item.name} in {room.name} is {pos}")
        p_item.setPos(pos)

        amulet.actors.append(p_item)

def load_actors(amulet, floor_yaml, floor_room_map, floor_room_tiles_map):
    for actor in floor_yaml['actors']:
        room_name = actor['room'] if 'room' in actor else 'Entry Room'
        all_spaces = floor_room_tiles_map[room_name]
        room = floor_room_map[room_name]

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

        left = sprites.image_at(template['dead_west'], colorkey=-1)
        if 'dead_south' in template:
            down = sprites.image_at(template['dead_south'], colorkey=-1)
        else:
            down = pygame.transform.flip(left, True, False)

        if 'dead_north' in template:
            up = sprites.image_at(template['dead_north'], colorkey=-1)
        else:
            up = pygame.transform.flip(left, False, True)

        if 'dead_east' in template:
            right = sprites.image_at(template['dead_east'], colorkey=-1)
        else:
            right = pygame.transform.flip(up, True, False)
        
        p_actor.dead_sprites = [up, right, down, left]

        if 'isplayer' in actor:
            p_actor.setIsPlayer(actor['isplayer'])
        else:
            p_actor.setIsPlayer(False)
        
        p_actor.health = p_actor.max_health = template['health']

        if 'inventory' in actor and actor['inventory']:
            for item in actor['inventory']:
                pitem = Item(amulet.weapons[item['item']])
                pitem.identified = True
                p_actor.inventory.append(pitem)

        wieldable_items = [item for item in p_actor.inventory if item.can_wield()]
        if wieldable_items:
            wieldable_items[0].wield()

        p_actor.room = room
        p_actor.phrases = actor['phrases'].split('\n') if 'phrases' in actor else None
        p_actor.ontop = actor['ontop'] if 'ontop' in actor else None

        pos, facing = p_actor.get_initial_space(room, p_actor.getIsPlayer())

        print (f"Alternate positioning for {p_actor.name} in {room.name} is {(pos, facing)}")
        
        if pos:
            p_actor.setFacing(facing)
            p_actor.setPos(pos)

        if pos and pos in all_spaces: all_spaces.remove(pos)

        amulet.actors.append(p_actor)
