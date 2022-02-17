import pygame
from spritesheet import SpriteSheet
from pygame.time import Clock
from room import Room, init_rooms
import sys
from itertools import cycle
from floor import Floor
from random import randint, shuffle
from actor import Babus, Archer, Templar, Mog


class Amulet:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((768, 640))
        self.myfont = pygame.font.SysFont(None, 24)
        self.floors = []
        init_rooms()
        self.clock = Clock()
        self.rotation = 0
        self.animation_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.animation_event, 250)
        self.movement_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.movement_event, 1000//120)

        self.new_message("Use the arrow keys to move around. Press P to swap players. Press ESC to quit.")
        self.new_alert("Welcome to Tactics Roguelike Engine Advance!")
    
    def get_player_room(self):
        for floor in self.floors:
            for room in floor.rooms:
                for actor in room.actors:
                    if actor.getIsPlayer():
                        return room
        return None
    
    def get_player(self):
        for floor in self.floors:
            for room in floor.rooms:
                for actor in room.actors:
                    if actor.getIsPlayer():
                        return actor
        return None

    def add_floor(self, floor):
        self.floors.append(floor)
    
    def get_floors(self):
        return self.floors

    def object_at(self, x, y):
        for actor in self.get_player_room().actors:
            if actor.getPos() == (x, y):
                return actor
        return None

    def rotate_player(self, rotation):
        player = self.get_player()
        player.setFacing(player.getRotatedFacing() + rotation)

    def in_room(self, room, x, y):
        if x < 0 or y < 0:
            return False
        if x >= room.width or y >= room.height:
            return False
        return True

    def move_player(self, forward):
        player = self.get_player()
        room = self.get_player_room()

        if player.moving:
            return

        (mx, my) = player.get_facing_delta()
        (px, py) = player.getPos()
        (nx, ny) = (px + mx, py + my) if forward else (px - mx, py - my)
        if self.object_at(nx, ny) is None and self.in_room(room, nx, ny):
            player.move_to(px, py, nx, ny)

    def swap_player(self):
        room = self.get_player_room()
        player = self.get_player()
        pi = room.actors.index(player)
        new_player = room.actors[pi+1] if pi < len(
            room.actors) - 1 else room.actors[0]
        player.setIsPlayer(False)
        new_player.setIsPlayer(True)
        self.new_alert("Swapped players")

    def new_message(self, message):
        self.instructions = self.myfont.render(message, True, (255, 255, 255))

    def new_alert(self, message):
        self.alert = self.myfont.render(message, True, (255, 255, 0))
        self.alert_time = pygame.time.get_ticks()

    def game_loop(self):
        running = True

        while running:
            room = self.get_player_room()
            player = self.get_player()

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
                            self.new_alert("Screenshot saved to screenshot.png")
                    except AttributeError:
                        pass
                elif event.type == self.animation_event:
                    for actor in room.actors:
                        actor.animate()
                        if actor != player:
                            actor.face_player(player.x, player.y)
                elif event.type == self.movement_event:
                    actors_in_motion = [
                        actor for actor in room.actors if actor.getMoving()]

                    if actors_in_motion:
                        for actor in actors_in_motion:
                            actor.update()

            self.screen.fill((0, 0, 0))

            room.draw(self.screen, self.rotation)

            self.screen.blit(self.instructions, ((self.screen.get_width() - self.instructions.get_width())//2, \
                self.screen.get_height() - 5 * self.instructions.get_height()))

            # if alert is set, display it for a while
            if self.alert is not None:
                if pygame.time.get_ticks() - self.alert_time > 5000:
                    self.alert = None
                else:
                    self.screen.blit(self.alert, ((self.screen.get_width() - self.alert.get_width())//2, \
                        self.screen.get_height() - 6 * self.alert.get_height()))

            pygame.display.flip()

        pygame.time.set_timer(self.animation_event, 0)
        pygame.time.set_timer(self.movement_event, 0)


def create_map(amulet: Amulet):
    floor = Floor('Test Floor')
    amulet.add_floor(floor)

    room = Room(randint(7, 10), randint(7, 10), '02')
    floor.add_room(room)

    all_spaces = [(x, y) for x in range(room.width) for y in range(room.height)]
    shuffle(all_spaces)
    player = Babus(all_spaces.pop())
    player.setIsPlayer(True)
    room.actors.append(player)
    room.actors.append(Archer(all_spaces.pop()))
    room.actors.append(Templar(all_spaces.pop()))
    room.actors.append(Mog(all_spaces.pop()))

if __name__ == '__main__':
    amulet = Amulet()
    create_map(amulet)
    amulet.game_loop()
    print("Thanks for playing!")
    pygame.quit()
    sys.exit()
