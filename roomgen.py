import os
import xml.etree.ElementTree as ET
import re
from random import randint, choice


def make_csv(tiles, width):
    """
    Takes a list of tiles and a width and returns a string of comma-separated values
    """
    csv = ""
    for i in range(0, len(tiles), width):
        csv += ",".join(str(t) for t in tiles[i:i+width])
        if i + width < len(tiles):
            csv += ',\n'
        else:
            csv += '\n'
    return csv


challenges = [
    ('*sprite', '*dagger', 1),
    ('*archer', '*longbow', 3),
    ('*templar', '*broadsword', 5),
    ('*babus', '*firewand', 8),
    ('*mogknight', '*lance', 13),
    ('*malboro', '*tentacle', 5),
    ('*crystal', '*shield', 5)
]

template = os.path.join('..', 'template.tmx')
actors = os.path.join('..', 'actors.txt')
rooms = os.path.join('..', 'rooms.txt')
roadmap = os.path.join('..', 'roadmap.txt')

# delete actors file
if os.path.exists(actors):
    os.remove(actors)

# delete rooms file
if os.path.exists(rooms):
    os.remove(rooms)

# delete roadmap file
if os.path.exists(roadmap):
    os.remove(roadmap)

tree = ET.parse(template)
root = tree.getroot()

layer1set = None
layer2set = None
layer1data = None
layer2data = None
width, height = 6+randint(0, 6), 6+randint(0, 6)

print(root.tag)

for child in root:
    print(child.tag, child.attrib)
    if child.tag == 'layer':
        for grandchild in child:
            print(grandchild.tag, grandchild.attrib)
            if grandchild.tag == 'data':
                fa = set(int(t) for t in re.findall(
                    r'\d+', grandchild.text) if int(t) > 0)
                if layer1set:
                    layer2 = child
                    layer2set = list(fa)
                    layer2data = grandchild
                else:
                    width = int(child.attrib['width'])
                    height = int(child.attrib['height'])
                    layer1set = list(fa)
                    layer1data = grandchild
                    layer1 = child

print(width, height)
print(layer1set)
print(layer2set)

for room in range(25):
    challenge_rating = 3 + room + randint(0, 2)
    width, height = 6+randint(0, 6), 6+randint(0, 6)
    root.attrib['width'] = str(width)
    root.attrib['height'] = str(height)
    layer1.attrib['width'] = str(width)
    layer1.attrib['height'] = str(height)
    layer2.attrib['width'] = str(width)
    layer2.attrib['height'] = str(height)
    roomsize = width * height
    tiles = [0] * roomsize
    while len([t for t in tiles if t > 0]) < roomsize * 0.75:
        tiles[randint(0, roomsize - 1)] = choice(layer1set)
    layer1tiles = tiles
    tiles = [0] * roomsize
    while len([t for t in tiles if t > 0]) < roomsize * 0.05:
        pos = randint(0, roomsize - 1)
        if layer1tiles[pos] > 0:
            tiles[pos] = choice(layer2set)
    layer2tiles = tiles

    layer1data.text = make_csv(layer1tiles, width)
    layer2data.text = make_csv(layer2tiles, width)

    # fn = os.path.join('..', f'genroom{room:02}.tmx')
    # tree.write(fn)
    # print(f'Wrote {fn}')

    clist = []

    print (f'challenge rating {challenge_rating}')
    while sum(c[2] for c in clist) < challenge_rating:
        candidate = choice(challenges)
        if candidate[2] + sum(c[2] for c in clist) <= challenge_rating:
            print (f'adding {candidate}')
            clist.append(candidate)

    with open(actors, 'a') as f:
        for c in clist:
            f.write(f"""      - actor: {c[0]}
        isplayer: False
        room: *rm03{room:02}
        inventory:
        - item: {c[1]}
""")

    with open(rooms, 'a') as f:
        f.write(f"""    - room: &rm03{room:02} Room {room}
      tileType: ROOM
      tiled:
        tiles: genroom{room:02}.tmj
        tilewidth: 64
        tileheight: 128
        displayheight: 37
        spritesheet: kenneytiles.png
        tilecount: 255
        columns: 15
        firstgid: 1
        lift: 91
        offset: 0
      width: {height}
      height: {width}
""")
    
    with open(roadmap, 'a') as f:
        f.write(f"  - *rm03{room:02}\n")
