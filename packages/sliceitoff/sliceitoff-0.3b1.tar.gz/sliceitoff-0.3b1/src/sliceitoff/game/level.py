""" game.level - This is what runs invidual levels """
import pygame

from status import Status
from player import Player, Life
from field import Field
from enemies import Enemies
from screens import levelup_screen, gameover_screen, level_screen
from .gameplay import Gameplay
from .show import Show

class Level(pygame.sprite.Group):
    """ One level that can be played """
    # pylint: disable = too-many-instance-attributes
    def __init__(self, stats = None):
        super().__init__()
        self.stats = stats
        self.status = Status(stats = self.stats)
        self.field = Field(stats = self.stats)
        self.enemies = Enemies(count = self.stats.enemies)
        self.player = Player()
        self.life = Life()
        self.level_info = Show(level_screen(stats.level))
        self.ended = False
        self.active = True
        self.endscreen = None

        self.gameplay = Gameplay(
                player = self.player,
                field = self.field,
                enemies = self.enemies,
                stats = self.stats,
                life = self.life)

    def update(self, dt = 0):
        """ Updates groups, calls gameplay and adds sprites for drawing """
        self.empty()
        self.status.update(dt = dt)
        self.field.update(dt = dt)
        self.enemies.update(dt = dt, field_rects = self.field.active_rects())
        self.life.update(dt = dt)
        self.add(self.status, self.field, self.enemies)

        if self.level_info.active:
            self.level_info.update(dt = dt)
            self.add(self.level_info)

        elif self.ended:
            if self.endscreen.active:
                self.endscreen.update(dt = dt)
                self.add(self.endscreen)
            else:
                self.active = False
        else:
            self.add(self.player)
            self.stats.update_bonus(dt)
            if self.gameplay.step():
                self.ended = True
                if self.stats.lives:
                    self.endscreen = Show(levelup_screen(self.stats))
                else:
                    self.endscreen = Show(gameover_screen())
        self.add(self.life)
