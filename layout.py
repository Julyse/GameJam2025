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

        # rien de spécial

    # -- Dessin
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        # rien de spécial

    def on_draw(self):
        self.clear()
        for p in self.panels:
            p.on_draw()

    def on_update(self, delta_time: float):
        # Le SectionManager gère les updates des sections
        for p in self.panels:
            p.on_update(delta_time)

    # -- Propager clavier
    def on_key_press(self, key, modifiers):
        for p in self.panels:
            if hasattr(p, "on_key_press"):
                p.on_key_press(key, modifiers)
