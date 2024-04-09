""" screens.hiscores - Defines how to display hiscore text on the screen """
from sliceitoff.text import TextPage

def hiscores_screen(score_text):
    """ hiscores_screen - only ajustments to hiscore text """
    return TextPage(
            score_text,
            font = 'lcd',
            size = (12_000, 24_000),
            grid = (12_000, 20_000),
            pos = (12_000, 0_000) )
