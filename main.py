import arcade
from panels import BigPanel, SmallPanel1, SmallPanel2, SmallPanel3
from panels.base_panel import BasePanel
from layout import LayoutView, SCREEN_WIDTH, SCREEN_HEIGHT, BOTTOM_HEIGHT


class Orchestrator(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Forgeron du donjon")
        self.layout_view = None
        self.start_layout()

    def build_panels(self) -> list[BasePanel]:
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

    def start_layout(self):
        self.layout_view = LayoutView(self.build_panels())
        self.show_view(self.layout_view)


def main():
    Orchestrator()
    arcade.run()

if __name__ == "__main__":
    main()