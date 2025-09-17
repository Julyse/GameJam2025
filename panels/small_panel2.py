from .base_panel import BasePanel
import arcade
from mini_games.flappy import FlappyGame, VisualMode
 
class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.SKY_BLUE, label="Flappy")
        self.game = FlappyGame(width, height, mode=VisualMode.LAVA)
 
    def on_update(self, delta_time: float):
        self.game.update(delta_time)

    def on_draw(self):
        super().on_draw()
        self.game.draw(offset_x=self.left, offset_y=self.bottom)

    def on_key_press(self, key, modifiers):
        self.game.on_key_press(key, modifiers)

