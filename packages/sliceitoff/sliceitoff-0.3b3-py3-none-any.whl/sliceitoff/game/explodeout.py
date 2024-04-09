""" game.explodeout - For showing explogind effect and waiting for a key """
import pygame

from .anykey import anykey

class ExplodeOutGroup(pygame.sprite.Group):
    """ Sprite group that just counts down feadeout/explosion or a key """
    def __init__(self, active = True):
        super().__init__()
        self.explode = False
        self.active = active
        self.fadeout = 1_000

    def update(self, dt = 0, **kwargs):
        """ Just does the explosion and marks group inactive """
        if not self.active:
            return False

        super().update(dt = dt, explode = self.explode, **kwargs)

        if self.explode:
            if self.fadeout <= 0:
                self.active = False
            else:
                if anykey():
                    self.fadeout = 0
                    self.active = False
                self.fadeout -= dt
            return True
        return True

    def do_fadeout(self):
        """ Just kicks off exploding phase """
        self.explode = True
