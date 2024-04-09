""" screens.initials - screen where input initials when one makes
    to hiscores """
from sliceitoff.text import TextPage

def initials_screen(name):
    """ initials_screen - screen where name is updating as user imputs """
    return TextPage(
            f" New High Score!\n"
            f"\n"
            f"\n"
            f"Initials, please:\n"
            f"\n"
            f"\n"
            f"{name:^17s}",
            font = '8x8',
            size = (16_000, 16_000),
            pos = (24_000, 32_000) )
