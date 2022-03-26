from math import sqrt
import random
import pygame
from actor import Actor
from item import Item, martialArts
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

class MartialArts(Item):
    def __init__(self, name, description, damage, damage_type):
        super().__init__(name, description)
        self.damage = damage
        self.damage_type = damage_type

class Amulet:
    def __init__(self, layout: Layout):
        self.layout = layout
        self.screen = layout.game_screen
        self.myfont = layout.font
        self.floors = []
        self.animation_event = pygame.USEREVENT + 1
        self.movement_event = pygame.USEREVENT + 2
        self.actors = []
        self.end_game_event = pygame.USEREVENT + 3
        self.item_phrase_event = pygame.USEREVENT + 4
        self.expire_corpse_event = pygame.USEREVENT + 5

        self.state = ExitState.RUNNING

        self.new_message(
            "Welcome to You are the Amulet!, an entry to the 7DRL 2022 Challenge")
        self.new_alert(
            "Follow along at https://chasingdings.com/category/other-games/7drl/")

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
            if actor.room == room and actor.getPos() == (x, y) and isinstance(actor, Actor):
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
            self.new_alert(
                "Please type 'P' and then 'c' to put on the amulet.")
    
    def remove_amulet(self, player):
        for item in player.inventory:
            if item.isyendor:
                player.inventory.remove(item)
                return True
        return False

    def new_message(self, message):
        self.layout.add_message(message, TextColor.BRIGHT)

    def new_alert(self, message):
        self.layout.add_message(message)

    def actors_in_room(self, room):
        return list(actor for actor in self.actors if isinstance(actor, Actor) and actor.room == room and actor.alive)

    def objects_in_room(self, room):
        return list(actor for actor in self.actors if isinstance(actor, StaticObject) and actor.room == room)

    def attack(self, attacker, victim):
        victim_item = victim.get_wielded()
        if victim_item is None:
            victim_item = martialArts
        item = attacker.get_wielded()
        if item is None:
            item = martialArts
        msg = f"{attacker.pronoun_subject()} {victim.pronoun_object()} with {attacker.wielding()}"
        if item.hit():
            blocker = victim.get_blocker()
            if blocker:
                msg += ", but it was blocked."
                blocker.attack_with()
            else:
                damage = item.roll_damage()
                victim.set_health(victim.get_health() - damage)
                msg += f" for {damage} damage."
                if item.is_vampiric():
                    healing = min(attacker.get_health() + damage, attacker.get_max_health()) - attacker.get_health()
                    if healing:
                        attacker.set_health(attacker.get_health() + healing)
                        msg += f" {attacker.pronoun_subject('gain')} {healing} health."
        else:
            msg += ", but it missed."
        self.new_alert(msg)
        if victim.get_health() <= 0:
            self.new_alert(f"{victim.name} died.")
            victim.kill()
        item.attack_with()

    def kill_non_player(self, actors: list):
        for actor in actors:
            if not actor.getIsPlayer():
                actor.kill()
                self.new_alert(f"{actor.name} is dead.")

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
            elif option == 'T':
                if not player.target:
                    self.new_alert("You must first target an enemy.")
                elif item.is_wielded():
                    self.new_alert(
                        "You cannot throw something you are wielding.")
                elif sqrt((player.target.x - player.x)**2 + (player.target.y - player.y)**2) > 4:
                    self.new_alert("You are too far away.")
                elif len(player.target.inventory) >= 10:
                    self.new_alert(player.target.name, "is carrying too much.")
                else:
                    player.inventory.remove(item)
                    player.target.inventory.append(item)
                    self.new_alert(
                        f"You throw {str(item)} at {player.target.name}.")
                    if item.isyendor:
                        player.setIsPlayer(False)
                        player.target.setIsPlayer(True)
                        self.new_alert(f"You are now {player.target.name}.")
                        player.target.target = None
                        player.target = None
                        item.adorned = True
            elif option == 'W':
                if not item.can_wield():
                    self.new_alert("You cannot wield this item.")
                else:
                    for pitem in player.inventory:
                        if pitem.is_wielded():
                            if item != pitem:
                                pitem.wield()
                                self.new_alert(
                                    f"You are no longer wielding {str(pitem)}.")
                    if item.wield():
                        self.new_alert(f"You are now wielding {str(item)}.")
                    else:
                        self.new_alert(
                            f"You are no longer wielding {str(item)}")

    def get_eligible_actors(self, player, actors):
        return list(actor for actor in actors if actor.alive and actor != player)

    def switch_target(self, player, actors):
        eligible_actors = self.get_eligible_actors(player, actors)
        if len(eligible_actors) == 0:
            self.new_alert("There is no one to attack.")
            player.target = None
            return
        if player.target is None:
            player.target = eligible_actors[0]
        else:
            player.target = eligible_actors[(eligible_actors.index(
                player.target) + 1) % len(eligible_actors)]

    def verify_target(self, player, actors):
        if player.target and (not player.target.alive or player.target not in actors):
            self.new_alert("You have no target.")
            player.target = None

    def expire_weapons(self):
        for actor in self.actors:
            if isinstance(actor, Actor):
                weapons_to_expire = [item for item in actor.inventory if item.quantity < 1]
                for item in weapons_to_expire:
                    actor.inventory.remove(item)

    def expire_corpses(self):
        corpses = list(actor for actor in self.actors if isinstance(
            actor, Actor) and (not actor.alive or actor.get_health() <= 0))
        if corpses:
            for corpse in corpses:
                self.actors.remove(corpse)
    
    def dump_map(self):
        for room in self.floors[0].rooms:
            filename = f"{room.name}.png"
            self.layout.clear()
            self.layout.game_screen.fill(self.layout.bg_color)
            self.draw(room, True)
            # save game_screen to file
            pygame.image.save(self.layout.game_screen, filename)

    def game_loop(self, killEverything=False):
        self.state = ExitState.RUNNING
        playerMoved = False
        waiting_for_selection = None
        waiting_for_godot = False
        saving_ani = False
        ani_frame = 0

        # animation happens on 1/4s timer
        pygame.time.set_timer(self.animation_event, 250)
        # movement happens on 1/8s timer
        pygame.time.set_timer(self.movement_event, 1000//120)
        # talking things talk on 10s timer
        pygame.time.set_timer(self.item_phrase_event, 10000)
        # expire corpses on 30s timer
        pygame.time.set_timer(self.expire_corpse_event, 30 * 1000)

        while self.state == ExitState.RUNNING:
            room = self.get_player_room()

            if not room:
                self.state = ExitState.QUIT
                break

            player = self.get_player()
            actors = self.actors_in_room(room)
            objects = self.objects_in_room(room)

            if room.takeAmulet and self.remove_amulet(player):
                self.new_message("With a wave of her hand, the Wizard of Yendor takes the Amulet of Yendor from you.")
                self.new_alert("The Wizard of Yendor says, \"You have done well.\"")
                self.new_alert("The Wizard of Yendor says, \"Now, come get your reward.\"")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = ExitState.QUIT
                    break
                elif event.type == pygame.KEYDOWN:
                    try:
                        if waiting_for_selection:
                            self.handle_inventory(
                                player, waiting_for_selection, event.key)
                            waiting_for_selection = False
                            playerMoved = True
                            continue

                        # Was it the Escape key? If so, stop the loop.
                        if event.key == pygame.K_ESCAPE:
                            self.state = ExitState.QUIT
                            break
                        elif event.key == pygame.K_PERIOD:
                            playerMoved = True
                            player.set_health(min(player.get_health() + 1, player.get_max_health()))
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
                        elif event.key == pygame.K_F12:
                            saving_ani = True
                            ani_frame = 0
                        elif event.key == pygame.K_TAB:
                            self.switch_target(player, actors)
                        elif event.key == pygame.K_a:
                            if player.alive and player.target and player.in_range:
                                player.face_player(
                                    player.target.x, player.target.y)
                                self.attack(player, player.target)
                                playerMoved = True
                        elif event.key == pygame.K_p:
                            self.new_alert(
                                "Put on or take off what? (type letter of item)")
                            waiting_for_selection = 'P'
                            break
                        elif event.key == pygame.K_t:
                            self.new_alert("Toss what? (type letter of item)")
                            waiting_for_selection = 'T'
                            break
                        elif event.key == pygame.K_w:
                            self.new_alert(
                                "Wield or unwield what? (type letter of item)")
                            waiting_for_selection = 'W'
                            break
                        elif event.key == pygame.K_g:
                            if player.alive:
                                self.pick_up_items(player, objects)
                                playerMoved = True
                        elif event.key == pygame.K_k:
                            if player.alive:
                                self.kill_non_player(actors)
                        elif event.key == pygame.K_PRINTSCREEN:
                            pygame.image.save(
                                self.layout.screen, "yata-screenshot.png")
                            self.layout.add_message(
                                "Screenshot saved to yata-screenshot.png", TextColor.COOL)
                    except AttributeError:
                        pass
                elif event.type == self.expire_corpse_event:
                    self.expire_corpses()
                elif event.type == self.item_phrase_event:
                    self.items_speak(objects, player)
                elif event.type == self.end_game_event:
                    self.state = ExitState.DIED if not player.alive else ExitState.WON
                elif event.type == self.animation_event:
                    self.expire_weapons()
                    for actor in (a for a in actors if a.room == room and a.alive):
                        actor.animate()
                        if actor != player and actor.in_range:
                            actor.face_player(player.x, player.y)
                    if saving_ani:
                        pygame.image.save(self.layout.screen,
                                          f"animation-{ani_frame:04}.png")
                        ani_frame += 1
                        if ani_frame == 4:
                            saving_ani = False
                            ani_frame = 0
                            self.layout.add_message(
                                "Finished recording animation", TextColor.COOL)
                elif event.type == self.movement_event:
                    for actor in [a for a in actors if a.getMoving() and a.alive]:
                        actor.update()
                    for actor in [a for a in actors if not a.getMoving() and a.alive]:
                        bad_spaces = set(
                            (b for a in actors for b in a.i_am_at() if a != actor))
                        bad_spaces = room.bad_spaces | bad_spaces
                        if actor.getIsPlayer():
                            if actor.target:
                                actor.in_range = actor.good_pos(
                                    actor.getPos(), actor.target.getPos(), bad_spaces)
                                #print (f"{actor.name} in range: {actor.in_range}")
                            else:
                                actor.in_range = False
                                #print (f"No target")
                        elif playerMoved:
                            if not actor.getIsPlayer() and actor.needs_to_wield():
                                self.new_alert(f"{actor.name} is now wielding {str(actor.get_wielded())}")
                                continue
                            actor.in_range = actor.pathfind(player, bad_spaces)
                            actor.target = player
                            if actor.in_range:
                                self.attack(actor, player)
                    playerMoved = False

            self.verify_target(player, actors)

            if not waiting_for_godot and player.get_health() <= 0:
                player.kill()
                self.new_message("You died.")
                pygame.time.set_timer(self.end_game_event, 5000)
                waiting_for_godot = True

            if not waiting_for_godot and player.alive and killEverything and not self.get_eligible_actors(player, actors):
                self.new_message("You killed everything!")
                pygame.time.set_timer(self.end_game_event, 5000)
                waiting_for_godot = True

            self.layout.draw(self)

        pygame.time.set_timer(self.animation_event, 0)
        pygame.time.set_timer(self.movement_event, 0)
        pygame.time.set_timer(self.item_phrase_event, 0)
        pygame.time.set_timer(self.end_game_event, 0)
        pygame.time.set_timer(self.expire_corpse_event, 0)

        return self.state

    def items_speak(self, objects, player):
        for obj in objects:
            if obj.ontop and obj.x == player.x and obj.y == player.y:
                self.new_message(obj.name + ' says, "' + obj.ontop + '"')
            elif obj.phrases:
                self.new_message(obj.name + ' calls out, "' +
                                 random.choice(obj.phrases) + '"')

    def draw(self, room=None, dump=False):
        if not room: room = self.get_player_room()

        if room:
            if dump:
                room.draw(self.screen, [], [], True)
            else:
                objects = self.objects_in_room(room)
                room.draw(self.screen, objects, self.get_floors()[0].exits)

                if room.phrases:
                    y = 5
                    for phrase in room.phrases:
                        message = self.myfont.render(
                            phrase, True, self.layout.get_text_color(TextColor.BRIGHT))
                        x = (self.screen.get_width() - message.get_width()) // 2
                        self.screen.blit(message, (x, y))
                        y += self.myfont.get_linesize()
