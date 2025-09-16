import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout
import arcade.gui.widgets.text
from mini_games.valve import ValveGame  # ton mini-jeu

# Constantes
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 325
SCREEN_TITLE = "Forgeron du donjon"


class QuitButton(arcade.gui.widgets.buttons.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()   


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.status = ["menu","cinematic","game"]
        self.current_minigame = None

        # --- Créer layout vertical pour les boutons
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout(space_between=20)

        # Titre du jeu
        title_label = arcade.gui.UILabel(
            text="Anvil NPC",
            width=450,
            height=40,
            font_size=24,
            font_name="Kenney Future",
            text_color=arcade.color.WHITE
        )
        self.v_box.add(title_label)

        # Boutons
        start_button = arcade.gui.UIFlatButton(text="Ouvrir l'Échoppe", width=200)
        settings_button = arcade.gui.UIFlatButton(text="Options", width=200)
        quit_button = QuitButton(text="Fermer l'Échoppe", width=200)

        self.v_box.add(start_button)
        self.v_box.add(settings_button)
        self.v_box.add(quit_button)

        # Méthode 2 : assigner fonction pour start
        start_button.on_click = self.on_click_start

        # Méthode 3 : décorateur pour settings
        @settings_button.event("on_click")
        def on_click_settings(event):
            print("Options ouvertes :", event)

        # Centrer la v_box
        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(ui_anchor_layout)

    def on_click_start(self, event):
        print("Mini-jeu lancé !")
        self.status = "game"
        

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_update(self, delta_time):
        pass


def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()