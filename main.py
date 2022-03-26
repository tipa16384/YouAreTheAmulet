from amulet import Amulet, ExitState
from gameloader import create_map
import pygame
import sys
from intro import Intro
from outro import Outro
from wintro import Wintro
from layout import Layout
from plotro import Plotro
from finder import helper

def init_screen():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(helper("epic-heart-2-min-8643.mp3"))
        pygame.mixer.music.play()
    except:
        # No music! Well, that's okay.
        pass

def exit():
    print("Thanks for playing!")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    layout = Layout()
    init_screen()

    # get the value of the "-dump" parameter.
    dump = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "-dump":
            dump = True

    intro = Intro(layout, layout.screen, layout.font)
    intro.game_loop()

    amulet = Amulet(layout)
    create_map(amulet)

    if dump:
        print (f"Dumping the rendered rooms")
        amulet.dump_map()
        print ("So long!")
        exit()

    state = amulet.game_loop()

    if state == ExitState.QUIT:
        exit()
    
    plotro = Plotro(layout, layout.screen, layout.font)
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
                break
    
        state = amulet.game_loop(True)

        if not state == ExitState.WON:
            break

    if state == ExitState.DIED:
        outro = Outro(layout, layout.screen, layout.font)
        outro.game_loop()
    elif state == ExitState.WON:
        wintro = Wintro(layout, layout.screen, layout.font)
        wintro.game_loop()

