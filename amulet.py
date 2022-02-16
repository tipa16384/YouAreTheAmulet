import pygame
from spritesheet import SpriteSheet
from pygame.time import Clock
from room import Room, init_rooms
import sys
from itertools import cycle


class Amulet:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((768, 640))
        self.myfont = pygame.font.SysFont(None, 24)
        init_rooms()
        self.clock = Clock()
        self.room = Room(10, 7, '02')
        self.rotation = 0
        self.player = self.room.actors[0]
        self.player.setIsPlayer(True)
        self.player.setFacing(1)
        self.player.setRotation(0)
        self.room.actors[1].setFacing(-1)
        self.room.actors[1].setRotation(0)
        self.room.actors[1].setIsPlayer(False)
        self.animation_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.animation_event, 250)
        self.movement_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.movement_event, 1000//120)

        self.new_message("Use the arrow keys to move around. Press P to swap players. Press ESC to quit.")

    def object_at(self, x, y):
        for actor in self.room.actors:
            if actor.getPos() == (x, y):
                return actor
        return None

    def rotate_player(self, rotation):
        self.player.setFacing(self.player.getRotatedFacing() + rotation)

    def in_room(self, room, x, y):
        if x < 0 or y < 0:
            return False
        if x >= room.width or y >= room.height:
            return False
        return True

    def move_player(self, forward):
        if self.player.moving:
            return

        (mx, my) = self.player.get_facing_delta()
        (px, py) = self.player.getPos()
        (nx, ny) = (px + mx, py + my) if forward else (px - mx, py - my)
        if self.object_at(nx, ny) is None and self.in_room(self.room, nx, ny):
            self.player.move_to(px, py, nx, ny)

    def swap_player(self):
        pi = self.room.actors.index(self.player)
        new_player = self.room.actors[pi+1] if pi < len(
            self.room.actors) - 1 else self.room.actors[0]
        self.player.setIsPlayer(False)
        new_player.setIsPlayer(True)
        self.player = new_player
        self.new_message("Swapped players")

    def new_message(self, message):
        self.instructions = self.myfont.render(message, True, (255, 255, 0))

    def game_loop(self):
        running = True

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
                        elif event.key == pygame.K_LEFT:
                            self.rotate_player(-1)
                        elif event.key == pygame.K_RIGHT:
                            self.rotate_player(1)
                        elif event.key == pygame.K_UP:
                            self.move_player(True)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(False)
                        elif event.key == pygame.K_p:
                            self.swap_player()
                        elif event.key == pygame.K_PRINTSCREEN:
                            pygame.image.save(self.screen, "screenshot.png")
                            self.new_message("Screenshot saved to screenshot.png")
                    except AttributeError:
                        pass
                elif event.type == self.animation_event:
                    for actor in self.room.actors:
                        actor.animate()
                        if actor != self.player:
                            actor.face_player(self.player.x, self.player.y)
                elif event.type == self.movement_event:
                    actors_in_motion = [
                        actor for actor in self.room.actors if actor.getMoving()]

                    if actors_in_motion:
                        for actor in actors_in_motion:
                            actor.update()

            self.screen.fill((0, 0, 0))

            self.room.draw(self.screen, self.rotation)

            self.screen.blit(self.instructions, ((self.screen.get_width() - self.instructions.get_width())//2, \
                self.screen.get_height() - 5 * self.instructions.get_height()))

            pygame.display.flip()

        pygame.time.set_timer(self.animation_event, 0)
        pygame.time.set_timer(self.movement_event, 0)


if __name__ == '__main__':
    amulet = Amulet()
    amulet.game_loop()
    print("Thanks for playing!")
    pygame.quit()
    sys.exit()
