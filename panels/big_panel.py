from .base_panel import BasePanel
from arcade import (
    Sprite,
    SpriteList,
    Texture,
    color,
    draw_text,
    load_texture,
    draw_texture_rect,
    load_animated_gif,
)
from math import cos, pi, sin
from random import random, gauss, uniform, choice
from enum import Enum
from numpy import linspace
from pathlib import Path
from effects import create_explosion_system


class SpriteState(Enum):
    STANDBY = 1
    ATTACKING = 2
    DEFENDING = 3
    DEAD = 4
    FLEEING = 5


class Character(Sprite):
    def update(self, delta_time: float = 1 / 60, p_x=0, p_y=0, *args, **kwargs) -> None:
        self.center_x -= p_x
        self.center_y -= p_y


class BigPanel(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int):

        super().__init__(x=x, y=y, width=width, height=height, color=color.BEIGE, label="")  # type: ignore

        self.sprites = SpriteList()
        self.knight = Character()
        self.drake = Character(
            path_or_texture=Path(__file__).parent.parent / "resources" / "drake.png"
        )
        self.sword = Sprite()
        
        self.fireball = Character(path_or_texture=Path(__file__).parent.parent / "resources" / "fire1.gif")
        self.fireball.append_texture(load_texture(Path(__file__).parent.parent / "resources" / "fire2_1.gif"))

        center_x = self.width / 2 + x
        center_y = self.height / 2 + y

        padding = uniform(200, 350)

        self.knight.position = (center_x - padding, center_y)
        self.drake.position = (center_x + padding, center_y)

        self.fireball.position = (self.drake.center_x, self.drake.center_y)
        self.fireball.multiply_scale(1.25)
        self.fireball.angle = 90.0
        self.fireball.color = color.TRANSPARENT_BLACK

        self.knight_ipos = (self.knight.center_x, self.knight.center_y)
        self.drake_ipos = (self.drake.center_x, self.drake.center_y)

        self.sword.position = (center_x - padding + 100, center_y + 20)

        self.drake.texture = self.drake.texture.flip_horizontally()

        self.k_state = SpriteState.STANDBY
        self.d_state = SpriteState.STANDBY
        self.s_state = SpriteState.STANDBY

        self.k_lives = 5
        self.d_lives = 10
        self.s_lives = 4
        self.s_strength = 1

        self.sword.width /= 4
        self.drake.multiply_scale(2)
        self.sword.angle = 40

        self._init_knight_gifs()
        self.bg_tex = load_texture(
            Path(__file__).parent.parent / "resources" / "main_bg.png"
        )

        self.n_dec = 20

        x_normal = [gauss(self.width / 2, self.width / 2) for _ in range(self.n_dec)]
        #y_normal = [gauss(self.height / 3, self.height / 2) for _ in range(self.n_dec)]
        y_normal = linspace(0, self.width, self.n_dec)

        self.decorations = SpriteList()
        self.bats = SpriteList()

        decorations_text = [x for x in (Path(__file__).parent.parent / "resources" / "Props").iterdir() if x.name != "misc_scenery.png"]
        bats_text = [x for x in (Path(__file__).parent.parent / "resources" / "Entities" / "Bats").iterdir()]
        print(decorations_text)

        for i in range(int(self.n_dec)):
            dec = Sprite(path_or_texture=choice(decorations_text))
            dec.angle = 2 * pi * random()
            dec.position = (self.left + x_normal[i], self.window.height - self.height + 20)
            self.decorations.append(dec)

        for i in range(int(self.n_dec / 2)):
            dec = Sprite(path_or_texture=choice(bats_text))
            dec.angle = 2 * pi * random()
            dec.scale = uniform(1.25, 2.1)
            dec.position = (self.left + x_normal[int(i + self.n_dec / 2)], self.bottom + y_normal[int(i + self.n_dec / 2)])
            self.bats.append(dec)
        

        self.sprites.append(self.drake)
        self.sprites.append(self.fireball)

        self.dt = 0.0
        self.curr = 0
        self.attacking = False
        self.attack_actor: Sprite | None = None
        self.attack_path: list[tuple[float, float]] = []
        self.attack_actor_start: tuple[float, float] | None = None
        self._attack_is_projectile = False

        # Explosions (animation PNGs dans resources/Explosion/X_Plosion)
        self.explosions, self.spawn_explosion, self.update_explosions, self.draw_explosions = create_explosion_system(
            Path(__file__).parent.parent / "resources" / "Explosion" / "X_plosion" / "PNG",
            frame_step=2,
        )
        # Debug: activer pour jouer des explosions aléatoires
        self.debug_explosions = False

    def on_draw(self) -> None:
        super().on_draw()
        draw_text("Arena", self.left + 20, self.bottom + 20, color.BLACK, font_name=("Righteous", "arial", "calibri"))
        draw_texture_rect(self.bg_tex, self.rect)

        self.decorations.draw()
        self.bats.draw()
        self.sprites.draw()
        # Dessiner les explosions
        self.draw_explosions()

        msg_x = self.left + self.width / 2 - 80
        msg_y = self.bottom + self.height - 40

        if self.s_lives <= 0:
            draw_text("The sword is broken!", msg_x, msg_y, color.RED, 16)
            self.knight.set_texture(1)
            msg_y -= 25
        if self.k_lives <= 0 or self.k_state == SpriteState.DEAD:
            draw_text("The knight is dead!", msg_x, msg_y, color.RED, 16)
            msg_y -= 25
        if self.d_lives <= 0 or self.d_state == SpriteState.DEAD:
            draw_text("The drake is dead!", msg_x, msg_y, color.RED, 16)

    def set_ball_type(type: any): # type: ignore
        pass

    def _init_knight_gifs(self) -> None:
        base = (
            Path(__file__).parent.parent
            / "resources/knight/Colour1/Outline/120x80_gifs"
        )

        L = lambda n: load_animated_gif(base / n)

        self.k_gifs = {
            SpriteState.STANDBY: L("__Idle.gif"),
            SpriteState.ATTACKING: L("__Attack.gif"),
            SpriteState.DEFENDING: L("__DeathNoMovement.gif"),
            SpriteState.FLEEING: L("__Run.gif"),
            SpriteState.DEAD: L("__Death.gif"),
        }
        for g in self.k_gifs.values():
            g.multiply_scale(4)

            g.center_x, g.center_y = self.knight.center_x, self.knight.center_y
            g.visible = False

            self.sprites.append(g)
        self._apply_knight_gif()

    def _apply_knight_gif(self) -> None:
        for g in self.k_gifs.values():
            g.visible = False
        self.k_gifs[self.k_state].visible = True

    def _sync_knight_gif_pos(self) -> None:
        for g in self.k_gifs.values():
            g.center_x, g.center_y = self.knight.center_x, self.knight.center_y

    def _start_attack_anim(
        self,
        attacker: Sprite,
        defender: Sprite,
        *,
        stop_before: float = 40.0,
        projectile: bool = False,
    ) -> None:
        ax, ay = attacker.center_x, attacker.center_y
        dx, dy = defender.center_x, defender.center_y
        vx, vy = dx - ax, dy - ay
        dist = max((vx * vx + vy * vy) ** 0.5, 1e-6)
        if projectile:
            tip_x, tip_y = dx, dy
        else:
            tip_x = dx - vx / dist * stop_before
            tip_y = dy - vy / dist * stop_before
        steps = 12
        fxs = linspace(ax, tip_x, steps)
        fys = linspace(ay, tip_y, steps)
        if projectile:
            # Projectile: uniquement l'aller, pas de retour
            self.attack_path = [(x, y) for x, y in zip(fxs, fys)]
        else:
            # Corps-à-corps: aller-retour
            bxs = linspace(tip_x, ax, steps)[1:]
            bys = linspace(tip_y, ay, steps)[1:]
            self.attack_path = [(x, y) for x, y in zip(fxs, fys)] + [
                (x, y) for x, y in zip(bxs, bys)
            ]
        self.attack_actor = attacker
        self.attack_actor_start = (ax, ay)
        self.attacking = True
        self._attack_is_projectile = projectile

    def _end_attack_anim(self) -> None:
        # Pour les projectiles, on capture la dernière position avant tout reset
        last_fx = None
        last_fy = None
        if self._attack_is_projectile and self.attack_actor is not None:
            last_fx = self.attack_actor.center_x
            last_fy = self.attack_actor.center_y
        if self._attack_is_projectile and last_fx is not None and last_fy is not None:
            # Explosion au point d'impact (dernière position atteinte)
            self.spawn_explosion(last_fx, last_fy)
        if self.attack_actor and self.attack_actor_start:
            self.attack_actor.center_x, self.attack_actor.center_y = (
                self.attack_actor_start
            )
        if self._attack_is_projectile:
            self.fireball.color = color.TRANSPARENT_BLACK
            self.fireball.center_x, self.fireball.center_y = (
                self.drake.center_x,
                self.drake.center_y,
            )
        self.attacking = False
        self._attack_is_projectile = False
        self.attack_actor = None
        self.attack_actor_start = None
        if self.k_lives > 0:
            self.k_state = SpriteState.STANDBY
        if self.d_lives > 0:
            self.d_state = SpriteState.STANDBY
        self._apply_knight_gif()

    def _tick_attack_anim(self) -> None:
        if not self.attacking or not self.attack_actor:
            return
        if not self.attack_path:
            self._end_attack_anim()
            return
        nx, ny = self.attack_path.pop(0)
        self.attack_actor.center_x = nx
        self.attack_actor.center_y = ny

    def on_update(self, delta_time: float) -> None:
        self.dt += delta_time

        # Mettre à jour les explosions
        self.update_explosions(delta_time)
        # Debug: explosions aléatoires
        if self.debug_explosions and random() < 0.01:
            self.spawn_explosion(uniform(self.left, self.right), uniform(self.bottom, self.top))

        if self.s_lives <= 0 or self.k_lives <= 0 or self.d_lives <= 0:
            if self.attacking and self._attack_is_projectile:
                self._end_attack_anim()
            if self.k_lives <= 0:
                self.k_state = SpriteState.DEAD
                self._apply_knight_gif()
            self._sync_knight_gif_pos()
            if self.k_state in self.k_gifs and self.k_gifs[self.k_state].visible:
                self.k_gifs[self.k_state].update_animation(delta_time)
            return


            # randomly shuffle positions of the decoration
        if random() < .4:
            for dec in self.bats:
                base_x, base_y = dec.position
                offset_x = (
                    sin(self.dt * uniform(0.5, 1.5) + uniform(0, 2 * pi)) * 5
                )
                offset_y = (
                    cos(self.dt * uniform(0.5, 1.5) + uniform(0, 2 * pi)) * 3
                )
                new_x = base_x + offset_x
                new_y = base_y + offset_y
                new_x = min(max(new_x, self.left), self.right)
                new_y = min(max(new_y, self.bottom), self.top)
                dec.center_x, dec.center_y = new_x, new_y

        if self.attacking:
            self._tick_attack_anim()
        else:
            if self.dt > 1.5:
                self.act()
                self.dt = 0.0

        self._sync_knight_gif_pos()
        if self.k_state in self.k_gifs and self.k_gifs[self.k_state].visible:
            self.k_gifs[self.k_state].update_animation(delta_time)

        # Draw life bar
        

    def act(self):
        if self.k_lives <= 0:
            self.k_state = SpriteState.DEAD
        if self.d_lives <= 0:
            self.d_state = SpriteState.DEAD
        if self.k_state == SpriteState.DEAD or self.d_state == SpriteState.DEAD:
            self._apply_knight_gif()
            return
        sprites = [self.knight, self.drake]
        curr_sprite = sprites[self.curr]
        curr_state = self.k_state if curr_sprite is self.knight else self.d_state
        choices = [s for s in SpriteState if s not in (curr_state, SpriteState.DEAD)]
        n_state = choice(choices) if choices else SpriteState.STANDBY
        match n_state:
            case SpriteState.STANDBY:
                pass
            case SpriteState.ATTACKING:
                if curr_sprite is self.knight:
                    self.d_lives = max(0, self.d_lives - self.s_strength)
                    self.s_lives = max(0, self.s_lives - 1)
                    self._start_attack_anim(
                        self.knight, self.drake, stop_before=40.0, projectile=False
                    )
                    self.k_state = SpriteState.ATTACKING
                    self._apply_knight_gif()
                else:
                    self.fireball.center_x, self.fireball.center_y = (
                        self.drake.center_x,
                        self.drake.center_y,
                    )
                    # L'explosion sera jouée à l'impact (voir _end_attack_anim)
                    self.fireball.color = color.RED
                    self.k_lives = max(0, self.k_lives - 1)
                    self._start_attack_anim(self.fireball, self.knight, projectile=True)
                    self.d_state = SpriteState.ATTACKING
            case SpriteState.DEFENDING:
                if random() > 0.33:
                    if curr_sprite is self.knight:
                        self.k_lives = max(0, self.k_lives - 1)
                    else:
                        self.d_lives = max(0, self.d_lives - 1)
                if curr_sprite is self.knight:
                    self.k_state = SpriteState.DEFENDING
                    self._apply_knight_gif()
            case SpriteState.FLEEING:
                step = 25
                if curr_sprite is self.knight:
                    self.knight.center_x -= step
                    self.k_state = SpriteState.FLEEING
                    self._apply_knight_gif()
                else:
                    self.drake.center_x += step
            case _:
                pass
        if n_state != SpriteState.ATTACKING and curr_sprite is self.knight:
            self.k_state = n_state
            self._apply_knight_gif()
        elif n_state != SpriteState.ATTACKING and curr_sprite is self.drake:
            self.d_state = n_state
        self.curr ^= 1
