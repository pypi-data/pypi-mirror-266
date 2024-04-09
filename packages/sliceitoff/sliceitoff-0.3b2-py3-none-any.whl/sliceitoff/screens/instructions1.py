""" screens.instructions1 - First page of instructions"""
from sliceitoff.text import TextPage

def instructions1_screen():
    """ Instructions about the goal """
    return TextPage(
            "\n       Slice It Off!\n\n"
            "\n"
            " What to do?\n"
            "\n"
            " * Move the slicing tool\n"
            "   in the playarea.\n"
            "\n"
            " * Slice when there is\n"
            "   no-one on the way.\n"
            "\n"
            " * Empty slices fall off.\n"
            "\n"
            " * If playarea is sliced\n"
            "   below 20% you level up.\n"
            "\n"
            " * Slicing costs points.\n",
            font = '8x8',
            size = (12_000, 12_000),
            pos = (0, 0) )
