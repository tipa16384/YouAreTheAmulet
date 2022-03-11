from amulet import Amulet, ExitState
from gameloader import create_map
import pygame
import sys
from intro import Intro
from outro import Outro
from wintro import Wintro
from layout import Layout
from plotro import Plotro
import os

def init_screen():
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join('music',"epic-heart-2-min-8643.mp3"))
    pygame.mixer.music.play()

def exit():
    print("Thanks for playing!")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    layout = Layout()
    init_screen()

    intro = Intro(layout.screen, layout.font)
    intro.game_loop()

    amulet = Amulet(layout)
    create_map(amulet)
    state = amulet.game_loop()

    if state == ExitState.QUIT:
        exit()
    
    plotro = Plotro(layout.screen, layout.font)
    state = plotro.game_loop()

    if state == ExitState.QUIT:
        exit()
    
    player = amulet.get_player()
    floor = amulet.get_floors()[0]

    for room_name in amulet.roadmap:
        for room in floor.rooms:
            if room.name == room_name:
                player.room = room
                pos, facing = player.get_initial_space(room, True)
                player.setPos(pos)
                player.setFacing(facing)
                print (f"Player is in {player.room.name} and room takes amulet {room.takeAmulet}")
                break
    
        state = amulet.game_loop(True)

        if not state == ExitState.WON:
            break

    if state == ExitState.DIED:
        outro = Outro(layout.screen, layout.font)
        outro.game_loop()
    elif state == ExitState.WON:
        wintro = Wintro(layout.screen, layout.font)
        wintro.game_loop()

