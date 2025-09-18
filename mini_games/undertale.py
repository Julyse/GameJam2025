import arcade
import os
import random
from typing import Callable, Optional
from enums.dragon_state import DragonState
from enums.minigames_status import GameStatus

DEBUG_SHOW_HITBOX = False
INVICIBILITY_TILE = 1.5 # IN SECONDS
MOVEMENT_SPEED = 4
HITBOX_HEIGHT = 5
HITBOX_WIDTH = 5

SPRITE_WIDTH = 15
SPRITE_HEIGHT = 15

class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, width: int, height: int, color=(255, 255, 255, 255)):
        texture = arcade.make_soft_square_texture(width, color, outer_alpha=255)
        super().__init__(texture, scale=1.0)
        self.width = width
        self.height = height

    def update(self, screen_width, screen_height, delta_time: float = 1/60):
        """ Move the player and clamp to screen. """
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        elif self.right > screen_width - 1:
            self.right = screen_width - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > screen_height - 1:
            self.top = screen_height - 1

class Undertale:
    """
    Load MAP
    """
    def get_resource_path(self, filename: str) -> str:
        """Return absolute path to a file inside ../resources/undertale."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "..", "resources", "undertale", filename)

    def load_text_file(self, filename: str) -> str:
        """
        Load a text file from the project's 'resources' folder and return its contents as a string.
        """
        base_path = os.path.dirname(__file__) 
        file_path = os.path.join(base_path, "..", "resources", "undertale", filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find resource file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def load_level_as_grid(self, text: str) -> list[list[int]]:
        grid = []
        for line in text.splitlines():
            grid.append([int(ch) for ch in line])
        
        max_rows = 7 
        return grid[:max_rows] if len(grid) > max_rows else grid

    def check_win_condition(self):
        """
        If all walls have scrolled past the left side of the screen, declare WIN.
        """
        if len(self.wall_list) == 0 or all(wall.right < 0 for wall in self.wall_list):
            self.finish(GameStatus.WIN)


    """
    Main application class.
    """
    def __init__(self, width, height, gamemode: DragonState, on_finish: Optional[Callable[[GameStatus], None]] = None):
        """
        Initializer
        """      
        self.screen_width = width #720
        self.screen_height = height #325
        
        self.tile_width = self.screen_width / 15
        self.tile_height = self.screen_height / 7

        self.sprite_scaling = 0.5

        self.game_status = GameStatus.ONGOING
        self.finished = False
        self.on_finish = on_finish

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # NEW: whether the minigame has started (true after first movement key)
        self.started = False

        self.gamemode = gamemode

        # compute the base scroll speeds according to gamemode, but DO NOT start scrolling yet
        match gamemode:
            case DragonState.NORMAL:
                self.base_scroll_speed_x = -1.5
                self.base_scroll_speed_y = 0
            case DragonState.FIRE:
                self.base_scroll_speed_x = -2.5
                self.base_scroll_speed_y = 0
            case DragonState.ICE:
                self.base_scroll_speed_x = -1
                self.base_scroll_speed_y = 0

        # Current active scroll speed — we start frozen until player presses a key
        self.scroll_speed_x = 0
        self.scroll_speed_y = 0

        self.lifepoints = 0 #to remove
        self.invincible = False;

        """ Set up the game and initialize the variables. """
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player(SPRITE_WIDTH, SPRITE_HEIGHT, color=(255, 255, 255, 255))
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50

        self.player_list.append(self.player_sprite)

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        RESOURCE_PATH = os.path.join(BASE_PATH, "..", "resources", "undertale")

        #print('GAMEMODE IS :', self.gamemode)
        match self.gamemode:
            case DragonState.NORMAL:
                self.background = arcade.load_texture(os.path.join(RESOURCE_PATH, "bg.png"))
            case DragonState.FIRE:
                self.background = arcade.load_texture(os.path.join(RESOURCE_PATH, "bg_fire.png"))
            case DragonState.ICE:
                self.background = arcade.load_texture(os.path.join(RESOURCE_PATH, "bg_ice.png"))

        self.player_hitbox = arcade.SpriteSolidColor(
            width=HITBOX_WIDTH,
            height=HITBOX_HEIGHT,
            color=(255, 0, 0, 100)   
        )
        self.player_hitbox.center_x = self.player_sprite.center_x
        self.player_hitbox.center_y = self.player_sprite.center_y
        self.hitbox_list = arcade.SpriteList()
        self.hitbox_list.append(self.player_hitbox)

        # Pick a random map among map_0 / map_1 / map_2 that actually exists
        candidates = ["map_0", "map_1", "map_2"]
        available = [n for n in candidates if os.path.exists(os.path.join(RESOURCE_PATH, n))]
        chosen_map = random.choice(available) if available else "map_0"
        level_data = self.load_text_file(chosen_map)
        level_grid = self.load_level_as_grid(level_data)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        for row_index, row in enumerate(level_grid):
            for col_index, tile in enumerate(row):
                if tile == 1:
                    center_x = col_index * self.tile_width + self.tile_width / 2
                    center_y = (len(level_grid) - row_index - 1) * self.tile_height + self.tile_height / 2

                    match self.gamemode:
                        case DragonState.NORMAL:
                            wall = arcade.SpriteSolidColor(
                                width=self.tile_width,
                                height=self.tile_height,
                                color=(255, 255, 255, 255)
                            )
                            wall.center_x = center_x
                            wall.center_y = center_y
                            self.wall_list.append(wall)
                        case DragonState.FIRE:
                            wall = arcade.load_animated_gif(self.get_resource_path("lava.gif"))
                            wall.width *= self.tile_width / 32 
                            wall.height *= self.tile_height / 32 
                            wall.center_x = center_x
                            wall.center_y = center_y
                            self.wall_list.append(wall)
                        case DragonState.ICE:
                            wall = arcade.SpriteSolidColor(
                                width=self.tile_width,
                                height=self.tile_height,
                                color=arcade.color.SEA_BLUE
                            )
                            wall.center_x = center_x
                            wall.center_y = center_y
                            self.wall_list.append(wall)
                    

    def draw(self, offset_x: float = 0, offset_y: float = 0):
        """
        Render the screen.
        """

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(offset_x, offset_y, self.screen_width, self.screen_height),
        )

        wall_positions = [(wall.center_x, wall.center_y) for wall in self.wall_list]
        player_positions = [(player.center_x, player.center_y) for player in self.player_list]
        hitbox_positions = [(hitbox.center_x, hitbox.center_y) for hitbox in self.hitbox_list]
        
        for wall in self.wall_list:
            wall.center_x += offset_x
            wall.center_y += offset_y
        
        for player in self.player_list:
            player.center_x += offset_x
            player.center_y += offset_y
        
        for hitbox in self.hitbox_list:
            hitbox.center_x += offset_x
            hitbox.center_y += offset_y

        self.wall_list.draw()
            
        if not self.invincible or self.blink_state:
            self.player_list.draw()
        
        if DEBUG_SHOW_HITBOX:
            self.hitbox_list.draw()
        
        for i, wall in enumerate(self.wall_list):
            wall.center_x, wall.center_y = wall_positions[i]
        
        for i, player in enumerate(self.player_list):
            player.center_x, player.center_y = player_positions[i]
        
        for i, hitbox in enumerate(self.hitbox_list):
            hitbox.center_x, hitbox.center_y = hitbox_positions[i]

        if not self.started:
            text = "Appuyez sur Z/Q/S/D ou les flèches directionnels"
            arcade.draw_text(
                text,
                self.screen_width / 2 + offset_x,  # X center
                self.screen_height / 2 + offset_y,  # Y center
                arcade.color.GRAY,
                font_size=14,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

    def update_player_speed(self):
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def take_damage(self):
        """Called whenever the player takes a hit."""

        if (self.lifepoints - 1 < 0):
            self.finish(GameStatus.LOST)

        self.lifepoints -= 1
        #print(f"Player hit! Lifepoints: {self.lifepoints}")

        self.invincible = True
        self.invincibility_timer = INVICIBILITY_TILE
        self.blink_timer = 0.1
        self.blink_state = False


    def manage_collision(self, delta_time):
        if not self.invincible:
            collision = arcade.check_for_collision_with_list(self.player_hitbox, self.wall_list)
            if collision:
                self.take_damage()

        if self.invincible:
            self.invincibility_timer -= delta_time
            self.blink_timer -= delta_time

            if self.blink_timer <= 0:
                self.blink_timer = 0.1
                self.blink_state = not self.blink_state

            if self.invincibility_timer <= 0:
                self.invincible = False
                self.player_sprite.alpha = 255

    def update(self, delta_time):
        """ Movement and game logic """
        # Stop all logic if finished
        if self.finished:
            return

        if not self.started:
            return

        self.player_list.update(self.screen_width, self.screen_height, delta_time)
        self.player_hitbox.center_x = self.player_sprite.center_x
        self.player_hitbox.center_y = self.player_sprite.center_y
        
        self.manage_collision(delta_time)
        if self.gamemode == DragonState.FIRE:
            self.wall_list.update_animation(delta_time)

        walls_to_remove = []
        for wall in self.wall_list:
            wall.center_x += self.scroll_speed_x
            wall.center_y += self.scroll_speed_y
            
            if wall.right < 35:  # Marge de 5 pixels pour être sûr
                walls_to_remove.append(wall)
        
        for wall in walls_to_remove:
            self.wall_list.remove(wall)

        self.check_win_condition()

    def finish(self, status: GameStatus):
        """Mark the game as finished and notify listener without closing the window."""
        if self.finished:
            return
        self.game_status = status
        self.finished = True
        self.started = False
        self.scroll_speed_x = 0
        self.scroll_speed_y = 0
        try:
            if self.on_finish is not None:
                self.on_finish(status)
        except Exception as exc:
            # Avoid crashing the game loop due to callback errors
            #print(f"Error in on_finish callback: {exc}")

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        match key:
            case arcade.key.UP | arcade.key.Z:
                self.up_pressed = True
            case arcade.key.DOWN | arcade.key.S:
                self.down_pressed = True
            case arcade.key.LEFT | arcade.key.Q:
                self.left_pressed = True
            case arcade.key.RIGHT | arcade.key.D:
                self.right_pressed = True
            case _:
                return

        if not self.started:
            self.started = True
            self.scroll_speed_x = self.base_scroll_speed_x
            self.scroll_speed_y = self.base_scroll_speed_y
            #print("Game started (player pressed a movement key).")

        self.update_player_speed()


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        match key:
            case arcade.key.UP | arcade.key.Z:
                self.up_pressed = False
            case arcade.key.DOWN | arcade.key.S:
                self.down_pressed = False
            case arcade.key.LEFT | arcade.key.Q:
                self.left_pressed = False
            case arcade.key.RIGHT | arcade.key.D:
                self.right_pressed = False
            case _:
                return
        
        self.update_player_speed()

#for the other modes
def change_scroll_direction(self, dx: float, dy: float):
    """Change the autoscroll direction dynamically."""
    self.scroll_dx = dx
    self.scroll_dy = dy


if __name__ == "__main__":
    main()
    