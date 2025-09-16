import arcade
from arcade.sections import SectionManager
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
        self.section_manager = SectionManager(self)
        for p in self.panels:
            self.section_manager.add_section(p)

    # -- Dessin
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.section_manager.enable()

    def on_draw(self):
        self.clear()
        # Le SectionManager intercepte et dessine les sections

    def on_update(self, delta_time: float):
        # Le SectionManager gère les updates des sections
        pass


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
