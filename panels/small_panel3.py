from .base_panel import BasePanel
import arcade
from sword_stacking import SwordStacking

class SmallPanel3(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.DARK_SLATE_GRAY, label="Sword Stack")
        self.game = SwordStacking(width, height)
    
    def on_update(self, delta_time: float):
        self.game.update(delta_time)
    
    def on_draw(self):
        super().on_draw()
        self.game.draw(offset_x=self.left, offset_y=self.bottom)
    
    def on_key_press(self, key, modifiers):
        self.game.add_sword()