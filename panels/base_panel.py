import arcade
from arcade.sections import Section


class BasePanel(Section):
    def __init__(self, x: int, y: int, width: int, height: int, *, color: arcade.color, label: str):
        super().__init__(x, y, width, height, name=label)
        self.color = color
        self.label = label


    def on_draw(self) -> None:
        arcade.draw_lrbt_rectangle_filled(
            self.left,
            self.right,
            self.bottom,
            self.top,
            self.color,
        )
        arcade.draw_text(
            self.label,
            self.left + 20,
            self.bottom + (self.height // 2) - 12,
            arcade.color.WHITE,
            20,
            font_name=("Righteous", "arial", "calibri"),
        )

