import arcade
import pymunk
import math
import random
import os
import audio_controller

UPSCALE = 1.0

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class BlacksmithUI:
    """Panel-friendly sword stacking class (no arcade.View)."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.static_lines = []


        # Background texture
        background_path = os.path.join(SCRIPT_DIR, "..","ressources", "backgrounds", "blacksmith.png")
        if os.path.exists(background_path):
            self.background = arcade.load_texture(background_path) 
        else :
            #print(f"Background image not found at {background_path}")


    def update(self, delta_time: float):
        pass
        
    def draw(self, offset_x=0, offset_y=0):
        if hasattr(self, "background") and self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(offset_x, offset_y, self.width, self.height)
            )


