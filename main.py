from amulet import Amulet
from gameloader import create_map
import pygame
import sys
from intro import Intro
from outro import Outro
from wintro import Wintro

def init_screen():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((768, 640))
    myfont = pygame.font.SysFont(None, 24)
    pygame.mixer.init()
    pygame.mixer.music.load("epic-heart-2-min-8643.mp3")
    pygame.mixer.music.play()

    return screen, myfont


if __name__ == '__main__':
    screen, myfont = init_screen()

    intro = Intro(screen, myfont)
    intro.game_loop()

    while True:
        amulet = Amulet(screen, myfont)
        create_map(amulet)
        restart, player_died = amulet.game_loop()
        if not restart:
            break

    if player_died:
        outro = Outro(screen, myfont)
        outro.game_loop()
    else:
        wintro = Wintro(screen, myfont)
        wintro.game_loop()

    print("Thanks for playing!")
    pygame.quit()
    sys.exit()
