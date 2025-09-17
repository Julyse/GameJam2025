import arcade

FONT_PATH = "ressources/fonts/Righteous.ttf"

class FontLoader:
    def __init__(self):
        self.instance = None
        self.font = None

    def load_font(self):
        self.font = arcade.load_font(FONT_PATH)
        return self.font

    @staticmethod
    def get_font() -> arcade.Font:
        if FontLoader.instance is None:
            FontLoader.instance = FontLoader()
            FontLoader.instance.load_font()
        return FontLoader.instance.font