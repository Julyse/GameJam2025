import arcade
from game_controller import SCREEN_WIDTH, SCREEN_HEIGHT, GameController
from ui.menu import MenuView


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Le faiseur d'épées")
        self.show_menu()
    def show_menu(self):
        self.show_view(MenuView())

def main():
    arcade.load_font("ressources/fonts/Righteous.ttf")
    GameWindow()
    arcade.run()
 
if __name__ == "__main__":
    main()
