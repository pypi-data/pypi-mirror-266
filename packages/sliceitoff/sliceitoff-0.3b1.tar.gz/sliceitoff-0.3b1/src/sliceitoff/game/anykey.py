""" game.anykey - Event waiting. Used for skipping screens. """
import pygame

def anykey():
    """ Anything but mouse movement gives True """
    for event in pygame.event.get():
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.QUIT):
            return True
    return False
