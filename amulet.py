import pygame
from spritesheet import SpriteSheet
from pygame.time import Clock
from room import Room, init_rooms

def init_game():
    screen_width = 1024
    screen_height = 768

    pygame.init()
    pygame.font.init()
    return pygame.display.set_mode((screen_width, screen_height))

def game_loop():
    running = True
    
    screen = init_game()
    init_rooms()

    room = Room(10, 7, '02')
    rotation = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_LEFT:
                    rotation -= 1
                elif event.key == pygame.K_RIGHT:
                    rotation += 1

        screen.fill((0, 0, 0))

        room.draw(screen, rotation)

        pygame.display.flip()

if __name__ == '__main__':
    game_loop()
    pygame.quit()

