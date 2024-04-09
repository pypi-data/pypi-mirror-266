""" enemies.ball - Enemy type that goes straight line hitting walls """
from random import randrange, choice

from sliceitoff.text import get_letter_surface
from .enemy import Enemy

BALL_SPAWN_AREA = (0, 0, 300_000, 200_000)
BALL_MOVEMENT = (100, 100)
BALL_SYMBOLS = (0x1,0x2)
BALL_SIZE = 8_000

class EnemyBall(Enemy):
    """ Basic type of enemy. """
    def __init__(self):
        super().__init__()
        self.position = (
                randrange(BALL_SPAWN_AREA[0], BALL_SPAWN_AREA[2]),
                randrange(BALL_SPAWN_AREA[1], BALL_SPAWN_AREA[3]))
        self.movement = (
                randrange(0, BALL_MOVEMENT[0]*2) - BALL_MOVEMENT[0],
                randrange(0, BALL_MOVEMENT[1]*2) - BALL_MOVEMENT[1])
        font_key = ('8x8', BALL_SIZE, 0)
        surface = get_letter_surface(font_key, choice(BALL_SYMBOLS))
        self.image = surface.subsurface(
                (0, 0, surface.get_rect().w, surface.get_rect().w))
        self.update()
        self.rect = None
