import arcade
from panels.base_panel import BasePanel
from panels import BigPanel, SmallPanel1, SmallPanel2, SmallPanel3
from enums.game_state import GameState

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
BOTTOM_HEIGHT = 260
NUM_SMALL = 3

class GameController(arcade.View):
    def __init__(self, panels: list[BasePanel]):
        super().__init__()
        self.panels = panels
        self.state = GameState.GAME
        


    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        for p in self.panels:
            p.on_draw()

    def on_update(self, delta_time: float):
        for p in self.panels:
            p.on_update(delta_time)

    def on_key_press(self, key, modifiers):
        for p in self.panels:
            if hasattr(p, "on_key_press"):
                p.on_key_press(key, modifiers)
    def start_game(self):
        self.controller = GameController.start_game(self)
    def on_key_press(self, key, modifiers):
        for p in self.panels:
            if hasattr(p, "on_key_press"):
                p.on_key_press(key, modifiers)

        if key == arcade.key.C: 
            print("Craft une épée")
            self.sword_panel.game.add_sword()

        if key == arcade.key.U: 
            print("Utilise une épée")
            self.sword_panel.game.remove_sword()
    @staticmethod
    def start_game(window: arcade.Window):
        panels, sword_panel = build_default_panels()
        controller = GameController(panels)
        controller.sword_panel = sword_panel 
        window.show_view(controller)        
        return controller

def build_default_panels() -> list[BasePanel]:
    panels: list[BasePanel] = []
    panels.append(BigPanel(x=0, y=BOTTOM_HEIGHT, width=SCREEN_WIDTH, height=SCREEN_HEIGHT - BOTTOM_HEIGHT))
    w1 = int(SCREEN_WIDTH * 0.25)
    w2 = int(SCREEN_WIDTH * 0.45)
    w3 = SCREEN_WIDTH - (w1 + w2)
    x_cursor = 0
    panels.append(SmallPanel1(x=x_cursor, y=0, width=w1, height=BOTTOM_HEIGHT))
    x_cursor += w1
    panels.append(SmallPanel2(x=x_cursor, y=0, width=w2, height=BOTTOM_HEIGHT))
    x_cursor += w2
    sword_panel = SmallPanel3(x=x_cursor, y=0, width=w3, height=BOTTOM_HEIGHT)
    panels.append(sword_panel)
    return panels, sword_panel
