""" enemies.enemies - group for enemies for the leve"""
from random import randrange
import pygame

from .ball import EnemyBall
from .bouncher import EnemyBouncher

class Enemies(pygame.sprite.Group):
    """ Init with count. Randomizing enemy types. Some are worth more. """
    def __init__(self, count = 0):
        super().__init__()
        while count:
            match randrange(0,4):
                case 0|1|2:
                    if count >= 1:
                        self.add(EnemyBall())
                        count -= 1
                case 3:
                    if count >= 2:
                        self.add(EnemyBouncher())
                        count -= 2

    def update(self, field_rects = None, **kwargs):
        """ Do actions on enemies that are only partly on the fields """
        super().update(**kwargs)
        for enemy in self.sprites():
            for field_rect in field_rects:
                # if enemy is completely inside any field do next enemy
                if field_rect.contains(enemy):
                    break
            else:
                # now find field that enemy is partly on
                for field_rect in field_rects:
                    if field_rect.colliderect(enemy):
                        enemy.update(wall_hit = field_rect)
