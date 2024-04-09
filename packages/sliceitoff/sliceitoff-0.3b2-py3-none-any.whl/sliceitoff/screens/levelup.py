""" screen.levelup - Screen to show after succesfully completing level """
from sliceitoff.text import TextPage

def levelup_screen(stats = None):
    """ levelup_screen - screen full of stats how bonus is calculated """
    (
            total_bonus,
            level_bonus,
            life_bonus,
            time_bonus,
            area_bonus,
            herd_bonus) = stats.calc_bonus()
    text = (
            "   LEVEL UP BONUS!\n"
            "   ===============\n"
            "\n"
            f"Level{stats.level:3d}\xee\x12\xef{level_bonus:9d}pts\n"
            f"Lives{stats.lives:3d}\xec\x03\xef{life_bonus:9d}pts\n"
            f"Time{int(stats.bonus/1000):4d}\xed\x0e\xef{time_bonus:9d}pts\n"
            f"Area{int(stats.percent):4d}\xe9\xfe\xef{area_bonus:9d}pts\n"
            f"Herd{stats.enemies-stats.field_count:4d}"
            f"\xea\x0f\xef{herd_bonus:9d}pts\n"
            f"\n"
            f"Bonus{total_bonus:13d}pts\n")
    return TextPage(
            text,
            font = 'lcd',
            size = (12_000, 24_000),
            grid = (14_000, 20_000),
            pos = (12_000, 6_000) )
