""" Reads user input and does actions when game play is on. """
import pygame

class Gameplay:
    """ Logic of the playfield """
    def __init__(
            self,
            player = None,
            field = None,
            enemies = None,
            stats = None,
            life = None):
        self.player = player
        self.field = field
        self.enemies = enemies
        self.stats = stats
        self.life = life

    def fire(self):
        """ Lazer is fired. Actions to be taken. """
        zap_sprite = self.field.slice(
                self.player.position,
                self.player.direction,
                4_000)
        if not zap_sprite:
            return False
        self.stats.add_score(-500)
        if pygame.sprite.spritecollideany(zap_sprite, self.enemies):
            self.life.lose_life()
            if self.stats.lose_life():
                return True
        self.field.kill_if_not_colliding(self.enemies.sprites())
        self.field.update_stats()
        return self.stats.percent < 20

    def quit(self):
        """ Lose lives so no leveling up """
        self.stats.lives = 0
        return True

    def step(self):
        """ Processes events for the step (frame) """
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEMOTION:
                    self.player.update(pos = pygame.mouse.get_pos())
                case pygame.MOUSEBUTTONDOWN:
                    self.player.update(pos = pygame.mouse.get_pos())
                    if event.button == 1:
                        if self.fire():
                            return True
                    if event.button == 3:
                        self.player.update(direction = True)
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE | pygame.K_q:
                            return self.quit()
                        case pygame.K_SPACE:
                            if self.fire():
                                return True
                case pygame.QUIT:
                    return self.quit()
        return False
