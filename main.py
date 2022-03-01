from amulet import Amulet
from gameloader import create_map
import pygame
import sys
from intro import Intro


def init_screen():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((768, 640))
    myfont = pygame.font.SysFont(None, 24)
    pygame.mixer.init()
    pygame.mixer.music.load("badkalimba.mp3")
    pygame.mixer.music.play()

    return screen, myfont


if __name__ == '__main__':
    screen, myfont = init_screen()

    intro = Intro(screen, myfont)
    intro.game_loop()

    while True:
        amulet = Amulet(screen, myfont)
        create_map(amulet)
        if not amulet.game_loop():
            break

    print("Thanks for playing!")
    pygame.quit()
    sys.exit()
