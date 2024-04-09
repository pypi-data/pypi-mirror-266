""" text.fonts - .FNT file loading and storing """
import os
import pygame

DEBUG = os.getenv("DEBUG")

class Fonts:
    """ Fonts - static class to store loaded fonts """
    fonts = {}

    @staticmethod
    def load_fonts(base_path):
        """ loads fonts from list """
        filename_fontlist = os.path.join(base_path, "assets", "fonts.lst")
        with open(filename_fontlist, "r", encoding="utf-8") as fontlist_file:
            for line in fontlist_file:
                name, *path = line.strip().split()
                filename = os.path.join(base_path, *path)
                __class__.fonts[name] = Font(filename)
        return True


class Font:
    """ Font - font surfaces to be loaded from file """
    def __init__(self, filename, height = 16):
        if DEBUG:
            print(f"Loading font {filename = }")
        self.surfaces = []
        with open(filename, mode="rb") as fnt_file:
            for _ in range(256):
                surface = pygame.Surface((8,height), pygame.SRCALPHA)
                for line in range(16):
                    byte = fnt_file.read(1)[0]
                    if line >= height:
                        continue
                    for bit in range(8):
                        if byte & 0x80:
                            surface.set_at((bit,line),"white")
                        byte <<= 1
                self.surfaces.append(surface)

    def get(self, ch):
        """ Just get surface of the font size 8x16 max """
        return self.surfaces[ch%256]
