import arcade
from panels import BigPanel, SmallPanel1, SmallPanel2, SmallPanel3
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
class MultiView(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Layout Modulaire")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Créer les panneaux une seule fois
        self.panels = self._create_panels()

    # -- Création des panneaux
    def _create_panels(self) -> list[BasePanel]:
        panels: list[BasePanel] = []

        # Grand panneau en haut
        panels.append(BigPanel(
            x=0,
            y=BOTTOM_HEIGHT,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT - BOTTOM_HEIGHT,
        ))

        # Petits panneaux en bas (ajuster largeurs : élargir Petit 2, réduire Petit 1)
        w1 = int(SCREEN_WIDTH * 0.25)
        w2 = int(SCREEN_WIDTH * 0.45)
        w3 = SCREEN_WIDTH - (w1 + w2)
        widths = [w1, w2, w3]
        x_cursor = 0
        # Petit 1
        panels.append(SmallPanel1(x=x_cursor, y=0, width=widths[0], height=BOTTOM_HEIGHT))
        x_cursor += widths[0]
        # Petit 2
        panels.append(SmallPanel2(x=x_cursor, y=0, width=widths[1], height=BOTTOM_HEIGHT))
        x_cursor += widths[1]
        # Petit 3
        panels.append(SmallPanel3(x=x_cursor, y=0, width=widths[2], height=BOTTOM_HEIGHT))
        return panels

    # -- Dessin
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
    MultiView()
    arcade.run()


if __name__ == "__main__":
    main()
