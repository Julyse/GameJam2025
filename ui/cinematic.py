import arcade
from game_controller import GameController
from ui import MessageBox

KEYS_TO_ADVANCE = [
    arcade.key.SPACE,
    arcade.key.ENTER,
    arcade.key.ESCAPE,
]

class CinematicView(arcade.View):
    def __init__(self, messages: list[str], *, cps: float = 35.0):
        super().__init__()
        self.messages = messages
        self.index = 0

        from game_controller import SCREEN_WIDTH, SCREEN_HEIGHT

        margin = 40
        box_width = SCREEN_WIDTH - margin * 2
        box_height = int(SCREEN_HEIGHT * 0.28)
        box_x = margin
        box_y = margin

        self.box = MessageBox(
            x=box_x,
            y=box_y,
            width=box_width,
            height=box_height,
            background_texture_path=None,
            text=self.messages[self.index],
            characters_per_second=cps,
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time: float):
        self.box.update(delta_time)

    def on_draw(self):
        self.clear()
        self.box.draw()

        hint = "[ESPACE] avancer"
        arcade.draw_text(
            hint,
            10,
            10,
            arcade.color.GRAY,
            14,
        )

    def _advance_or_finish(self):
        if self.box.is_finished():
            self.index += 1
            if self.index < len(self.messages):
                self.box.set_text(self.messages[self.index])
            else:
                self._start_game()
        else:
            self.box.skip()

    def on_key_press(self, key, modifiers):
        if key in KEYS_TO_ADVANCE:
            self._advance_or_finish()

    def _start_game(self):
        GameController.start_game(self.window)
