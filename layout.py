import arcade
from panels.base_panel import BasePanel

# -------------------------------
# 1. Données et constantes
# -------------------------------
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
BOTTOM_HEIGHT = 260
NUM_SMALL     = 3


# -------------------------------
# 2. Un panneau générique
# -------------------------------


# -------------------------------
# 3. Fenêtre principale
# -------------------------------
class LayoutView(arcade.View):
    def __init__(self, panels: list[BasePanel]):
        super().__init__()
        self.panels = panels

    # -- Dessin
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        for p in self.panels:
            p.draw()

    def on_update(self, delta_time: float):
        for p in self.panels:
            p.update(delta_time)


# -------------------------------
# 4. Lancement
# -------------------------------
def main():
    # Exemple d'utilisation autonome
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Layout Modulaire")
    view = LayoutView([])
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
