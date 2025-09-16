from .base_panel import BasePanel
import arcade
from arcade import Sprite, SpriteList, color, draw_text
from math import pi
from random import random, gauss, uniform


class BigPanel(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height, color=arcade.color.BEIGE, label="")

        # --- Contenu "Arena" embarqué ---
        self.sprites = SpriteList()

        self.knight = Sprite()
        self.drake = Sprite()
        self.sword = Sprite()

        center_x = self.width / 2 + x
        center_y = self.height / 2 + y

        padding = uniform(200, 350)

        self.knight.position = (center_x - padding, center_y)
        self.drake.position = (center_x + padding, center_y)
        self.sword.position = (center_x - padding + 100, center_y + 20)
        
        self.sword.width /= 4
        self.drake.width += 200

        self.sword.angle = 40

        self.sprites.append(self.knight)
        self.sprites.append(self.drake)
        self.sprites.append(self.sword)

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
        draw_text("Arena", self.left + 20, self.bottom + 20, color.BLACK)

