from arcade import View, color
from enum import Enum

class AnvilState(Enum):
    GOOD = 1
    OKAY = 2
    BAD = 3
    BROKEN = 4

class AnvilGame(View):
    click_count = 0
    
    def __init__(self):
        """ Initialisation du mini jeu """
        super().__init__()

        self.background_color = color.BLACK_BEAN

        pass
    
    def setup(self):
        """ Configuration du mini jeu """
        pass
    def on_draw(self):
        """ Dessiner le mini jeu """
    def on_update(self, delta_time):
        """ Mettre à jour le mini jeu """
        pass
