""" screens.mainmenu - Screen for mainmenu"""
from random import randrange
from sliceitoff.text import TextPage

def mainmenu_screen(selection):
    """ Screen where current selection is flashing """
    active = randrange(0xe9,0xf0)
    inactive = 0xe7
    text =  (
            f" Slice it off!!\n"
            f"\n\n"
            f"{chr(active if selection == 0 else inactive)}"
            f"New Game\n\n"
            f"{chr(active if selection == 1 else inactive)}"
            f"High Scores\n\n"
            f"{chr(active if selection == 2 else inactive)}"
            f"Instructions\n\n"
            f"{chr(active if selection == 3 else inactive)}"
            f"Quit, Why?")
    return TextPage(
            text,
            font = '8x8',
            size = (16_000, 16_000),
            pos = (24_000, 32_000) )
