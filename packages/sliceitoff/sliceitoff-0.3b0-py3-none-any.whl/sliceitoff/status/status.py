""" status.status - The statusline bottom of screen showinf all stats """
import pygame

from text import TextPage

class Status(pygame.sprite.Group):
    """ Statusline bottom of screen """
    def __init__(self, stats = None):
        super().__init__()
        self.stats = stats
        self.old_srt = None

    def update(self, **kwargs):
        """ Rebuilds statusline if needed """
        super().update(**kwargs)
        percent = int(self.stats.percent)
        if percent == 100:
            percent = 99
        score_str = (
                f"\xee\x12\xef{self.stats.level:<2d}"
                f"\xec\x03\xef{self.stats.lives:<2d}"
                f"\xed\x0e\xef{self.stats.bonus // 1000:<3d}"
                f"\xe9\xfe\xef{percent:<3d}"
                f"\xea\x0f\xef{self.stats.enemies-self.stats.field_count:<3d}"
                f"{self.stats.score:08d}")
        if self.old_srt != score_str:
            self.empty()
            self.add( TextPage(
                    score_str,
                    pos = (2_000, 220_000),
                    size = (12_000, 0),
                    font = 'lcd') )
