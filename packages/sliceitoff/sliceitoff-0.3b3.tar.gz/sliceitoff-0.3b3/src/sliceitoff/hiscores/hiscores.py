""" hiscores.hiscores - high socres: loading, saving, converting to string """
import os
from pathlib import Path

from .static import INITIAL_HIGHSCORES, MAX_HIGHSCORES

class HiScores:
    """ Keeps track of high scores """
    def __init__(self):
        """ On creation load high scores from config file """
        self.table=[]
        if os.name == 'nt':
            self.config_filename = os.path.join(Path.home(), "sliceitoff.cfg")
        else:
            self.config_filename = os.path.join(
                    Path.home(),
                    ".config",
                    "sliceitoffrc")
        if not os.path.isfile(self.config_filename):
            self.table=INITIAL_HIGHSCORES[:]
            return
        with open(self.config_filename, "r", encoding="utf-8") as config_file:
            for line in config_file:
                option, *value = line.split('=')
                if option == 'hiscore' and value:
                    score, name = value[0].split('!')
                    self.add(int(score.strip()),name.strip())
        if len(self.table)<MAX_HIGHSCORES:
            self.table+=[(0,"") for _ in range(MAX_HIGHSCORES-len(self.table))]

    def add(self, score, initials):
        """ Add new high score and reranks top """
        self.table.append( (score, initials) )
        self.table.sort(reverse=True)
        self.table = self.table[:MAX_HIGHSCORES]

    def high_enough(self, score):
        """ Score is enough to make high scores """
        return self.table[-1][0] < score

    def __del__(self):
        """ On object deletion save current high scores to config file """
        oldlines=[]
        if os.path.isfile(self.config_filename):
            with (open(self.config_filename, "r", encoding="utf-8")
                    as config_file):
                for line in config_file:
                    option, *_ = line.split('=')
                    if option != 'hiscore':
                        oldlines.append(line)
        with open(self.config_filename, 'w', encoding="utf-8") as config_file:
            config_file.writelines(oldlines)
            for score, name in self.table:
                config_file.write(f"hiscore={score}!{name}\n")

    def __str__(self):
        text = (
                "      "
                "\xeeH\xecI\xedG\xe9H "
                "\xeaS\xedC\xeeO\xebR\xe9E\xecS\xeb!\xed!\n\n")
        half = len(self.table) // 2
        for i in range(half):
            text += (
                    f"\xed{self.table[i][1]:<3s} "
                    f"\xef{self.table[i][0]:07}  "
                    f"\xed{self.table[i+half][1]:<3s} "
                    f"\xef{self.table[i+half][0]:07}\n")
        return text
