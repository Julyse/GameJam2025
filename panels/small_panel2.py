from .base_panel import BasePanel
import arcade
from mini_games.flappy import FlappyGame
from enums.dragon_state import DragonState
from enums.minigames_status import GameStatus
from mini_games.undertale import Undertale

class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int): #DragonState
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.SKY_BLUE, label="Flappy")

        self.game = None
        self.last_result: GameStatus | None = None
        self._next_is_undertale = True
        self.start_next_minigame()

    def start_undertale(self):
        self.last_result = None
        self.game = Undertale(self.width, self.height, DragonState.NORMAL, on_finish=self.on_game_finish)

    def start_flappy(self):
        self.last_result = None
        self.game = FlappyGame(self.width, self.height, mode=DragonState.NORMAL, on_finish=self.on_game_finish)

    def start_next_minigame(self):
        if self._next_is_undertale:
            self.start_undertale()
        else:
            self.start_flappy()
        self._next_is_undertale = not self._next_is_undertale

    def on_game_finish(self, status: GameStatus):
        # Stop rendering the minigame and show result on panel
        self.last_result = status
        self.game = None


    def on_update(self, delta_time: float):
        if self.game is not None:
            self.game.update(delta_time)

    def on_draw(self):
        super().on_draw()
        if self.game is not None:
            self.game.draw(offset_x=self.left, offset_y=self.bottom)
        elif self.last_result is not None:
            # Show a simple WIN/LOST message centered in the panel
            msg = "WIN" if self.last_result == GameStatus.WIN else "LOST"
            color = arcade.color.APPLE_GREEN if self.last_result == GameStatus.WIN else arcade.color.RED_ORANGE
            arcade.draw_text(
                msg,
                self.left + self.width / 2,
                self.bottom + self.height / 2,
                color,
                28,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )
            arcade.draw_text(
                "Press SPACE for next minigame",
                self.left + self.width / 2,
                self.bottom + self.height / 2 - 40,
                arcade.color.WHITE,
                16,
                anchor_x="center",
                anchor_y="center",
            )

    def on_key_press(self, key, modifiers):
        if self.game is not None:
            self.game.on_key_press(key, modifiers)
        else:
            if key == arcade.key.SPACE:
                self.start_next_minigame()

    def on_key_release(self, key, modifiers):
        if self.game is not None:
            self.game.on_key_release(key, modifiers)

