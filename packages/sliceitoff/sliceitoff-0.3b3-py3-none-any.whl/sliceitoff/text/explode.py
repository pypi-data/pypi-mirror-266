""" text.explode - Exploding effect movements and updates for the sprite """
from random import randrange

import pygame

from sliceitoff.display import Scaling

class ExplodingSprite(pygame.sprite.Sprite):
    """ Just adds exloding movement to the sprite """
    def __init__(self):
        super().__init__()
        self.rect = None
        self.direction = (
                Scaling.factor * (1_000 - randrange(2_000)),
                Scaling.factor * (1_000 - randrange(2_000)))

    def update(self, dt = 0, explode = 0):
        """ Exploding movement """
        if explode and dt:
            self.rect = pygame.Rect(
                    self.rect.x + self.direction[0] * dt,
                    self.rect.y + self.direction[1] * dt,
                    self.rect.w,
                    self.rect.h)
            self.direction = (
                    self.direction[0] * 0.95,
                    self.direction[1] * 0.95 + 0.3)
