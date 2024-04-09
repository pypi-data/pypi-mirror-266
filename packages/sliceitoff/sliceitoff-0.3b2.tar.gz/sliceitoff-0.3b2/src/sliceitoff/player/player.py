""" player.player - Player sprite group and actions """
import os
import pygame

from sliceitoff.display import Scaling

from .static import SLICER

DEBUG = os.getenv("DEBUG")

def dataclass_to_surface(dc):
    """ Converts dataclass to surface """
    image = pygame.Surface(dc.DIMENSIONS, pygame.SRCALPHA)
    for x in range(dc.DIMENSIONS[0]):
        for y in range(dc.DIMENSIONS[1]):
            image.set_at((x,y), dc.COLORS[dc.IMAGE[y*dc.DIMENSIONS[0]+x]])
    return image

class PlayerSprite(pygame.sprite.Sprite):
    """ The slicing tool. There is 2 of these. Horizontal and vertical """
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

    def update(self, pos = None):
        """ Sets sprite center at given position """
        if pos:
            w, h = self.image.get_size()
            self.rect = self.image.get_rect().move(pos[0]-w//2,pos[1]-h//2)

class Player(pygame.sprite.Group):
    """ The slicer. Special sprite group that only list 1 sprite """
    def __init__(self):
        super().__init__()
        self.position = (0,0)
        self.direction = False
        self.lazer = False
        image = dataclass_to_surface(SLICER)
        image = pygame.transform.scale_by(image, 1_000 * Scaling.factor)
        self.add(PlayerSprite(image))
        image = pygame.transform.rotate(image, 90)
        self.add(PlayerSprite(image))

    def update(self, pos = None, direction = False):
        """ Updates the position and direction """
        if self.lazer:
            direction = False
            pos = None
        if direction:
            self.direction = not self.direction
        if pos:
            self.position = Scaling.scale_to_internal(pos)
            for sprite in super().sprites():
                sprite.update(pos = pos)

    def sprites(self):
        """ Only list sprite of current direction for draw """
        return [super().sprites()[self.direction]]
