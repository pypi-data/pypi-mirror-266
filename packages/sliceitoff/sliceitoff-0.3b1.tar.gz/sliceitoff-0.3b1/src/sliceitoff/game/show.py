""" Sprite group that show sprites and skips if key is pressed """
from .anykey import anykey
from .explodeout import ExplodeOutGroup

class Show(ExplodeOutGroup):
    """ To show some sprites and quit on any key """
    def __init__(self, sprites = None, active = True):
        super().__init__(active = active)
        self.add(sprites)
        self.timeout = 15_000

    def update(self, dt = 0, **kwargs):
        """ First timeout then fadeout and then inactivity """
        if not super().update(dt = dt, **kwargs):
            return
        if anykey():
            self.do_fadeout()
        if self.timeout <= 0:
            self.do_fadeout()
        self.timeout -= dt

    def sprites(self):
        """ Return sprites only when active """
        return super().sprites() if self.active else []
