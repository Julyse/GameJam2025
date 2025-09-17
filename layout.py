import arcade
from panels.base_panel import BasePanel
from panels import BigPanel, SmallPanel1, SmallPanel2, SmallPanel3

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


# -------------------------------
# 4. Fabrique de panels par défaut
# -------------------------------
def build_default_panels() -> list[BasePanel]:
    panels: list[BasePanel] = []
    panels.append(BigPanel(x=0, y=BOTTOM_HEIGHT, width=SCREEN_WIDTH, height=SCREEN_HEIGHT - BOTTOM_HEIGHT))
    w1 = int(SCREEN_WIDTH * 0.25)
    w2 = int(SCREEN_WIDTH * 0.45)
    w3 = SCREEN_WIDTH - (w1 + w2)
    x_cursor = 0
    panels.append(SmallPanel1(x=x_cursor, y=0, width=w1, height=BOTTOM_HEIGHT))
    x_cursor += w1
    panels.append(SmallPanel2(x=x_cursor, y=0, width=w2, height=BOTTOM_HEIGHT))
    x_cursor += w2
    panels.append(SmallPanel3(x=x_cursor, y=0, width=w3, height=BOTTOM_HEIGHT))
    return panels
