""" screens.level - Screen to be shown when level begins. """
from sliceitoff.text import TextPage

def level_screen(level):
    """ level_screen - displays level number """
    return TextPage(
            f"Level {level}!",
            font = '8x8',
            size = (24_000, 24_000),
            pos = (48_000, 108_000) )
