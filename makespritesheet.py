from gameloader import create_map
from layout import Layout
from amulet import Amulet
from actor import Actor
import pygame
import sys
from collections import defaultdict

p_layout = Layout(320, 2880)
p_amulet = Amulet(p_layout)
create_map(p_amulet)

actor_dict = {}

for actor in p_amulet.actors:
    if isinstance(actor, Actor):
        actor_dict[actor.name] = actor

sprite_width = 64
sprite_height = 80
rows_per_sprite = 4

screen_width, screen_height = 5 * sprite_width, len(actor_dict) * rows_per_sprite * sprite_height

p_layout.screen = pygame.display.set_mode((screen_width, screen_height))

# make screen red
p_layout.screen.fill((255, 0, 0))

# - actor: the actor to render
#   spritesheet: babus.png
#   west: [[12, 42, 32, 48], [54, 42, 32, 48], [96, 42, 32, 48], [138, 42, 32, 48]]
#   east: [[12, 106, 32, 48], [54, 106, 32, 48], [96, 106, 32, 48], [138, 106, 32, 48]]
#   south: [[12, 170, 32, 48], [54, 170, 32, 48], [96, 170, 32, 48], [138, 170, 32, 48]]
#   north: [[12, 234, 32, 48], [54, 234, 32, 48], [96, 234, 32, 48], [138, 234, 32, 48]]
#   dead_west: [100, 684, 32, 38]
#   dead_east: [238, 684, 32, 40]
#   dead_south: [100, 752, 32, 38]
#   dead_north: [238, 752, 32, 40]

sprite_sheet_name = "actorsprites.png"

facing_name_list = ['north', 'east', 'south', 'west']

for i, name in enumerate(actor_dict):
    actor = actor_dict[name]
    print (f"- actor: {name}")
    print (f"  spritesheet: {sprite_sheet_name}")
    actor_info = dict()
    for facing in range(rows_per_sprite):
        actor.setFacing(facing)
        facing_name = facing_name_list[facing]
        actor_info[facing_name] = []
        for frame in range(5):
            x0 = frame * sprite_width
            y0 = (facing + i * rows_per_sprite) * sprite_height
            # if facing + frame is odd, make background green
            if (facing + frame) % 2 == 1:
                # fill rect (x0, y0, sprite_width, sprite_height) with green
                p_layout.screen.fill((0, 255, 0), (x0, y0, sprite_width, sprite_height))
            actor.alive = frame != 4
            actor.frame = frame
            sprite = actor.get_sprite()
            x_offset = (sprite_width - sprite.get_width()) // 2
            y_offset = (sprite_height - sprite.get_height())
            p_layout.screen.blit(sprite, (x_offset + x0, y_offset + y0))
            if actor.alive:
                actor_info[facing_name].append([x0 + x_offset, y0 + y_offset, sprite.get_width(), sprite.get_height()])
            else:
                actor_info['dead_' + facing_name] = [x0 + x_offset, y0 + y_offset, sprite.get_width(), sprite.get_height()]
    for key in actor_info:
        print (f"  {key}: {actor_info[key]}")

running = True

pygame.display.flip()

# save screen in PNG format
pygame.image.save(p_layout.screen, sprite_sheet_name)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            try:
                # Was it the Escape key? If so, stop the loop.
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
            except:
                pass

pygame.quit()
sys.exit()

