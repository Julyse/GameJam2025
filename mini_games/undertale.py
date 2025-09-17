import arcade
import os
from enum import Enum

DEBUG_SHOW_HITBOX = True

# to be moved and used by everyone, same for dragon mode
class GameStatus(Enum):
    ONGOING = 1
    WIN = 2
    LOST = 3

SPRITE_SCALING = 0.5
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 325
SCREEN_TITLE = "temp"
MOVEMENT_SPEED = 6
TILE_WIDTH = SCREEN_WIDTH / 10
TILE_HEIGHT = SCREEN_HEIGHT / 5

INVICIBILITY_TIME = 1.5 # IN SECONDS

HITBOX_HEIGHT = 20
HITBOX_WIDTH = 20

class Player(arcade.Sprite):
    """ Player Class """

    def update(self, delta_time: float = 1/60):
        """ Move the player """
        # Move player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1

class MyGame(arcade.Window):
    """
    Load MAP
    """

    # to use
    #to be static
    def get_resource_path(self, filename: str) -> str:
        """Return absolute path to a file inside ../resources/undertale."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "..", "resources", "undertale", filename)

    # map_1, map_2, ...
    # should be static?
    def load_text_file(self, filename: str) -> str:
        """
        Load a text file from the project's 'resources' folder and return its contents as a string.
        """
        # Build full path relative to project root
        base_path = os.path.dirname(__file__)  # folder where this script lives
        file_path = os.path.join(base_path, "..", "resources", "undertale", filename)

        # Make sure the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find resource file: {file_path}")

        # Read file contents
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    # should be static?
    def load_level_as_grid(self, text: str) -> list[list[int]]:
        grid = []
        for line in text.splitlines():
            grid.append([int(ch) for ch in line])
        return grid


    """
    Main application class.
    """
    def __init__(self, width, height, title, gamemode):
        """
        Initializer
        """
        # Call the parent class initializer
        super().__init__(width, height, title)

        self.game_status = GameStatus.ONGOING

        # Variables that will hold sprite lists
        # self.player_list = None 
        # Set up the player info
        self.player_sprite = None
        self.player_hitbox = None
        self.hitbox_list = None
        # To be replaced with the image
        self.background = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # to-do switch gamemode for scrolling speed ....
        self.scroll_speed_x = -1
        self.scroll_speed_y = 0

        #should maybe be in player class
        self.lifepoints = 3
        self.invincible = False; 

        self.fire_list = None

    def setup(self):
        """ Set up the game and initialize the variables. """
        # Sprite lists
        self.player_list = arcade.SpriteList()
        # Set up the player
        self.player_sprite = Player(":resources:images/animated_characters/female_person/"
                                    "femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50

        self.player_list.append(self.player_sprite)

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))  # folder where THIS script is located
        RESOURCE_PATH = os.path.join(BASE_PATH, "..", "resources", "undertale")  # go up one folder
        # self.background = arcade.load_texture(os.path.join(RESOURCE_PATH, "bg.png"))
        self.background = arcade.load_texture(os.path.join(RESOURCE_PATH, "bg_fire.png"))

        print(self.get_resource_path("bg.png"))
        print(os.path.exists(self.get_resource_path("bg.png")))

        self.player_hitbox = arcade.SpriteSolidColor(
            width=HITBOX_WIDTH,  # smaller than your player sprite
            height=HITBOX_HEIGHT,
            color=(255, 0, 0, 100)   
        )
        self.player_hitbox.center_x = self.player_sprite.center_x
        self.player_hitbox.center_y = self.player_sprite.center_y
        self.hitbox_list = arcade.SpriteList()
        self.hitbox_list.append(self.player_hitbox)

        level_data = self.load_text_file("map_1")
        level_grid = self.load_level_as_grid(level_data)


        # fire_sprite_template = arcade.load_animated_gif(self.get_resource_path("fire.gif"))
        # fire_sprite_template.scale = FIRE_SCALING

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.fire_list = arcade.SpriteList(use_spatial_hash=True)
        for row_index, row in enumerate(level_grid):
            for col_index, tile in enumerate(row):
                if tile == 1:
                    # maybe we should define spritesolidcolr outsite
                    wall = arcade.SpriteSolidColor(
                        width=TILE_WIDTH,
                        height=TILE_HEIGHT,
                        # color=(255, 255, 255, 255)
                        color=(255, 0, 0, 255)
                    )

                    wall.center_x = col_index * TILE_WIDTH + TILE_WIDTH / 2
                    wall.center_y = (len(level_grid) - row_index - 1) * TILE_HEIGHT + TILE_HEIGHT / 2

                    self.wall_list.append(wall)


                    #PATH CAN ALSO BE Pathlib.Path
                    
                    fire_wall = arcade.load_animated_gif(self.get_resource_path("lava.gif"))
                    fire_wall.width *= TILE_WIDTH / 32 
                    fire_wall.height *= TILE_HEIGHT / 32 

                                        
                    fire_wall.center_x = wall.center_x
                    fire_wall.center_y = wall.center_y

                    self.fire_list.append(fire_wall)
        #load_level
        # print(level_grid)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        self.wall_list.draw() 
        self.fire_list.draw()
        # Draw all the sprites.
        if not self.invincible or self.blink_state:
            self.player_list.draw()

        if (DEBUG_SHOW_HITBOX):
            self.hitbox_list.draw()  # Debug

    def update_player_speed(self):
        # Calculate speed based on the keys pressed
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

        #
        # DO A CHECK EVERY GAME LOOP IF GAME OVER
        # 

        if (self.lifepoints - 1 < 0):
            self.game_status = GameStatus.LOST
            # return ?

        self.lifepoints -= 1
        print(f"Player hit! Lifepoints: {self.lifepoints}")

        # Trigger invincibility period
        self.invincible = True
        self.invincibility_timer = INVICIBILITY_TIME
        self.blink_timer = 0.1          # start blink timer
        self.blink_state = False


    def manage_collision(self, delta_time):
        # If not invincible, check for collisions
        if not self.invincible:
            collision = arcade.check_for_collision_with_list(self.player_hitbox, self.wall_list)
            if collision:
                self.take_damage()

        # If invincible, count down
        if self.invincible:
            self.invincibility_timer -= delta_time
            self.blink_timer -= delta_time

            # Toggle blinking every 0.1s
            if self.blink_timer <= 0:
                self.blink_timer = 0.1
                self.blink_state = not self.blink_state

            if self.invincibility_timer <= 0:
                self.invincible = False
                self.player_sprite.alpha = 255  # fully visible again

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player
        self.player_list.update(delta_time)
        self.player_hitbox.center_x = self.player_sprite.center_x
        self.player_hitbox.center_y = self.player_sprite.center_y
        
        self.manage_collision(delta_time)
        # collision = arcade.check_for_collision_with_list(self.player_hitbox, self.wall_list)
        # print(self.lifepoints)
        # print(collision)

        #only if fire
        self.fire_list.update_animation(delta_time)
        for fire_wall in self.fire_list:
            fire_wall.center_x += self.scroll_speed_x
            fire_wall.center_y += self.scroll_speed_y

        for wall in self.wall_list:
            wall.center_x += self.scroll_speed_x
            wall.center_y += self.scroll_speed_y

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

#self.change_scroll_direction(0, 2)

def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, "Fire")
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
    
# Mod shift space

# source venv/bin/activate

# ajuster hitbox, mettre tout les paramètres en constante

# charger map aléatoire
# créer des maps
# charger sprite

# coeur qui clignote
# hp
# 3 mode
# - normal
# - feu : plus rapide et hitbox enflamé donc plus grosse
# - glace : inverse sens souvent
# assets

# enum for gamemode
# implementer à main menu

# reafacor

# ENUM A RETURN WITH GAME STATUS {LOST / WIN}