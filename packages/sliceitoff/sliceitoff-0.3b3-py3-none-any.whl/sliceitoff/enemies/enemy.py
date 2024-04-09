""" enemy.enemy - Enemy super class. Wall hitting and other commons """
import pygame

from sliceitoff.display import Scaling

class Enemy(pygame.sprite.Sprite):
    """ Enemy super class. Just common movements. """
    def __init__(self):
        super().__init__()
        self.position = (0, 0)
        self.movement = (0, 0)
        self.rect = None

    def update(self, dt = 0, wall_hit = None):
        """ hit walls, update position and rect """
        if wall_hit:
            if self.rect.x < wall_hit.x:
                self.movement = (abs(self.movement[0]), self.movement[1])
            if self.rect.y < wall_hit.y:
                self.movement = (self.movement[0], abs(self.movement[1]))
            if self.rect.x + self.rect.w >= wall_hit.x + wall_hit.w:
                self.movement = (-abs(self.movement[0]), self.movement[1])
            if self.rect.y + self.rect.h >= wall_hit.y + wall_hit.h:
                self.movement = (self.movement[0], -abs(self.movement[1]))
            return
        if dt:
            self.position = (
                    self.position[0] + self.movement[0] * dt,
                    self.position[1] + self.movement[1] * dt)
        self.rect = pygame.Rect(
                Scaling.scale_to_display(self.position),
                self.image.get_size())
