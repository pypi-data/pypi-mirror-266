""" mainmenu.mainmenu - Let's user choose """
from enum import IntEnum
import pygame

from sliceitoff.screens import mainmenu_screen
from sliceitoff.display import Scaling

from sliceitoff.game.explodeout import ExplodeOutGroup

MOUSE_TRESHOLD = 100

class MenuItems(IntEnum):
    """ Items in the menu. Should match mainmenu_screen """
    NEWGAME = 0
    HISCORES = 1
    INSTRUCT = 2
    QUIT = 3

class Mainmenu(ExplodeOutGroup):
    """ sprite group with imputs to make selection """
    def __init__(self):
        super().__init__()
        self.add(mainmenu_screen(0))
        self.selection = 0
        self.mousey = 0

    def update(self, dt = 0, **kwargs):
        """ Does it all. Reads keyboard and updates screen """
        if not super().update(dt = dt, **kwargs) or self.explode:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.selection = MenuItems.QUIT
                self.do_fadeout()
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button <= 3:
                self.do_fadeout()
                break
            if event.type == pygame.KEYDOWN:
                if self.process_key(event.key):
                    break
            elif event.type == pygame.MOUSEMOTION:
                self.process_mouse_motion()
        self.empty()
        self.add(mainmenu_screen(self.selection))

    def process_mouse_motion(self):
        """ Mouse movement up or down moves menu selection """
        self.mousey += pygame.mouse.get_rel()[1]
        pygame.mouse.set_pos(Scaling.center)
        if abs(self.mousey) > MOUSE_TRESHOLD:
            self.selection += 1 if self.mousey > 0 else -1
            self.selection %= len(MenuItems)
            self.mousey = 0

    def process_key(self, key):
        """ Processes known key presses """
        match key:
            case pygame.K_KP_ENTER | pygame.K_RETURN | pygame.K_RIGHT:
                self.do_fadeout()
                return True
            case pygame.K_ESCAPE | pygame.K_q | pygame.K_LEFT:
                self.selection = MenuItems.QUIT
                self.do_fadeout()
                return True
            case pygame.K_UP:
                self.selection -= 1
                self.selection %= len(MenuItems)
            case pygame.K_DOWN:
                self.selection += 1
                self.selection %= len(MenuItems)
        return False
