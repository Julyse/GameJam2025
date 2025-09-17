import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout
from ui.cinematic import CinematicView
from dialogues.start_dialogues import START_DIALOGUES

class QuitButton(arcade.gui.widgets.buttons.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        v_box = arcade.gui.widgets.layout.UIBoxLayout(space_between=20)

        title_label = arcade.gui.UILabel(
            text="Forgeron du donjon",
            width=450,
            height=40,
            font_size=28,
            text_color=arcade.color.WHITE,
        )
        v_box.add(title_label)

        start_button = arcade.gui.UIFlatButton(text="Lancer le jeu", width=220)
        options_button = arcade.gui.UIFlatButton(text="Options", width=220)
        quit_button = QuitButton(text="Quitter", width=220)

        v_box.add(start_button)
        v_box.add(options_button)
        v_box.add(quit_button)

        @start_button.event("on_click")
        def on_click_start(event):
            self.start_cinematic()

        @options_button.event("on_click")
        def on_click_options(event):
            print("Options…")

        anchor = arcade.gui.widgets.layout.UIAnchorLayout()
        anchor.add(child=v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def start_cinematic(self):
        if hasattr(self.manager, "disable"):
            self.manager.disable()
        if hasattr(self.manager, "clear"):
            self.manager.clear()
        elif hasattr(self.manager, "purge_ui_elements"):
            self.manager.purge_ui_elements()
        elif hasattr(self.manager, "children"):
            self.manager.children = []
        self.window.show_view(CinematicView(START_DIALOGUES))

    def on_hide_view(self):
        if hasattr(self.manager, "disable"):
            self.manager.disable()
        if hasattr(self.manager, "clear"):
            self.manager.clear()
        elif hasattr(self.manager, "purge_ui_elements"):
            self.manager.purge_ui_elements()
        elif hasattr(self.manager, "children"):
            self.manager.children = []