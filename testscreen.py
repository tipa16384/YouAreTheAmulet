import pygame

pygame.init()
pygame.font.init()

# create an 800x600 screen
screen = pygame.display.set_mode((800, 600))

# initialize the font
font = pygame.font.Font(None, 36)

# while the game is not quit
done = False

# do the game loop
while not done:
    # for every event in the event queue
    for event in pygame.event.get():
        # if the event is the X button
        if event.type == pygame.QUIT:
            # quit the game
            done = True
    
    # fill the screen with black
    screen.fill((0, 0, 0))

    # put a 10x10 red square at each corner of the screen
    pygame.draw.rect(screen, (255, 0, 0), (0, 0, 10, 10))
    pygame.draw.rect(screen, (255, 0, 0), (0, 590, 10, 10))
    pygame.draw.rect(screen, (255, 0, 0), (790, 0, 10, 10))
    pygame.draw.rect(screen, (255, 0, 0), (790, 590, 10, 10))

    # in the center of the screen, render the text "Displayport Test"
    text = "Displayport Test"
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (400, 300)
    screen.blit(text_surface, text_rect)

    # update the screen
    pygame.display.flip()

# quit pygame
pygame.quit()
