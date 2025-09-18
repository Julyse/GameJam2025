from .base_panel import BasePanel
import arcade
from mini_games.flappy import FlappyGame
from enums.dragon_state import DragonState
from enums.minigames_status import GameStatus
from mini_games.undertale import Undertale

class SmallPanel2(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int, *, big_panel_ref=None, sword_panel_ref=None, mode=DragonState.NORMAL):
        super().__init__(x=x, y=y, width=width, height=height,
                         color=arcade.color.SKY_BLUE, label="Flappy")
        self.game = None
        self.last_result: GameStatus | None = None
        self._next_is_undertale = True
        self.big_panel_ref = big_panel_ref
        self.sword_panel_ref = sword_panel_ref
        self.mode = mode
        self.enabled = True  # allow BigPanel to disable minigames
        self.start_next_minigame()

    def start_undertale(self):
        self.last_result = None
        mode= self.big_panel_ref.combat_mode 
        self.game = Undertale(self.width, self.height, mode, on_finish=self.on_game_finish)

    def start_flappy(self):
        self.last_result = None
        mode= self.big_panel_ref.combat_mode 
        self.game = FlappyGame(self.width, self.height, mode, on_finish=self.on_game_finish)

    def start_next_minigame(self):
        if not self.enabled:
            return
        if self._next_is_undertale:
            self.start_undertale()
        else:
            self.start_flappy()
        self._next_is_undertale = not self._next_is_undertale

    def on_game_finish(self, status: GameStatus):
        if not self.enabled:
            return
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
        if not self.enabled:
            return
        if self.game is not None:
            self.game.update(delta_time)
    
    def on_draw(self):
        super().on_draw()
        if self.game is not None:
            self.game.draw(offset_x=self.left, offset_y=self.bottom)
    
    def on_key_press(self, key, modifiers):
        if not self.enabled:
            return
        if self.game is not None:
            self.game.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if not self.enabled:
            return
        if self.game is not None:
            self.game.on_key_release(key, modifiers)

    def disable_minigames(self):
        """Stop current minigame and prevent starting new ones."""
        self.enabled = False
        if self.game is not None:
            try:
                if hasattr(self.game, "finish"):
                    self.game.finish(GameStatus.LOST)
                else:
                    setattr(self.game, "finished", True)
            except Exception:
                pass