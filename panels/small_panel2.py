from .base_panel import BasePanel
import arcade
from mini_games.flappy import FlappyGame
from enums.dragon_state import DragonState
from mini_games.undertale import Undertale

class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int): #DragonState
        print("x")
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.SKY_BLUE, label="Flappy")

        # self.game = FlappyGame(width, height, mode=DragonState.FIRE)
        self.game = Undertale(width, height, DragonState.NORMAL)


    def on_update(self, delta_time: float):
        self.game.update(delta_time)

    def on_draw(self):
        super().on_draw()
        self.game.draw(offset_x=self.left, offset_y=self.bottom)

    def on_key_press(self, key, modifiers):
        self.game.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.game.on_key_release(key, modifiers)

