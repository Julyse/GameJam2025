import arcade
import random
from enum import Enum

# ---------- Dimensions de référence (monde logique) ----------
REF_WIDTH  = 1280
REF_HEIGHT = 720

# ---------- Constantes du jeu ----------
BIRD_X        = REF_WIDTH * 0.25
BIRD_SIZE     = 35
GRAVITY       = 1200
FLAP_STRENGTH = 400

PIPE_WIDTH         = 100
GAP_HEIGHT         = 230
PIPE_SPEED         = 250
PIPE_INTERVAL      = 1.6
PIPE_VERTICAL_SPEED = 30

FONT_SIZE = 36

class VisualMode(Enum):
    NORMAL = "normal"
    LAVA   = "lava"
    OCEAN  = "ocean"

PALETTES = {
    VisualMode.NORMAL: (arcade.color.SKY_BLUE, arcade.color.GREEN),
    VisualMode.LAVA:   (arcade.color.DARK_TANGERINE, arcade.color.DARK_RED),
    VisualMode.OCEAN:  (arcade.color.SEA_BLUE, arcade.color.DARK_BLUE),
}

BIRD_COLORS = {
    VisualMode.NORMAL: arcade.color.YELLOW_ORANGE,
    VisualMode.LAVA:   arcade.color.BLACK,
    VisualMode.OCEAN:  arcade.color.YELLOW_ORANGE,
}

class FlappyGame:
    """Mini-jeu Flappy Bird intégrable dans un panneau Arcade."""

    def __init__(self, width: int, height: int, *, mode: VisualMode = VisualMode.NORMAL):
        # dimensions du panel hôte
        self.panel_w = width
        self.panel_h = height
        # échelle uniforme pour conserver le ratio
        self.scale = min(width / REF_WIDTH, height / REF_HEIGHT)
        self.margin_x = (width  - REF_WIDTH  * self.scale) / 2
        self.margin_y = (height - REF_HEIGHT * self.scale) / 2

        # couleurs selon le mode
        bg, pipe_col   = PALETTES[mode]
        self.background_color = bg
        self.pipe_color       = pipe_col
        self.bird_color       = BIRD_COLORS[mode]
        self.mode = mode

        # vitesse ajustée
        self.pipe_speed   = PIPE_SPEED * (2.5 if mode == VisualMode.LAVA else 1)
        # ajustement physique à l'échelle du panel
        self.gravity       = GRAVITY * self.scale
        self.flap_strength = FLAP_STRENGTH * self.scale
        self.moving_pipes = (mode == VisualMode.OCEAN)

        self._reset()
        self.started = False

    # ----------------------- boucle -----------------------
    def update(self, dt: float):
        if self.game_over or self.victory or not self.started:
            return

        # physique oiseau
        self.bird_velocity -= self.gravity * dt
        self.bird_y        += self.bird_velocity * dt
        if self.bird_y < BIRD_SIZE/2 or self.bird_y > REF_HEIGHT - BIRD_SIZE/2:
            self._end_game(); return

        # tuyaux
        for pipe in list(self.pipes):
            pipe["x"] -= self.pipe_speed * dt
            if self.moving_pipes:
                pipe["gap_y"] += pipe["vel_y"] * dt
                margin = 60 + GAP_HEIGHT//2
                if pipe["gap_y"] > REF_HEIGHT - margin or pipe["gap_y"] < margin:
                    pipe["vel_y"] *= -1
            if not pipe.get("scored") and pipe["x"] + PIPE_WIDTH/2 < BIRD_X:
                pipe["scored"] = True; self.score += 1
        # nettoyage
        self.pipes = [p for p in self.pipes if p["x"] + PIPE_WIDTH/2 > 0]

        # spawn
        self.time_since_last_pipe += dt
        if self.time_since_last_pipe >= PIPE_INTERVAL:
            self._spawn_pipe(); self.time_since_last_pipe = 0

        # collision / victoire
        if self._check_collision(): self._end_game()
        if self.score >= 12: self._win_game()

    # ----------------------- rendu -----------------------
    def draw(self, *, offset_x: float = 0, offset_y: float = 0):
        # fond du panel
        arcade.draw_lrbt_rectangle_filled(
            offset_x, offset_x + self.panel_w,
            offset_y, offset_y + self.panel_h,
            self.background_color,
        )
        s, mx, my = self.scale, self.margin_x, self.margin_y
        sx = lambda x: offset_x + mx + x * s
        sy = lambda y: offset_y + my + y * s

        # oiseau
        arcade.draw_lrbt_rectangle_filled(sx(BIRD_X-BIRD_SIZE/2), sx(BIRD_X+BIRD_SIZE/2),
                                          sy(self.bird_y-BIRD_SIZE/2), sy(self.bird_y+BIRD_SIZE/2),
                                          self.bird_color)
        # tuyaux
        for pipe in self.pipes:
            x = pipe["x"]; gap = pipe["gap_y"]
            bottom_h = gap - GAP_HEIGHT/2
            top_h    = REF_HEIGHT - (gap + GAP_HEIGHT/2)
            arcade.draw_lrbt_rectangle_filled(sx(x-PIPE_WIDTH/2), sx(x+PIPE_WIDTH/2),
                                              sy(0), sy(bottom_h), self.pipe_color)
            arcade.draw_lrbt_rectangle_filled(sx(x-PIPE_WIDTH/2), sx(x+PIPE_WIDTH/2),
                                              sy(REF_HEIGHT-top_h), sy(REF_HEIGHT), self.pipe_color)
        # score
        arcade.draw_text(f"Score : {self.score}", offset_x+20, offset_y+self.panel_h-60,
                         arcade.color.WHITE, FONT_SIZE*self.scale*0.6)
        if self.game_over or self.victory:
            msg = "Vous avez gagné" if self.victory else "Game Over"
            arcade.draw_text(msg, offset_x+self.panel_w/2, offset_y+self.panel_h/2,
                             arcade.color.BLACK, FONT_SIZE*self.scale,
                             anchor_x="center", anchor_y="center")

    # ----------------------- input -----------------------
    def on_key_press(self, key, _mods):
        if self.game_over or self.victory:
            if key == arcade.key.ESCAPE:
                self._reset(); self.started = False
            return
        if key == arcade.key.SPACE:
            if not self.started:
                self.started = True
            self.bird_velocity = self.flap_strength

    # ----------------------- helper interne -----------------------
    def _spawn_pipe(self):
        margin = 60
        gap_center = random.randint(margin+GAP_HEIGHT//2, REF_HEIGHT-margin-GAP_HEIGHT//2)
        vel = PIPE_VERTICAL_SPEED if self.moving_pipes else 0
        self.pipes.append({"x": REF_WIDTH+PIPE_WIDTH/2, "gap_y": gap_center,
                            "vel_y": vel, "scored": False})

    def _check_collision(self) -> bool:
        for p in self.pipes:
            if abs(p["x"]-BIRD_X) < PIPE_WIDTH/2+BIRD_SIZE/2:
                if not (p["gap_y"]-GAP_HEIGHT/2+BIRD_SIZE/2 < self.bird_y < p["gap_y"]+GAP_HEIGHT/2-BIRD_SIZE/2):
                    return True
        return False

    def _end_game(self): self.game_over=True
    def _win_game(self): self.victory=True
    def _reset(self):
        self.bird_y = REF_HEIGHT//2
        self.bird_velocity = 0
        self.pipes = []
        self.time_since_last_pipe = 0
        self.score = 0
        self.game_over = False
        self.victory = False
        self.started = False
