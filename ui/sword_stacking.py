from sys import platform
import arcade
import pymunk
import math
import random
import os
import audio_controller
from PIL import Image
import io

UPSCALE = 4.5

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SWORD_FOLDER = os.path.join(SCRIPT_DIR, "..", "ressources", "sprites", "swords")
SOUND_FOLDER = os.path.join(SCRIPT_DIR, "..", "ressources", "audio")

if platform == "darwin":
    sounds = ["broke_sword.wav", "craft_sword_fixed.wav","music.mp3"]

else:
    sounds = ["broke_sword.wav", "craft_sword.wav","music.mp3"]


class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename, scale=1.0):
        super().__init__(
            filename,
            scale=scale,
            center_x=pymunk_shape.body.position.x,
            center_y=pymunk_shape.body.position.y,
        )
        self.pymunk_shape = pymunk_shape


class SwordStacking:
    """Panel-friendly sword stacking class (no arcade.View)."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.sprite_list: arcade.SpriteList[PhysicsSprite] = arcade.SpriteList()
        self.static_lines = []

        # Physics
        self.space = pymunk.Space()
        self.space.iterations = 10
        self.space.gravity = (0.0, -900.0)
        self.physics_time = 0.0
        self.physics_step = 1 / 30.0

        # Audio
        self.audio = audio_controller.SoundController()
        self.load_sounds()

        # load sword images
        self.sword_files = [
            os.path.join(SWORD_FOLDER, f)
            for f in os.listdir(SWORD_FOLDER)
            if f.lower().endswith((".png", ".jpg"))
        ]
        if not self.sword_files:
            raise FileNotFoundError(f"No sword images found in {SWORD_FOLDER}")

        # Background texture
        background_path = os.path.join(SCRIPT_DIR, "..", "ressources", "backgrounds", "right_screen_background.png")
        if os.path.exists(background_path):
            self.background = arcade.load_texture(background_path)  
        else:
            #print(f"Background image not found at {background_path}")
            None

        self._create_boundaries()
        self.audio.load_and_loop_music("background", r"ressources\audio\music.mp3", volume=0.5)

    def load_sounds(self):
        for file in sounds:
            path = os.path.join(SOUND_FOLDER, file)
            key = file.replace(".wav", "")
            self.audio.load_sound(key, path)

    def add_sword(self):
        mass = 1.0
        width, height = 32 * UPSCALE, 8 * UPSCALE
       
        x = random.randint(40, self.width - 40)
        y = random.randint(self.height // 2, self.height - 20)

        # Random drop angle
        angle = random.uniform(0, 2 * math.pi)

        # Physics body
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, (width, height)))
        body.position = x, y
        body.angle = angle

        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = 0.6
        shape.elasticity = 0.1
        self.space.add(body, shape)

        # Load texture
        sword_file = random.choice(self.sword_files)
        sprite = PhysicsSprite(shape, sword_file, scale=UPSCALE)
        texture = arcade.load_texture(sword_file)
        sprite.texture = texture
        if hasattr(texture, 'texture') and hasattr(texture.texture, 'filter'):
            texture.texture.filter = (arcade.gl.NEAREST, arcade.gl.NEAREST)

        # Set sprite angle based on physics body
        sprite.angle = -math.degrees(angle) + 90
        self.sprite_list.append(sprite)

        self.audio.play("craft_sword", volume=0.5)
        return sprite

    def remove_sword(self, sprite=None, index=None):
        """Remove a sword from the game.

        If a sprite is provided, remove that sprite. If an index is provided,
        remove the sword at that index. Otherwise, remove the most recently
        added sword (top of the stack).
        """
        if len(self.sprite_list) == 0:
            #print("No swords to remove")
            return False

        target_sprite = None
        if sprite is not None and sprite in self.sprite_list:
            target_sprite = sprite
        elif index is not None and 0 <= index < len(self.sprite_list):
            target_sprite = self.sprite_list[index]
        else:
            # Default: remove last (most recently added)
            target_sprite = self.sprite_list[-1]

        # Remove from physics space (shape then body)
        try:
            self.space.remove(target_sprite.pymunk_shape, target_sprite.pymunk_shape.body)
        except Exception:
            pass

        # Remove from sprite list
        target_sprite.remove_from_sprite_lists()

        # Play sound
        try:
            self.audio.play("broke_sword", volume=1.0)
        except Exception:
            pass
        #print("Removed sword")
        return True

    def remove_all_swords(self):
        for sprite in self.sprite_list[:]:
            self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
            sprite.remove_from_sprite_lists()

    def get_sword_count(self):
        return len(self.sprite_list)

    def update(self, delta_time: float):
        self.physics_time += delta_time
        while self.physics_time >= self.physics_step:
            self.space.step(self.physics_step)
            self.physics_time -= self.physics_step

        for sprite in self.sprite_list:
            if sprite.pymunk_shape.body.position.y < -50:
                self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
                sprite.remove_from_sprite_lists()
            else:
                sprite.center_x = sprite.pymunk_shape.body.position.x
                sprite.center_y = sprite.pymunk_shape.body.position.y
                sprite.angle = -math.degrees(sprite.pymunk_shape.body.angle) + 90

    def draw(self, offset_x=0, offset_y=0):
        # Draw background
        if hasattr(self, "background") and self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(offset_x, offset_y, self.width, self.height)
            )

        # Draw all swords
        for sprite in self.sprite_list:
            # Use the current physics angle
            angle_deg = -math.degrees(sprite.pymunk_shape.body.angle) + 90

            arcade.draw_texture_rect(
                sprite.texture,
                arcade.LBWH(
                    sprite.pymunk_shape.body.position.x + offset_x - sprite.width / 2,
                    sprite.pymunk_shape.body.position.y + offset_y - sprite.height / 2,
                    sprite.width,
                    sprite.height
                ),
                angle=angle_deg
            )

    def _create_boundaries(self):
        floor_height = 10
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, floor_height], [self.width, floor_height], 0.0)
        floor_shape.friction = 1.0
        self.space.add(floor_body, floor_shape)

        left_wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        left_wall_shape = pymunk.Segment(left_wall_body, [0, 0], [0, self.height], 0.0)
        left_wall_shape.friction = 0.7
        self.space.add(left_wall_body, left_wall_shape)

        right_wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        right_wall_shape = pymunk.Segment(right_wall_body, [self.width, 0], [self.width, self.height], 0.0)
        right_wall_shape.friction = 0.7
        self.space.add(right_wall_body, right_wall_shape)