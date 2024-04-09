""" field.field - The playing area or slices, lazer of explosions of it """
import os
from random import randrange, choice

import pygame

from sliceitoff.display import Scaling, CGA_COLORS
from sliceitoff.text import LetterSprite

DEBUG = os.getenv("DEBUG")

class FieldSprite(pygame.sprite.Sprite):
    """ Playing area consist of these sprites """
    def __init__(self, area: tuple):
        super().__init__()
        self.color = (0,255,0,255)
        self.dead = False
        self.area = area
        self.rect = Scaling.area_to_rect(self.area)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(self.color)

class SliceSprite(FieldSprite):
    """ Flashing rectangle like lazer """
    def __init__(self, area: tuple ):
        super().__init__(area)
        self.color = (255,255,255,255)
        self.image.fill(self.color)
        self.timeout = 300
        self.dead = True

    def update(self, dt = 0, **kwargs):
        """ Just pick a randon color every update from cga palette """
        # pylint: disable = unused-argument
        # explosion arg is given, but no use in SliceSprite
        if dt:
            self.timeout -= dt
            self.color = choice(CGA_COLORS)
            if self.timeout <= 0:
                self.kill()
            else:
                self.image.fill(self.color)


class Field(pygame.sprite.LayeredUpdates):
    """ group that contains all pieces of field """
    initial_area = (320_000, 220_000)

    def __init__(self, stats = None):
        super().__init__()
        self.add(FieldSprite( (0, 0, *__class__.initial_area) ))
        self.area_full = __class__.initial_area[0] * __class__.initial_area[1]
        self.stats = stats

    def calculate_current_area(self):
        """ calculates sum of areas of all fields """
        return sum( s.area[2]*s.area[3] for s in self.active_sprites() )

    def update(self, **kwargs):
        """ just force explosion on """
        super().update(explode = True, **kwargs)

    def update_stats(self):
        """ calculates remaining area and remaining percentage """
        self.stats.percent = 100 * self.calculate_current_area() / self.area_full
        if DEBUG:
            print(f"FIELD: {self.stats.percent}")

    def slice(
            self,
            pos: tuple,
            direction: bool,
            thickness: int) -> pygame.Rect:
        """ Slice one area into two areas """

        # Slicing hits the area?
        for overlap in self.get_sprites_at(Scaling.scale_to_display(pos)):
            if not overlap.dead:
                break
        else:
            return None

        # Save the area information and remove the sprite
        overlap_area = overlap.area
        overlap.remove(self)

        slicer = self.vertical_slicer if direction else self.horizontal_slicer
        # create new areas if there is any space
        area = slicer(pos, overlap_area, thickness)
        self.explode(area)
        zap_spite = SliceSprite(area)
        self.add(zap_spite)
        return zap_spite

    def vertical_slicer(self, pos, area, thickness):
        """ slices area in 3 parts vertically. returns lazer area """
        ax, ay, aw, ah = area
        t2 = pos[0] - thickness
        t3 = pos[0] + thickness
        t4 = ax + aw
        if t2 > ax:
            self.add(FieldSprite( (ax, ay, t2-ax, ah) ))
        if t4 > t3:
            self.add(FieldSprite( (t3, ay, t4-t3, ah) ))
        return (t2, ay, t3-t2, ah)

    def horizontal_slicer(self, pos, area, thickness):
        """ slices area in 3 parts horizontally. returns lazer area """
        ax, ay, aw, ah = area
        t2 = pos[1] - thickness
        t3 = pos[1] + thickness
        t4 = ay + ah
        if t2 > ay:
            self.add(FieldSprite( (ax, ay, aw, t2-ay) ))
        if t4 > t3:
            self.add(FieldSprite( (ax, t3, aw, t4-t3) ))
        return (ax, t2, aw, t3-t2)


    def active_sprites(self):
        """ Returns all sprites that are not dead """
        return [s for s in self.sprites() if not s.dead]

    def active_rects(self):
        """ Returns active areas as rects """
        return [s.rect for s in self.sprites() if not s.dead]

    def explode(self, area):
        """ Make area full of explogind letters """
        sx, sy, w, h = area
        for x in range(int(sx),int(sx+w),8_000):
            for y in range(int(sy),int(sy+h),8_000):
                self.add(LetterSprite(
                        ('8x8', 8_000, 0xf),
                        randrange(0,0x100),
                        Scaling.scale_to_display((x,y)) ))

    def kill_if_not_colliding(self, sprites):
        """ If there is empty fields that are not yet dead kill them """
        for field in self.active_sprites():
            for enemy in sprites:
                if enemy.rect.colliderect(field.rect):
                    break
            else:
                self.explode(field.area)
                field.remove(self)
        self.stats.field_count = len(self.active_sprites())
