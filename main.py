from amulet import Amulet
from gameloader import create_map
import pygame
import sys
from intro import Intro
from outro import Outro
from wintro import Wintro
from layout import Layout

def init_screen(layout: Layout):
    pygame.mixer.init()
    pygame.mixer.music.load("epic-heart-2-min-8643.mp3")
    pygame.mixer.music.play()

if __name__ == '__main__':
    layout = Layout()
    init_screen(layout)

    intro = Intro(layout.screen, layout.font)
    intro.game_loop()

    while True:
        amulet = Amulet(layout)
        create_map(amulet)
        restart, player_died = amulet.game_loop()
        if not restart:
            break

    if player_died:
        outro = Outro(layout.screen, layout.font)
        outro.game_loop()
    else:
        wintro = Wintro(layout.screen, layout.font)
        wintro.game_loop()

    print("Thanks for playing!")
    pygame.quit()
    sys.exit()
