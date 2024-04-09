""" text.text - letters, texts and scaling and coloring of fonts """
import pygame

from sliceitoff.display import Scaling, CGA_COLORS
from .fonts import Fonts
from .explode import ExplodingSprite

scaled_fonts = {}

def get_letter_surface(font_key, ch):
    """ Get letter surface at given properties hopefully from cache
        
        args:
            font_key: 	(font name, width to scale, color)
            ch:		0-255 character on cp473
            color:	0-15 as in CGA palette
    """
    font, w, color = font_key
    if font not in Fonts.fonts:
        return None
    if font_key not in scaled_fonts:
        scaled_fonts[font_key]=[None for _ in range(256)]
    if scaled_fonts[font_key][ch] is None:
        scaled_fonts[font_key][ch] = pygame.transform.scale_by(
                Fonts.fonts[font].get(ch),
                w/8 * Scaling.factor)
        scaled_fonts[font_key][ch].fill(
                CGA_COLORS[color],
                special_flags = pygame.BLEND_RGBA_MULT)
    return scaled_fonts[font_key][ch]


class LetterSprite(ExplodingSprite):
    """ Make sprite out of letter surface at given position """
    def __init__(self, font_key, ch, pos):
        super().__init__()
        self.dead = True
        self.image = get_letter_surface(font_key, ch)
        self.rect = self.image.get_rect().move(pos)

class TextPage(pygame.sprite.Group):
    """ Creates sprite group out of given text and parameters
    
        args:
        
        text	Just text. \xe0 - \xef  to cahnge color on cga palette
        pos	Position of right top corner in internal cooordinates
        size	Single character size (w,h)
        grid	Space for a character (w,h)
        font	Font loaded in Fonts.fonts dict
    """
    # pylint: disable = too-many-arguments	# all argumets necessaary

    def __init__(
            self,
            text,
            pos = (0,0),
            size = (8_000,16_000),
            grid = None,
            font = 'lcd'):
        super().__init__()
        if grid is None:
            grid = size
        color = 0xf
        col, row = 0, 0
        for ch_txt in text:
            if ch_txt == '\n':
                row += 1
                col = 0
                continue
            if ch_txt == '\t':
                col = (col + 4) % 4
                continue
            ch = ord(ch_txt)
            if ch in range(0xe0,0xf0):
                color = ch - 0xe0
                continue
            font_key = (font, size[0], color)
            sprite_pos = Scaling.scale_to_display(
                    (pos[0]+col*grid[0], pos[1]+row*grid[1]) )
            self.add(LetterSprite(font_key, ch, sprite_pos))
            col += 1
