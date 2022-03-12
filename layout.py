import pygame
from enum import Enum
import json
import os
from finder import helper

json_fn = 'amulet.dat'

class TextColor(Enum):
    NORMAL = 0
    BRIGHT = 1
    COOL = 2

class Layout:
    def __init__(self):
        layout = json.load(open(json_fn))['layout']
        pygame.init()
        pygame.font.init()
        self.screen_width = layout['screen_width']
        self.screen_height = layout['screen_height']

        if 'gameport' in layout:
            self.gameport_rect = layout['gameport']
            self.gameport = pygame.Surface((layout['gameport'][2], layout['gameport'][3]))
        else:
            self.gameport = None

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.logo_image = pygame.image.load(helper(layout['logo_pic']))
        self.logo_rect = layout['logo']
        self.stats_rect = layout['stats']
        self.messages_rect = layout['messages']
        self.num_messages = layout['num_messages']
        self.game_rect = layout['game']
        self.game_screen = pygame.Surface((self.game_rect[2], self.game_rect[3]))
        self.bg_color = pygame.Color(layout['bg_color'])
        self.text_color = pygame.Color(layout['text_color'])
        self.bright_text_color = pygame.Color(layout['bright_color'])
        self.cool_text_color = pygame.Color(layout['cool_color'])
        self.messages = []
        self.font = pygame.font.SysFont(None, 24)
    
    def clear(self):
        self.screen.fill(self.bg_color)
    
    def draw(self, game_state):
        self.clear()
        self.draw_logo()
        self.draw_stats(game_state)
        self.draw_messages()
        self.draw_game(game_state)
        self.drawscale()

    def drawscale(self):
        # resize self.screen into self.realscreen
        pygame.display.flip()

    def draw_game(self, game_state):
        self.game_screen.fill(self.bg_color)
        game_state.draw()
        if self.gameport:
            pygame.transform.scale(self.game_screen, (self.gameport.get_width(), self.gameport.get_height()), self.gameport)
            self.screen.blit(self.gameport, self.gameport_rect)
        else:
            self.screen.blit(self.game_screen, self.game_rect)

    def draw_logo(self):
        image_rect = self.logo_image.get_rect()
        image_rect.center = self.logo_rect[0] + self.logo_rect[2]/2, self.logo_rect[1] + self.logo_rect[3]/2
        self.screen.blit(self.logo_image, image_rect)

    def draw_stats(self, amulet):
        player = amulet.get_player()
        lines = list()

        if player:
            lines.append((TextColor.BRIGHT, f"You are {player.name}"))
            lines.append((TextColor.NORMAL, ""))
            lines.append((TextColor.NORMAL, f"Health: {player.get_health()}/{player.get_max_health()}"))
            lines.append((TextColor.NORMAL, ""))
            lines.append((TextColor.COOL, "Inventory"))
            lines.append((TextColor.NORMAL, ""))

            for index, item in enumerate(player.inventory):
                lines.append((TextColor.NORMAL, chr(ord('a')+index) + ") " + str(item)))

            lines.append((TextColor.NORMAL, ""))
            lines.append((TextColor.COOL, "Target"))
            lines.append((TextColor.NORMAL, ""))

            if not player.target:
                lines.append((TextColor.NORMAL, "Nothing Targeted"))
            else:
                lines.append((TextColor.NORMAL, f"{player.target.name} at {int(player.target.x)}, {int(player.target.y)}"))

        lines.append((TextColor.NORMAL, ""))
        lines.append((TextColor.COOL, "Commands"))
        lines.append((TextColor.NORMAL, ""))
        lines.append((TextColor.NORMAL, "ESC - Quit"))
        lines.append((TextColor.NORMAL, "TAB - Target"))
        lines.append((TextColor.NORMAL, "PrtSc - Screenshot"))
        lines.append((TextColor.NORMAL, ". - Rest"))
        lines.append((TextColor.NORMAL, "a - Attack Target"))
        lines.append((TextColor.NORMAL, "g - Get Item"))
        lines.append((TextColor.NORMAL, "P - Put On/Take Off Item"))
        lines.append((TextColor.NORMAL, "T - Toss Item"))
        lines.append((TextColor.NORMAL, "W - Wield/Unwield Item"))

        self.draw_lines(self.stats_rect, lines, True)
    
    def draw_messages(self):
        self.draw_lines(self.messages_rect, self.messages)
    
    def draw_lines(self, rect, lines, center = False):
        y = rect[1]
        for line in lines:
            color, message = line
            text = self.font.render(message, True, self.get_text_color(color))
            text_rect = text.get_rect()
            if center:
                x = rect[0] + rect[2]/2 - text_rect.width/2
                self.screen.blit(text, (x, y + 5 + text_rect[1], text_rect[2], text_rect[3]))
            else:
                self.screen.blit(text, (5 + rect[0] + text_rect[0], y + 5 + text_rect[1], text_rect[2], text_rect[3]))
            y += self.font.get_linesize()
    
    def get_text_color(self, color):
        if color == TextColor.BRIGHT:
            return self.bright_text_color
        elif color == TextColor.COOL:
            return self.cool_text_color
        else:
            return self.text_color
    
    def add_message(self, message, color = TextColor.NORMAL):
        self.messages.append((color, message))
        if len(self.messages) > self.num_messages:
            self.messages.pop(0)