import pygame

intro_file_pic = "intropic.png"

intro_text = """A Game You Cannot Win
A Game You Cannot Lose
A Game You Cannot Forget
A Game You Will Not Remember"""

press_escape_to_continue = "Press ESC to continue"
title_banner = "7DRL Tactics Roguelike Engine Advance"

class Intro:
    def __init__(self, screen, myfont):
        self.screen = screen
        self.myfont = myfont
        self.intro_pic = pygame.image.load(intro_file_pic)
        self.titleFont = pygame.font.SysFont(None, 48)
        self.continue_text = self.myfont.render(press_escape_to_continue, True, (255, 255, 255))
        self.title_text = self.titleFont.render(title_banner, True, (255, 255, 255))
        self.intro_lines = [self.myfont.render(line, True, (255, 255, 0)) for line in intro_text.split("\n")]
    
    def game_loop(self):
        start_time = pygame.time.get_ticks()

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
            self.screen.blit(self.intro_pic, (0, 0))

            start_y = self.screen.get_height()/2 - (len(self.intro_lines) * self.myfont.get_height())

            for i, line in enumerate(self.intro_lines):
                xparency = 255 - ((elapsed_time - 2000 * i)/ 2000) * 255
                xparency = 255 - max(0, min(255, xparency))
                line.set_alpha(xparency)
                self.screen.blit(line, (self.screen.get_width()/2 - line.get_width()/2, start_y + (i * 2 * self.myfont.get_height())))

            self.screen.blit(self.title_text, (self.screen.get_width()/2 - self.title_text.get_width()/2, self.screen.get_height()/4 - self.title_text.get_height()/2))
            self.screen.blit(self.continue_text, (self.screen.get_width()/2 - self.continue_text.get_width()/2, self.screen.get_height() - 3 * self.continue_text.get_height()))
            pygame.display.flip()

        return running