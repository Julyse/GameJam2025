from .base_panel import BasePanel
import arcade
from mini_games.flappy import FlappyGame, VisualMode

from mini_games.undertale import Undertale, DragonState

class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        print("x")
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.SKY_BLUE, label="Flappy")

        #pick dragon state depending on the game

        # self.game = FlappyGame(width, height, mode=VisualMode.LAVA)
        self.game = Undertale(width, height, DragonState.FIRE)

        # On n'utilise pas push_handlers car la propagation des événements
        # est gérée par LayoutView qui appelle on_key_press et on_key_release

    def on_update(self, delta_time: float):
        self.game.update(delta_time)

    def on_draw(self):
        super().on_draw()
        # Pas de scissor disponible, on dessine simplement avec les offsets
        self.game.draw(offset_x=self.left, offset_y=self.bottom)

    def on_key_press(self, key, modifiers):
        self.game.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        print(f"Key released: {key}")
        self.game.on_key_release(key, modifiers)

