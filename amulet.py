import random
import pygame
from actor import Actor
from item import Item
from staticobject import StaticObject
from functools import reduce
from layout import Layout, TextColor
from enum import Enum

class ExitState(Enum):
    RUNNING = 0
    QUIT = 1
    DIED = 3
    WON = 4
    WORE_AMULET = 5
class Amulet:
    def __init__(self, layout: Layout):
        self.layout = layout
        self.screen = layout.game_screen
        self.myfont = layout.font
        self.floors = []
        self.animation_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.animation_event, 250)
        self.movement_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.movement_event, 1000//120)
        self.actors = []
        self.end_game_event = pygame.USEREVENT + 3
        self.item_phrase_event = pygame.USEREVENT + 4
        pygame.time.set_timer(self.item_phrase_event, 10000)
        self.state = ExitState.RUNNING

        self.new_message("Welcome to You are the Amulet!, an entry to the 7DRL 2022 Challenge")
        self.new_alert("Follow along at https://chasingdings.com/category/other-games/7drl/")

    def get_player_room(self):
        for actor in self.actors:
            if isinstance(actor, Actor) and actor.getIsPlayer():
                return actor.room
        return None

    def get_player(self):
        for actor in self.actors:
            if isinstance(actor, Actor) and actor.getIsPlayer():
                return actor
        return None

    def add_floor(self, floor):
        self.floors.append(floor)

    def get_floors(self):
        return self.floors

    def object_at(self, x, y):
        room = self.get_player_room()
        for actor in self.actors:
            if actor.room == room and actor.getPos() == (x, y):
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
        return (x, y) in room.good_spaces

    def leave(self, nx, ny):
        player = self.get_player()
        room = self.get_player_room()
        floor = self.get_floors()[0]

        exits = [(con, dest)
                 for exit in floor.exits for con in exit.connections
                 for dest in exit.connections if con[0] == room and dest[0] != room]

        for exit in exits:
            con, dest = exit
            if nx == con[1] and ny == con[2]:
                self.new_alert("Moving to room: " + dest[0].name)
                (mx, my) = player.get_facing_delta()
                player.room = dest[0]
                player.x = dest[1] + mx
                player.y = dest[2] + my
                player.pos = (player.x, player.y)
                return True

        return False

    def move_player(self, forward):
        player = self.get_player()
        room = self.get_player_room()

        if player.moving:
            return

        (mx, my) = player.get_facing_delta()
        (px, py) = player.getPos()
        (nx, ny) = (px + mx, py + my) if forward else (px - mx, py - my)

        if not self.leave(nx, ny):
            if self.object_at(nx, ny) is None and self.in_room(room, nx, ny):
                player.move_to(px, py, nx, ny)

    def swap_player(self):
        player = self.get_player()
        local_actors = self.actors_in_room(player.room)
        pi = local_actors.index(player)
        new_player = local_actors[pi+1] if pi < len(
            local_actors) - 1 else local_actors[0]
        player.setIsPlayer(False)
        new_player.setIsPlayer(True)
        self.new_alert(f"You are now {new_player.name}")

    def pick_up_items(self, player, objects):
        picked_up_amulet = False
        for_removal = list()
        for obj in objects:
            if not isinstance(obj, Actor) and obj.x == player.x and obj.y == player.y:
                for_removal.append(obj)
                inventory_item = Item(self.weapons[obj.name])
                player.inventory.append(inventory_item)
                self.new_alert(f"You picked up {str(inventory_item)}.")
                picked_up_amulet |= inventory_item.isyendor
        for obj in for_removal:
            self.actors.remove(obj)
        if picked_up_amulet:
            self.new_alert("Please type 'P' and then 'b' to put on the amulet.")

    def new_message(self, message):
        self.layout.add_message(message, TextColor.BRIGHT)

    def new_alert(self, message):
        self.layout.add_message(message)

    def actors_in_room(self, room):
        return list(actor for actor in self.actors if isinstance(actor, Actor) and actor.room == room and actor.alive)

    def objects_in_room(self, room):
        return list(actor for actor in self.actors if isinstance(actor, StaticObject) and actor.room == room)

    def attack(self, attacker, victim):
        msg = f"{attacker.pronoun_subject()} {victim.pronoun_object()} with {attacker.wielding()}."
        victim.health -= 1
        self.new_alert(msg)

    def kill_non_player(self, actors: list):
        for actor in actors:
            if not actor.getIsPlayer():
                actor.kill()
                self.new_alert(f"{actor.name} is dead.")

    def any_npcs_alive(self):
        return reduce(lambda x, y: x or y, [a.alive for a in self.actors if isinstance(a, Actor) and not a.getIsPlayer()])
    
    def handle_inventory(self, player, option, selection):
        item_index = selection - pygame.K_a
        if item_index < 0 or item_index >= len(player.inventory):
            self.new_alert("Invalid selection.")
        else:
            item = player.inventory[item_index]
            if option == 'P':
                if item.adorned:
                    self.new_alert("You have already put that on.")
                elif not item.can_put_on:
                    self.new_alert("You cannot put that on.")
                else:
                    self.new_alert(f"You put on {str(item)}.")
                    item.put_on()
                    if item.isyendor:
                        self.state = ExitState.WORE_AMULET

    def game_loop(self):
        self.state = ExitState.RUNNING
        playerMoved = False
        waiting_for_selection = None
        waiting_for_godot = False

        while self.state == ExitState.RUNNING:
            room = self.get_player_room()
            player = self.get_player()
            actors = self.actors_in_room(room)
            objects = self.objects_in_room(room)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = ExitState.QUIT
                    break
                elif event.type == pygame.KEYDOWN:
                    try:
                        if waiting_for_selection:
                            self.handle_inventory(player, waiting_for_selection, event.key)
                            waiting_for_selection = False
                            continue

                        # Was it the Escape key? If so, stop the loop.
                        if event.key == pygame.K_ESCAPE:
                            self.state = ExitState.QUIT
                            break
                        elif event.key == pygame.K_LEFT:
                            if player.alive:
                                self.rotate_player(-1)
                        elif event.key == pygame.K_RIGHT:
                            if player.alive:
                                self.rotate_player(1)
                        elif event.key == pygame.K_UP:
                            if player.alive:
                                self.move_player(True)
                                playerMoved = True
                        elif event.key == pygame.K_DOWN:
                            if player.alive:
                                self.rotate_player(2)
                        elif event.key == pygame.K_p and event.mod & pygame.KMOD_SHIFT:
                            self.new_alert("Put on what? (type letter of item)")
                            waiting_for_selection = 'P'
                            break
                        elif event.key == pygame.K_g:
                            if player.alive:
                                self.pick_up_items(player, objects)
                        elif event.key == pygame.K_k and event.mod & pygame.KMOD_SHIFT:
                            if player.alive:
                                self.kill_non_player(actors)
                        elif event.key == pygame.K_PRINTSCREEN:
                            pygame.image.save(self.layout.screen, "yata-screenshot.png")
                            self.layout.add_message("Screenshot saved to yata-screenshot.png", TextColor.COOL)
                    except AttributeError:
                        pass
                elif event.type == self.item_phrase_event:
                    self.items_speak(objects, player)
                elif event.type == self.end_game_event:
                    self.state = ExitState.DIED if waiting_for_godot else ExitState.WON
                elif event.type == self.animation_event:
                    for actor in (a for a in actors if a.room == room and a.alive):
                        actor.animate()
                        if actor != player:
                            actor.face_player(player.x, player.y)
                elif event.type == self.movement_event:
                    for actor in [a for a in actors if a.getMoving() and a.alive]:
                        actor.update()
                    if playerMoved:
                        for actor in [a for a in actors if not a.getMoving() and not a.getIsPlayer() and a.alive]:
                            bad_spaces = set(
                                (b for a in objects for b in a.i_am_at() if a != actor))
                            bad_spaces = room.bad_spaces | bad_spaces
                            ready_to_attack = actor.pathfind(
                                player, bad_spaces)
                            if ready_to_attack:
                                self.attack(actor, player)
                        playerMoved = False

            if not waiting_for_godot and player.health <= 0:
                player.kill()
                self.new_message("You died.")
                pygame.time.set_timer(self.end_game_event, 5000)
                waiting_for_godot = True

            if not waiting_for_godot and player.alive and not self.any_npcs_alive():
                self.new_message("You killed everything!")
                pygame.time.set_timer(self.end_game_event, 5000)
                waiting_for_godot = True

            self.layout.draw(self)

        pygame.time.set_timer(self.animation_event, 0)
        pygame.time.set_timer(self.movement_event, 0)
        pygame.time.set_timer(self.item_phrase_event, 0)
        pygame.time.set_timer(self.end_game_event, 0)

        return self.state

    def items_speak(self, objects, player):
        random.seed()
        for obj in objects:
            if obj.ontop:
                print (f"object position: {obj.getPos()} actor position: {player.getPos()}")
            if obj.ontop and obj.x == player.x and obj.y == player.y:
                self.new_message(obj.name + ' says, "' + obj.ontop + '"')
            elif obj.phrases:
                self.new_message(obj.name + ' calls out, "' + random.choice(obj.phrases) + '"')

    def draw(self):
        room = self.get_player_room()
        objects = self.objects_in_room(room)
        room.draw(self.screen, objects, self.get_floors()[0].exits)
