from .base_panel import BasePanel
import arcade
from arcade import Sprite, SpriteList, color, draw_text
from math import pi
from random import random, gauss


class BigPanel(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height, color=arcade.color.AIR_FORCE_BLUE, label="Grand ecran")

        # --- Contenu "Arena" embarqué ---
        self.sprites = SpriteList()

        center_x = self.left + self.width / 2
        center_y = self.bottom + self.height / 2

        self.knight = Sprite()
        self.knight.position = (center_x, center_y + center_y / 2)

        self.drake = Sprite()
        self.drake.position = (center_x, center_y / 2)

        self.sprites.append(self.knight)
        self.sprites.append(self.drake)

        # Décors
        self.n_dec = 30
        x_normal = [gauss(self.width / 2, self.width / 2) for _ in range(self.n_dec)]
        y_normal = [gauss(self.height / 2, self.height / 2) for _ in range(self.n_dec)]

        for i in range(self.n_dec):
            dec = Sprite()
            r_scale = random() / 2
            dec.scale = r_scale
            dec.angle = 2 * pi * random()

            # Position relative au panel
            dec.position = (self.left + x_normal[i], self.bottom + y_normal[i])
            self.sprites.append(dec)

    def on_update(self, delta_time: float) -> None:
        # Logique d'update future pour les sprites
        pass

    def on_draw(self) -> None:
        # Dessin du fond + label par la classe de base
        super().on_draw()
        # Dessin du contenu Arena dans la zone du panel
        self.sprites.draw()
        draw_text("Arena", self.left + 20, self.bottom + 20, color.BLACK, font_name=("Righteous", "arial", "calibri"))

