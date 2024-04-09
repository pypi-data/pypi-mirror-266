""" screens.instructions2 - Page about scoring """
from sliceitoff.text import TextPage

def instructions2_screen():
    """ Instructions about scoring """
    return TextPage(
            "\n       Slice It Off!\n\n"
            "\n"
            " Getting scores?\n"
            "\n"
            " \xee\x12\xef Level up gives bonus\n"
            "   and also multiplies.\n"
            "\n"
            " \xec\x03\xef Extra lives gives bonus\n"
            "\n"
            " \xed\x0e\xef Getting level done\n"
            "   before bonus timer.\n"
            "\n"
            " \xe9\xfe\xef Area smaller than 20%\n"
            "   gives bonuses.\n"
            "\n"
            " \xea\x0f\xef Keeping herd together\n"
            "   in same area.\n",
            font = '8x8',
            size = (12_000, 12_000),
            pos = (0, 0) )
