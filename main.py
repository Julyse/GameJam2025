import arcade

#import mini jeu
from mini_games.valve import ValveGame 

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
        
        self.minigames = [ValveGame,] #mini jeu disponible 
        
        self.current_minigame = None # mini jeu en cours
        
    def setup(self):
        pass 

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