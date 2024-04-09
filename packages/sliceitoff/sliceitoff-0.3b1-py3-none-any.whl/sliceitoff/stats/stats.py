""" stats.stats """
class Stats:
    """ score, level, enemy count etc stats during the game """
    def __init__(self):
        self.score = 0
        self.level = 1
        self.bonus = 20_000
        self.lives = 3
        self.enemies = 3
        self.percent = 100
        self.field_count = 1

    def level_up(self):
        """ task on beginning of level. new bonus, enemy count... """        
        self.score += self.calc_bonus()[0]
        self.bonus = 20_000
        self.percent = 100
        self.field_count = 1
        self.level += 1
        self.enemies = 3 + (self.level - 1) * 2

    def lose_life(self):
        """ lives left after losing life """
        self.lives -= 1
        return not self.lives

    def add_score(self, score_to_add):
        """ adding score never goes negative """
        self.score += score_to_add
        self.score = max(0, self.score)

    def calc_bonus(self):
        """ calculates bonus and returns components """
        level = self.level * 3_000
        life = self.lives * 1_000
        time = self.level * self.bonus
        area = self.level * int(max(20-self.percent,0) * 1_000)
        herd = (self.enemies - self.field_count) * 1_000
        total = level + area + time + life + herd
        return total, level, life, time, area, herd

    def update_bonus(self, dt):
        """ bonus countdown. never goes negative """
        self.bonus = max(0, self.bonus - dt)
