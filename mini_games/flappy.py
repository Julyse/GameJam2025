import arcade
import os
import random
from enum import Enum
from pathlib import Path
from typing import Callable, Optional
from enums.dragon_state import DragonState
from enums.minigames_status import GameStatus

# ---------- Dimensions de référence (monde logique) ----------
REF_WIDTH  = 1280
REF_HEIGHT = 720

#  Y'a toutes les Constantes du jeu au début si tu veux changer fait le ici ---------- 
BIRD_X        = REF_WIDTH * 0.25
BIRD_SIZE     = 35
GRAVITY       = 2400
FLAP_STRENGTH = 700

PIPE_WIDTH         = 100
GAP_HEIGHT         = 230
PIPE_SPEED         = 320
PIPE_INTERVAL      = 1.2
PIPE_VERTICAL_SPEED = 45

FONT_SIZE = 36

PALETTES = {
    DragonState.NORMAL: (arcade.color.SKY_BLUE, arcade.color.WHITE),
    DragonState.FIRE:   (arcade.color.DARK_TANGERINE, arcade.color.DARK_RED),
    DragonState.ICE:    (arcade.color.SEA_BLUE, arcade.color.DARK_BLUE),
}

class FlappyGame:
    """Mini-jeu Flappy Bird intégrable dans un panneau Arcade."""

    def __init__(self, width: int, height: int, mode: DragonState = DragonState.NORMAL, on_finish: Optional[Callable[[GameStatus], None]] = None):
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
        self.bird_color       = arcade.color.WHITE
        self.mode = mode
        self.on_finish = on_finish
        self.finished = False

        # Gamemode pour correspondre à DragonState
        if mode == DragonState.FIRE:
            self.gamemode = DragonState.FIRE
        elif mode == DragonState.ICE:
            self.gamemode = DragonState.ICE
        else:
            self.gamemode = DragonState.NORMAL

        # --- Background selon le mode ---
        RESOURCE_PATH = Path(__file__).resolve().parents[1] / "ressources" / "images"
        match self.gamemode:
            case DragonState.NORMAL:
                self.background = arcade.load_texture(str(RESOURCE_PATH / "bg.png"))
            case DragonState.FIRE:
                self.background = arcade.load_texture(str(RESOURCE_PATH / "bg_fire.png"))
            case DragonState.ICE:
                self.background = arcade.load_texture(str(RESOURCE_PATH / "bg_ice.png"))

        # vitesse ajustée par mode
        if mode == DragonState.FIRE:
            self.pipe_speed = PIPE_SPEED * 3.0
        elif mode == DragonState.NORMAL:
            self.pipe_speed = PIPE_SPEED * 1.0
        else:  # DragonState.ICE
            self.pipe_speed = PIPE_SPEED * 1.0

        # cadence de spawn des tuyaux par mode
        self.pipe_interval = 0.9 if mode == DragonState.FIRE else PIPE_INTERVAL

        # vitesse verticale des tuyaux mobiles (utilisé seulement en ICE)
        self.pipe_vertical_speed = PIPE_VERTICAL_SPEED * (1.5 if mode == DragonState.ICE else 1.0)

        # ajustement physique à l'échelle du panel
        self.gravity       = GRAVITY * self.scale
        self.flap_strength = FLAP_STRENGTH * self.scale
        self.moving_pipes = (mode == DragonState.ICE)

        self._reset()
        self.started = False

    # ----------------------- boucle -----------------------
    def update(self, dt: float):
        if self.finished or self.game_over or self.victory or not self.started:
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
        if self.time_since_last_pipe >= self.pipe_interval:
            self._spawn_pipe(); self.time_since_last_pipe = 0

        # collision / victoire
        if self._check_collision(): self._end_game()
        if self.score >= 8: self._win_game()

    # ----------------------- rendu -----------------------
    def draw(self, *, offset_x: float = 0, offset_y: float = 0):
        # fond du panel via draw_texture_rect + LBWH
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(offset_x, offset_y, self.panel_w, self.panel_h),
        )
        s, mx, my = self.scale, self.margin_x, self.margin_y
        sx = lambda x: offset_x + mx + x * s
        sy = lambda y: offset_y + my + y * s

        # oiseau (carré simple pour le moment)
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
        # arcade.draw_text(f"Score : {self.score}", offset_x+20, offset_y+self.panel_h-60,
        #                  arcade.color.WHITE, FONT_SIZE*self.scale*0.6)
        # if self.game_over or self.victory:
        #     msg = "Vous avez gagné" if self.victory else "Game Over"
        #     arcade.draw_text(msg, offset_x+self.panel_w/2, offset_y+self.panel_h/2,
        #                      arcade.color.BLACK, FONT_SIZE*self.scale,
        #                      anchor_x="center", anchor_y="center")

        if not self.started:
            text = "Appuyer sur espace"
            arcade.draw_text(
                text,
                self.panel_w / 2 + offset_x,  # X center
                self.panel_h / 2 + offset_y,  # Y center
                arcade.color.GRAY,
                font_size=14,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

  
    def on_key_press(self, key, _mods):
        if self.game_over or self.victory:
            if key == arcade.key.ESCAPE:
                self._reset(); self.started = False
            return
        if key == arcade.key.SPACE:
            if not self.started:
                self.started = True
            self.bird_velocity = self.flap_strength

    def on_key_release(self, key, modifiers):
        pass

    # ----------------------- helper interne -----------------------
    def _spawn_pipe(self):
        margin = 60
        gap_center = random.randint(margin+GAP_HEIGHT//2, REF_HEIGHT-margin-GAP_HEIGHT//2)
        vel = self.pipe_vertical_speed if self.moving_pipes else 0
        self.pipes.append({"x": REF_WIDTH+PIPE_WIDTH/2, "gap_y": gap_center,
                            "vel_y": vel, "scored": False})

    def _check_collision(self) -> bool:
        for p in self.pipes:
            if abs(p["x"]-BIRD_X) < PIPE_WIDTH/2+BIRD_SIZE/2:
                if not (p["gap_y"]-GAP_HEIGHT/2+BIRD_SIZE/2 < self.bird_y < p["gap_y"]+GAP_HEIGHT/2-BIRD_SIZE/2):
                    return True
        return False

    def _end_game(self):
        if not self.finished:
            self.game_over = True
            self.finish(GameStatus.LOST)

    def _win_game(self):
        if not self.finished:
            self.victory = True
            self.finish(GameStatus.WIN)
    def _reset(self):
        self.bird_y = REF_HEIGHT//2
        self.bird_velocity = 0
        self.pipes = []
        self.time_since_last_pipe = 0
        self.score = 0
        self.game_over = False
        self.victory = False
        self.started = False
        self.finished = False

    def finish(self, status: GameStatus):
        """Marquer la fin du mini-jeu et notifier sans fermer la fenêtre."""
        if self.finished:
            return
        self.finished = True
        self.started = False
        try:
            if self.on_finish is not None:
                self.on_finish(status)
        except Exception as exc:
            print(f"Error in Flappy on_finish callback: {exc}")
