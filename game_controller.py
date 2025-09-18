import arcade
from panels.base_panel import BasePanel
from panels import BigPanel, SmallPanel1, SmallPanel2, SmallPanel3
from enums.game_state import GameState
from enums.dragon_state import DragonState


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
                    
    def on_key_release(self, key, modifiers):
        for p in self.panels:
            if hasattr(p, "on_key_release"):
                p.on_key_release(key, modifiers)

    def on_key_press(self, key, modifiers):
        for p in self.panels:
            if hasattr(p, "on_key_press"):
                p.on_key_press(key, modifiers)


    @staticmethod
    def start_game(window: arcade.Window):
        panels, sword_panel = GameController.build_default_panels()
        controller = GameController(panels)
        controller.sword_panel = sword_panel 
        window.show_view(controller)
        # Ensure one sword is visible at the start to match initial inventory
        try:
            sword_panel.add_sword()
        except Exception:
            pass
        
        return controller

    @staticmethod
    def build_default_panels() -> list[BasePanel]:
        panels: list[BasePanel] = []
        big_panel = BigPanel(x=0, y=BOTTOM_HEIGHT, width=SCREEN_WIDTH, height=SCREEN_HEIGHT - BOTTOM_HEIGHT, combat_mode=DragonState.NORMAL)
        panels.append(big_panel)
        w1 = int(SCREEN_WIDTH * 0.25)
        w2 = int(SCREEN_WIDTH * 0.45)
        w3 = SCREEN_WIDTH - (w1 + w2)
        x_cursor = 0
        panels.append(SmallPanel1(x=x_cursor, y=0, width=w1, height=BOTTOM_HEIGHT))
        x_cursor += w1
        sp2 = SmallPanel2(x=x_cursor, y=0, width=w2, height=BOTTOM_HEIGHT, big_panel_ref=big_panel, mode=DragonState.ICE)
        panels.append(sp2)
        x_cursor += w2
        sword_panel = SmallPanel3(x=x_cursor, y=0, width=w3, height=BOTTOM_HEIGHT)
        panels.append(sword_panel)
        sp2.sword_panel_ref = sword_panel
        big_panel.sword_panel_ref = sword_panel
        big_panel.minigames_panel_ref = sp2  # connect BigPanel -> SmallPanel2 to stop minigames
        return panels, sword_panel
