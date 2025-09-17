from .base_panel import BasePanel
import arcade
from ui.blacksmith import BlacksmithUI

class SmallPanel1(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height, color=arcade.color.ORANGE, label="Petit 1")
        self.game = BlacksmithUI(width, height)  # your panel has a BlacksmithUI instance

        
    def on_update(self, delta_time: float) -> None:
        self.game.update(delta_time)

    def on_draw(self):
        super().on_draw()
        self.game.draw(offset_x=self.left, offset_y=self.bottom)

