""" game.initials - Use will be asked for initials """
import pygame

from sliceitoff.screens import initials_screen

from .explodeout import ExplodeOutGroup

class Initials(ExplodeOutGroup):
    """ Sprite group that asks initials to self.name from user """
    def __init__(self):
        super().__init__()
        self.add(initials_screen(""))
        self.name = ""

    def update(self, dt = 0, **kwargs):
        """ Does it all. Reads keyboard and updates screen """
        if not super().update(dt = dt, **kwargs):
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.do_fadeout()
                break
            if event.type == pygame.KEYDOWN:
                if event.key in (
                        pygame.K_ESCAPE,
                        pygame.K_KP_ENTER,
                        pygame.K_RETURN):
                    self.do_fadeout()
                    break
                if event.key in (
                        pygame.K_RSHIFT,
                        pygame.K_LSHIFT,
                        pygame.K_RCTRL,
                        pygame.K_LCTRL,
                        pygame.K_RALT,
                        pygame.K_LALT,
                        pygame.K_RMETA,
                        pygame.K_LMETA,
                        pygame.K_LSUPER,
                        pygame.K_RSUPER,
                        pygame.K_SPACE):
                    continue
                if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    self.name = self.name [:-1]
                elif pygame.key.name(event.key):
                    self.name += pygame.key.name(event.key)[0].upper()
                    self.name = self.name[:3]
                self.empty()
                self.add(initials_screen(self.name))
