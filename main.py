import arcade

#import mini jeu
from mini_games.mystery_box import MysteryBoxGame

#Constantes
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Forgeron du donjon"

class GameState:
    DIALOGUE = "dialogue"
    MENU = "menu"
    MINIGAME = "minigame"


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.current_state = GameState.MENU
        
        self.minigames = [MysteryBoxGame,] #mini jeu disponible 
        
        self.current_minigame = None # mini jeu en cours
        
    def setup(self):
        # Démarrer directement le mini-jeu MysteryBox
        self.current_minigame = MysteryBoxGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.show_view(self.current_minigame)

    def on_draw(self):
        pass  

    def on_update(self, delta_time):
        pass

def main():
    """ Main method """
    game= Game()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()