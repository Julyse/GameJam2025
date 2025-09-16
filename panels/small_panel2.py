from .base_panel import BasePanel
import arcade


class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height, color=arcade.color.SKY_BLUE, label="Petit 2")

    def update(self, delta_time: float) -> None:
        pass

