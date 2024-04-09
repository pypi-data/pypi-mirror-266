""" Slice It Off! - Game where you slice the area where enemies reside to
    the minimum
"""

from pathlib import Path

import pygame

from sliceitoff.display import Display
from sliceitoff.text import Fonts
from sliceitoff.stats import Stats
from sliceitoff.screens import (
    hiscores_screen,
    instructions1_screen,
    instructions2_screen)
from sliceitoff.hiscores import HiScores
from sliceitoff.mainmenu import Mainmenu, MenuItems

from .level import Level
from .show import Show
from .initials import Initials

class Game:
    """ This is the whole game. """
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.display = Display()
        self.stats = None
        self.hiscores = HiScores()
        Fonts.load_fonts( Path(__file__).parent.parent.resolve() )
        pygame.mouse.set_visible(False)

    def __del__(self):
        pygame.quit()

    def instructions(self):
        """ displays instruction and waits a key """
        for page in [instructions1_screen, instructions2_screen]:
            screen = Show(page())
            while screen.active:
                screen.update(dt = self.clock.tick())
                self.display.update( [screen] )

    def show_highscores(self):
        """ displays highscores and waits a key """
        his = Show(hiscores_screen(str(self.hiscores)))
        while his.active:
            his.update(dt = self.clock.tick())
            self.display.update( [his] )

    def newgame(self):
        """ new game, new score, runs through levels till game over """
        self.stats = Stats()
        while self.stats.lives:
            level = Level(stats = self.stats)
            while level.active:
                level.update(dt = self.clock.tick())
                self.display.update( [level] )
            if self.stats.lives:
                self.stats.level_up()

    def initials(self):
        """ asks for initials in case of high enough score """
        initials = Initials()
        while initials.active:
            initials.update(dt = self.clock.tick())
            self.display.update([initials])
        return initials.name

    def mainmenu(self):
        """ menu where one select what to do """
        menu = Mainmenu()
        while menu.active:
            menu.update(dt = self.clock.tick())
            self.display.update([menu])
        return menu.selection

    def run(self):
        """ This is the main loop of the game """
        while True:
            match self.mainmenu():
                case MenuItems.QUIT:
                    break
                case MenuItems.HISCORES:
                    self.show_highscores()
                case MenuItems.INSTRUCT:
                    self.instructions()
                case MenuItems.NEWGAME:
                    self.newgame()
                    if self.hiscores.high_enough(self.stats.score):
                        self.hiscores.add( self.stats.score, self.initials())
                    self.show_highscores()
