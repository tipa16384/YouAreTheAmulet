import json
from floor import Floor
from room import Room
from exit import Exit
from random import shuffle
from actor import Babus, Archer, Templar, Mog
from staticobject import Pillar
from terraintile import TileType

json_fn = 'amulet.dat'

def create_map(amulet):
    with open(json_fn, "r") as stream:
        game_yaml = json.load(stream)
    
    amulet.floors = []
    amulet.actors = []

    for floor_yaml in game_yaml:
        floor_room_map = dict()

        floor = Floor(floor_yaml['floor'])
        amulet.add_floor(floor)

        for room in floor_yaml['rooms']:
            tiletype = eval('TileType.'+room['tileType'])
            froom = Room(room['width'], room['height'], tiletype)
            froom.name = room['room']
            floor.add_room(froom)
            floor_room_map[froom.name] = froom
        
        for exit in floor_yaml['exits']:
            from_room = exit['exit'][0]
            to_room = exit['exit'][1]
            tuple1 = (floor_room_map[from_room['room']], from_room['x'], from_room['y'])
            tuple2 = (floor_room_map[to_room['room']], to_room['x'], to_room['y'])
            floor.exits.append(Exit(tuple1, tuple2))

        room = floor_room_map['Entry Room']
        all_spaces = [(x, y) for x in range(room.width)
                    for y in range(room.height)]
        shuffle(all_spaces)
        player = Babus(all_spaces.pop())
        player.setIsPlayer(True)
        amulet.actors.append(player)
        amulet.actors.append(Archer(all_spaces.pop()))
        amulet.actors.append(Templar(all_spaces.pop()))
        amulet.actors.append(Mog(all_spaces.pop()))
        for _ in range(4):
            amulet.actors.append(Pillar(all_spaces.pop()))
        for actor in amulet.actors:
            actor.room = room

