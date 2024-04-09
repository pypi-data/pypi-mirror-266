""" screen.gameover - screen to be displayer game over situation """
from sliceitoff.text import TextPage

def gameover_screen():
    """ gameover_screen - overlay top of ended gameplay """
    return TextPage(
            "Game Over!",
            font = '8x8',
            size = (24_000, 24_000),
            pos = (48_000, 108_000) )
