import arcade
from game_controller import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.menu import MenuView


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Forgeron du donjon")
        self.show_menu()
    def show_menu(self):
        self.show_view(MenuView())

        if key == arcade.key.U:  # Use sword
            self.sword_panel.game.remove_sword(index=0)
def main():
    GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()