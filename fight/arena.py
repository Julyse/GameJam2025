from random import randint, random, uniform
from math import pi
from arcade import Sprite, View, SpriteList, color, draw_text
from numpy.random import normal

class Arena(View):
    def __init__(self):
        super().__init__()
        
        # Set background
        self.background_color = color.BEIGE
        
        # Set sprites

        self.sprites = SpriteList()

        self.knight = Sprite()
        self.knight.position = (self.center_x, self.center_y + self.center_y / 2)

        self.drake = Sprite()
        self.drake.position = (self.center_x, self.center_y / 2)

        self.sprites.append(self.knight)
        self.sprites.append(self.drake)

        # Set decorations
        # TODO: implement texturing
        self.n_dec = 30
        
        x_normal = normal(float(self.center_x/2), float(self.center_x/2), self.n_dec)
        y_normal = normal(float(self.center_y/2), float(self.center_y/2), self.n_dec)

        for i in range(0, self.n_dec):
            dec = Sprite()
            
            r_scale = random() / 2
            scale = (r_scale, r_scale)

            r_x = uniform(0, self.width)
            r_y = uniform(0, self.height)

            dec.position = (x_normal[i], y_normal[i])

            dec.scale = scale
            dec.angle = 2 * pi * random()
            self.sprites.append(dec)

        # Draw and store text

    def on_draw(self) -> bool | None:
        self.clear()
        self.sprites.draw()

        draw_text("Delta Time:"+str("aa"), 100, 100, color.BLACK)

    def on_update(self, delta_time: float) -> bool | None:
        super().on_update(delta_time)

