from .base_panel import BasePanel
import arcade
from mini_games.flappy import FlappyGame
from enums.dragon_state import DragonState
from enums.minigames_status import GameStatus
from mini_games.undertale import Undertale

class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int, *, big_panel_ref=None, sword_panel_ref=None, mode: DragonState = DragonState.FIRE):
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.SKY_BLUE, label="Flappy")
        self.game = None
        self.last_result: GameStatus | None = None
        self._next_is_undertale = True
        self.big_panel_ref = big_panel_ref
        self.sword_panel_ref = sword_panel_ref
        self.mode = mode
        self.start_next_minigame()

    def start_undertale(self):
        self.last_result = None
        self.game = Undertale(self.width, self.height, self.mode, on_finish=self.on_game_finish)

    def start_flappy(self):
        self.last_result = None
        self.game = FlappyGame(self.width, self.height, mode=self.mode, on_finish=self.on_game_finish)

    def start_next_minigame(self):
        if self._next_is_undertale:
            self.start_undertale()
        else:
            self.start_flappy()
        self._next_is_undertale = not self._next_is_undertale

    def on_game_finish(self, status: GameStatus):
        # Award sword if mini-game won
        if status == GameStatus.WIN:
            if self.big_panel_ref and hasattr(self.big_panel_ref, 'encounter'):
                self.big_panel_ref.encounter.add_sword(1)
            if self.sword_panel_ref and hasattr(self.sword_panel_ref, 'add_sword'):
                self.sword_panel_ref.add_sword()
        # Immediately start next minigame; built-in prompts from each mini-game will show
        self.game = None
        self.last_result = None
        self.start_next_minigame()

    def on_update(self, delta_time: float):
        if self.game is not None:
            self.game.update(delta_time)

    def on_draw(self):
        super().on_draw()
        if self.game is not None:
            self.game.draw(offset_x=self.left, offset_y=self.bottom)

    def on_key_press(self, key, modifiers):
        if self.game is not None:
            self.game.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.game is not None:
            self.game.on_key_release(key, modifiers)