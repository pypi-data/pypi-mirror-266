""" display.scaling - for converting internal resolution to actual screen """

import pygame

from .static import INTERNAL_WIDTH, INTERNAL_HEIGHT

class Scaling():
    """ Holds data and methods needed for coordinate conversion """
    factor = 0.02
    left = 0
    top = 0
    resolution = (0,0)
    center = (0,0)
    borders = (pygame.Rect(0,0,0,0), pygame.Rect(0,0,0,0))
    active = pygame.Rect(0,0,0,0)

    @staticmethod
    def area_to_rect(area: tuple) -> pygame.Rect:
        """ converts area coordinates to pygame.Rect"""
        return pygame.Rect(
                area[0] * __class__.factor + __class__.left,
                area[1] * __class__.factor + __class__.top,
                area[2] * __class__.factor,
                area[3] * __class__.factor)

    @staticmethod
    def scale_to_display(coords: tuple ) -> tuple:
        """ Converts internal coordinates to display coodinates """
        return (
                coords[0] * __class__.factor + __class__.left,
                coords[1] * __class__.factor + __class__.top)

    @staticmethod
    def scale_to_internal(coords: tuple ) -> tuple:
        """ Converts display coordinates to internal coodinates """
        x = coords[0] - __class__.left
        x = max(x, 0) // __class__.factor
        x = min(x, INTERNAL_WIDTH - 1)
        y = coords[1] - __class__.top
        y = max(y, 0) // __class__.factor
        y = min(y, INTERNAL_HEIGHT - 1)
        return (x, y)

    @staticmethod
    def update_scaling(size: tuple) -> None:
        """ Calculates new scaling and positionin according given
        actual resolution """
        __class__.resolution = size
        __class__.center = (size[0]/2,size[1]/2)
        if size[0] / size[1] <= INTERNAL_WIDTH / INTERNAL_HEIGHT:
            __class__.factor = size[0] / INTERNAL_WIDTH
            __class__.left = 0
            __class__.top = int (
                    (size[1] - INTERNAL_HEIGHT * __class__.factor) // 2)
            __class__.borders = (
                    pygame.Rect(
                            0,
                            0,
                            size[0],
                            __class__.top),
                    pygame.Rect(
                            0,
                            size[1] - __class__.top,
                            size[0],
                            __class__.top),
                    )
        else:
            __class__.factor = size[1] / INTERNAL_HEIGHT
            __class__.left = int(
                    (size[0] - INTERNAL_WIDTH * __class__.factor) // 2)
            __class__.top = 0
            __class__.borders = (
                    pygame.Rect(
                            0,
                            0,
                            __class__.left,
                            size[1]),
                    pygame.Rect(
                            size[0] - __class__.left,
                            0,
                            __class__.left,
                            size[1]),
                    )
        __class__.active = pygame.Rect(
                __class__.left,
                __class__.top,
                INTERNAL_WIDTH * __class__.factor,
                INTERNAL_HEIGHT * __class__.factor)
