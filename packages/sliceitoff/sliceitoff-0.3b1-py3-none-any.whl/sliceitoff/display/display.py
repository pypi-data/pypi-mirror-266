""" display.display - Routines to init and display graphics on screen """
import os
import pygame

from .scaling import Scaling
from .static import CGA_COLORS

DEBUG = os.getenv("DEBUG")

def gen_backdrop(color, color2):
    """ generates backdrop with 50% dithering """
    srfc = pygame.Surface((320, 240))
    for x in range(320):
        for y in range(240):
            srfc.set_at((x,y),color if (x+y)%2 else color2)
    return srfc

class Display():
    """display.Display - Handles graphics. Init, clear, draw, borders... """
    def __init__(self):
        pygame.display.init()
        mode_info = pygame.display.Info()
        self.screen = pygame.display.set_mode(
                (mode_info.current_w, mode_info.current_h),
                pygame.FULLSCREEN | pygame.SCALED,
                vsync = 1 )
        Scaling.update_scaling(self.screen.get_size())
        self.backdrop = pygame.transform.scale_by(
                gen_backdrop(CGA_COLORS[1], CGA_COLORS[8]),
                1_000 * Scaling.factor)
        if DEBUG:
            print(
                    "DISPLAY: \n"
                    f"  {Scaling.active = }\n"
                    f"  {Scaling.borders = }\n"
                    f"  {Scaling.factor = }\n")

    def __del__(self):
        pygame.display.quit()

    def update(self, groups = None):
        """ Updates the screen: clear, blit gropus and flip """
        self.screen.blit(self.backdrop, (Scaling.left,Scaling.top))
        for group in groups:
            group.draw(self.screen)
        self.screen.fill(0, rect=Scaling.borders[0])
        self.screen.fill(0, rect=Scaling.borders[1])
        pygame.display.flip()
