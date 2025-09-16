from .base_panel import BasePanel
import arcade


class BigPanel(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height, color=arcade.color.AIR_FORCE_BLUE, label="Grand écran", speed=0.5)

