import pygame
import json
import os

json_fn = 'amulet.dat'

class Wintro:
    def __init__(self, screen, myfont):
        intro_data = json.load(open(json_fn))['wintro']
        self.screen = screen
        self.myfont = myfont
        self.intro_pic = pygame.image.load(os.path.join('images',intro_data['intro_file_pic']))
        self.titleFont = pygame.font.SysFont(None, 48)
        self.continue_text = self.myfont.render(
            intro_data['press_escape_to_continue'], True, (255, 255, 255))
        self.title_text = self.titleFont.render(
            intro_data['title_banner'], True, (255, 255, 255))
        self.intro_lines = [self.myfont.render(
            line, True, (255, 255, 0)) for line in intro_data['intro_text'].split("\n")]
        self.scroll_speed = intro_data['scroll_speed']

    def game_loop(self):
        start_time = pygame.time.get_ticks()
        line_height = self.myfont.get_linesize()

        running = True
        while running:
            elapsed_time = pygame.time.get_ticks() - start_time
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    elif event.key == pygame.K_RETURN:
                        running = False
                        break
                    elif event.key == pygame.K_PRINTSCREEN:
                        pygame.image.save(self.screen, "screenshot.png")

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.intro_pic, ((self.screen.get_width(
            ) - self.intro_pic.get_height())/2, (self.screen.get_height() - self.intro_pic.get_height())/2))

            start_y = self.screen.get_height()/2 - (len(self.intro_lines) * line_height)/2

            for i, line in enumerate(self.intro_lines):
                xparency = 255 - \
                    ((elapsed_time - self.scroll_speed * i) / self.scroll_speed) * 255
                xparency = 255 - max(0, min(255, xparency))
                line.set_alpha(xparency)
                self.screen.blit(line, (self.screen.get_width(
                )/2 - line.get_width()/2, start_y + (i * line_height)))

            self.screen.blit(self.title_text, (self.screen.get_width(
            )/2 - self.title_text.get_width()/2, self.screen.get_height()/4 - self.title_text.get_height()/2))
            self.screen.blit(self.continue_text, (self.screen.get_width(
            )/2 - self.continue_text.get_width()/2, self.screen.get_height() - 3 * self.continue_text.get_height()))
            pygame.display.flip()

        return running
