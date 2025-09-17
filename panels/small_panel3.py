from .base_panel import BasePanel
import arcade
from ui.sword_stacking import SwordStacking

class SmallPanel3(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.DARK_SLATE_GRAY, label="Sword Stack")
        self.game = SwordStacking(width, height)  # your panel has a SwordStacking instance

    # expose add/remove methods so external code can call them
    def add_sword(self):
        return self.game.add_sword()

    def remove_sword(self, sprite=None, index=None):
        return self.game.remove_sword(sprite, index)

    def remove_all_swords(self):
        self.game.remove_all_swords()

    # update & draw
    def on_update(self, delta_time: float):
        self.game.update(delta_time)
    
    def on_draw(self):
        super().on_draw()
        self.game.draw(offset_x=self.left, offset_y=self.bottom)
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.game.add_sword()  # optionel pour test
