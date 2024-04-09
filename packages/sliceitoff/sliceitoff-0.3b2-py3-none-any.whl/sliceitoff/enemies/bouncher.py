""" enemies.bouncher - Enemy type that bouches around """
from random import randrange, choice

from sliceitoff.text import get_letter_surface
from .enemy import Enemy

BOUNCHER_SPAWN_AREA = (0, 0, 300_000, 80_000)
BOUNCHER_MOVEMENT = (200, 20)
BOUNCHER_SIZE = 12_000
BOUNCHER_SYMBOLS = (0x1,0x2)
GRAVITY = 4

class EnemyBouncher(Enemy):
    """ Type of enemy that is affected by gravity """
    def __init__(self):
        super().__init__()
        self.position = (
                randrange(BOUNCHER_SPAWN_AREA[0], BOUNCHER_SPAWN_AREA[2]),
                randrange(BOUNCHER_SPAWN_AREA[1], BOUNCHER_SPAWN_AREA[3]))
        self.movement = (
                randrange(0, BOUNCHER_MOVEMENT[0]*2) - BOUNCHER_MOVEMENT[0],
                randrange(0, BOUNCHER_MOVEMENT[1]*2) - BOUNCHER_MOVEMENT[1])
        font_key = ('8x8', BOUNCHER_SIZE, 0)
        surface = get_letter_surface(font_key, choice(BOUNCHER_SYMBOLS))
        self.image = surface.subsurface(
                (0, 0, surface.get_rect().w, surface.get_rect().w))
        self.rect = None
        self.update()

    def update(self, dt = 0, wall_hit = None, **kwargs):
        """ wall hit from super(). added gravity """
        super().update(dt = dt, wall_hit = wall_hit, **kwargs)
        if dt:
            self.movement = (
                    self.movement[0],
                    (self.movement[1] + GRAVITY)*0.999)
