from .base_panel import BasePanel
import arcade


class SmallPanel1(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height, color=arcade.color.ORANGE, label="Petit 1")

    def on_update(self, delta_time: float) -> None:
        pass

