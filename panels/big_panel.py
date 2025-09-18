from ast import arg
from os import execl, execv
from sys import argv, executable
from .base_panel import BasePanel
from itertools import cycle
from arcade import (
    Sprite,
    SpriteList,
    Texture,
    color,
    draw_text,
    load_texture,
    draw_texture_rect,
    load_animated_gif,
    key
)
from math import cos, pi, sin
from random import random, gauss, uniform, choice, shuffle
from enum import Enum
from enums import dragon_state
from numpy import linspace
from pathlib import Path
from effects import create_explosion_system
from enums.dragon_state import DragonState


class SpriteState(Enum):
    STANDBY = 1
    ATTACKING = 2
    DEFENDING = 3
    DEAD = 4
    FLEEING = 5

SWORD_DURABILITY = 3

class ActionType(Enum):
    DRAGON_ATTACK = "dragon_attack"
    HERO_ATTACK = "hero_attack"

class CombatEncounter:
    """Sequenced combat system with randomized action queue"""
    
    def __init__(self, parent_panel):
        self.panel = parent_panel
        self.reset()
        
    def reset(self):
        """Reset encounter state"""
        self.dragon_hp = 40
        self.hero_hp = 40
        # Max HP used for UI scaling
        self.max_dragon_hp = self.dragon_hp
        self.max_hero_hp = self.hero_hp
        self.running = False
        self.finished = False
        self.result = None  # "victory", "defeat", or None
        
        # Sword inventory system
        self.sword_inventory = [5]  # Start with 1 sword, durability 3
        
        # Random scheduler (no fixed queue)
        self.action_timer = 0.0
        self.action_interval = 1.2  
        self.current_action = None
        self.action_in_progress = False
        self.final_message_timer = 0.0
        self.final_message_delay = 1.0
        
        # Scheduler probabilities
        self.p_dragon = 0.42
        self.p_hero = 0.58
        
    def start_encounter(self):
        """Initialize and start the combat sequence"""
        self.reset()
        self.running = True
        print(f"🎯 Combat started! Dragon HP: {self.dragon_hp}, Hero HP: {self.hero_hp}, Swords: {len(self.sword_inventory)}")
        
    def add_sword(self, count=1):
        """Add sword(s) to inventory - called by mini-games on success"""
        for _ in range(count):
            self.sword_inventory.append(SWORD_DURABILITY)  # Each sword has 3 durability
        print(f"⚔️ Added {count} sword(s)! Total swords: {len(self.sword_inventory)}")
        
    def _has_usable_sword(self):
        """Check if hero has any sword with durability > 0"""
        return len(self.sword_inventory) > 0 and any(durability > 0 for durability in self.sword_inventory)
        
    def _use_sword(self):
        """Use 1 durability from first available sword, remove if depleted"""
        if not self.sword_inventory:
            return False
            
        # Find first sword with durability > 0
        for i, durability in enumerate(self.sword_inventory):
            if durability > 0:
                self.sword_inventory[i] -= 1
                if self.sword_inventory[i] <= 0:
                    # Remove depleted sword
                    self.sword_inventory.pop(i)
                    #print(f"💔 Sword broke! Remaining swords: {len(self.sword_inventory)}")
                    # Sync SwordStacking visual: remove one sword
                    try:
                        ref = getattr(self.panel, "sword_panel_ref", None)
                        game = getattr(ref, "game", None) if ref else None
                        if game and hasattr(game, "remove_sword"):
                            game.remove_sword()
                    except Exception:
                        pass
                return True
        return False
        
    def update_encounter(self, dt):
        """Update combat logic - called from BigPanel.on_update"""
        if not self.running or self.finished:
            return
            
        # Wait for current action to complete
        if self.action_in_progress:
            if not self.panel.attacking:  # Attack animation finished
                self._on_action_complete()
            return
            
        # Timer for next action
        self.action_timer += dt
        if self.action_timer >= self.action_interval:
            self._schedule_next_action()
            
    def _schedule_next_action(self):
        """Randomly choose next actor and execute action"""
        # Choose next actor randomly
        next_actor = self._choose_next_actor()
        
        self.current_action = ActionType.DRAGON_ATTACK if next_actor == "dragon" else ActionType.HERO_ATTACK
        self.action_in_progress = True
        self.action_timer = 0.0
        if self.current_action == ActionType.DRAGON_ATTACK:
            self.action_interval = uniform(3, 4)
        else:
            self.action_interval = uniform(1.5, 2)
        
       # print(f"🎲 Next action: {self.current_action.value}")
        
        if self.current_action == ActionType.DRAGON_ATTACK:
            self._begin_dragon_attack()
        elif self.current_action == ActionType.HERO_ATTACK:
            self._begin_hero_attack()
            
    def _choose_next_actor(self):
        """Returns 'dragon' or 'hero' using randomized logic"""
        # If hero has no swords, force dragon attack
        if not self._has_usable_sword():
            return "dragon"
            
        # Otherwise use probability weights
        return "dragon" if random() < self.p_dragon else "hero"
            
    def _begin_dragon_attack(self):
        """Start dragon fireball attack"""
        # Set dragon to attacking state
        self.panel.d_state = SpriteState.ATTACKING
        
        # Position and fire projectile
        self.panel.fireball.center_x = self.panel.drake.center_x
        self.panel.fireball.center_y = self.panel.drake.center_y
        self.panel.fireball.color = self.panel.breath_color
        
        # Start projectile animation
        self.panel._start_attack_anim(
            self.panel.fireball, 
            self.panel.knight, 
            projectile=True
        )
        
    def _begin_hero_attack(self):
        """Start hero sword attack"""
        # Check if hero has usable sword
        if not self._has_usable_sword():
            print("💥 Hero attack failed - no sword available!")
            # Play failed attack animation or effect
            self.action_in_progress = False  # Skip this action
            return
            
        # Set hero to attacking state and apply animation
        self.panel.k_state = SpriteState.ATTACKING
        self.panel._apply_knight_gif()
        
        # Start sword attack animation
        self.panel._start_attack_anim(
            self.panel.knight, 
            self.panel.drake, 
            stop_before=40.0, 
            projectile=False
        )
    
    def _on_action_complete(self):
        """Called when an attack animation finishes"""
        self.action_in_progress = False
        
        if self.current_action == ActionType.DRAGON_ATTACK:
            self._on_projectile_hit()
        elif self.current_action == ActionType.HERO_ATTACK:
            self._on_hero_strike_hit()
            
        # Return to standby if still alive
        if self.hero_hp > 0 and not self.finished:
            self.panel.k_state = SpriteState.STANDBY
            self.panel._apply_knight_gif()
        if self.dragon_hp > 0 and not self.finished:
            self.panel.d_state = SpriteState.STANDBY
            
    def _on_projectile_hit(self):
        """Handle dragon projectile hitting hero"""
        # Spawn explosion at hero position
        self.panel.spawn_explosion(
            self.panel.knight.center_x + uniform(-15, 15),
            self.panel.knight.center_y + uniform(-15, 15)
        )
        
        # Damage hero
        self.hero_hp -= 1
        print(f"🔥 Dragon hits hero! Hero HP: {self.hero_hp}/{self.max_hero_hp}")
        
        # Check for hero death
        if self.hero_hp <= 0:
            self._on_hero_death()
            
    def _on_hero_strike_hit(self):
        """Handle hero sword hitting dragon"""
        # Use sword durability
        if not self._use_sword():
            print("💥 Hero attack failed - no sword durability!")
            return
            
        # Damage dragon
        self.dragon_hp -= 1
        print(f"⚔️ Hero strikes dragon! Dragon HP: {self.dragon_hp}/{self.max_dragon_hp}, Swords: {len(self.sword_inventory)}")
        
        # Check for dragon death
        if self.dragon_hp <= 0:
            self._on_dragon_death()
        # Check if hero has no more swords and dragon still alive
        elif not self._has_usable_sword() and self.dragon_hp > 0:
            print("💔 Hero has no more swords - defeat!")
            self.panel.k_state = SpriteState.DEAD
            self.panel._apply_knight_gif()
            
            self._end_encounter("defeat_sword")

    def _on_hero_death(self):
        """Handle hero death"""
        print("💀 Hero has fallen!")
        
        # Set hero to dead state and keep on ground
        self.panel.k_state = SpriteState.DEAD
        self.panel._apply_knight_gif()
        
        self._end_encounter("defeat")
        
    def _on_dragon_death(self):
        """Handle dragon death"""
        print("🏆 Dragon defeated!")
        
        # Set dragon to defeated state
        self.panel.d_state = SpriteState.DEAD
        
        self._end_encounter("victory")
        
    def _end_encounter(self, result):
        """End the encounter with given result"""
        self.result = result
        self.running = False
        self.action_in_progress = False
        
        # Clear any remaining attacks
        if self.panel.attacking:
            self.panel._end_attack_anim()
        
        # Stop minigames (SmallPanel2) when combat ends
        try:
            ref = getattr(self.panel, "minigames_panel_ref", None)
            if ref and hasattr(ref, "disable_minigames"):
                ref.disable_minigames()
        except Exception:
            pass
        
        # Start final message timer
        self.final_message_timer = 0.0
        
    def update_final_message(self, dt):
        """Update final message timer"""
        if self.result and not self.finished:
            self.final_message_timer += dt
            if self.final_message_timer >= self.final_message_delay:
                self.finished = True
                
    def draw_hud(self, panel):
        """Draw HP bars and combat info"""
        
        # Texte des épées masqué à la demande

        # Texte d'état de combat masqué à la demande
                     
    def draw_final_messages(self, panel):
        """Draw victory/defeat messages"""
        if not self.finished:
            return
            
        center_x = panel.left + panel.width // 2
        center_y = panel.bottom + panel.height // 2
        
        if self.result == "defeat":
            draw_text("GAME OVER", center_x, center_y,
                     color.RED, 48, anchor_x="center", anchor_y="center",
                     font_name=("Righteous", "arial", "calibri"))
            draw_text("La bataille est perdue...", center_x, center_y - 60,
                     color.RED, 18, anchor_x="center", anchor_y="center",
                     font_name=("Righteous", "arial", "calibri"))

        elif self.result == "defeat_sword":
            draw_text("GAME OVER", center_x, center_y,
                     color.RED, 48, anchor_x="center", anchor_y="center",
                     font_name=("Righteous", "arial", "calibri"))
            draw_text("Vous n'avez pas fabrique assez d'epee", center_x, center_y - 60,
                     color.RED, 18, anchor_x="center", anchor_y="center",
                     font_name=("Righteous", "arial", "calibri"))

        elif self.result == "victory":
            draw_text("VICTORY", center_x, center_y,
                     color.GREEN, 48, anchor_x="center", anchor_y="center", 
                     font_name=("Righteous", "arial", "calibri"))
            draw_text("Le dragon est vaincu !", center_x, center_y - 60,
                     color.GREEN, 18, anchor_x="center", anchor_y="center",
                     font_name=("Righteous", "arial", "calibri"))

        if "defeat" in str(self.result): # ADD DEFEAT SWORD!!
            draw_text("PRESS ESCAPE TO RESTART", center_x, center_y - 120,
                     color.RED, 20, anchor_x="center", anchor_y="center", font_name=("Righteous", "arial", "calibri"))
class Character(Sprite):
    def update(self, delta_time: float = 1 / 60, p_x=0, p_y=0, *args, **kwargs) -> None:
        self.center_x -= p_x
        self.center_y -= p_y


class BigPanel(BasePanel):
    def __init__(self, x: int, y: int, width: int, height: int, *, combat_mode: DragonState = DragonState.NORMAL):

        super().__init__(x=x, y=y, width=width, height=height, color=color.BEIGE, label="")  # type: ignore
        
        self.state_cycle= cycle(DragonState)
        self.state_timer= 0.0 
        self.state_interval= 15
        self.combat_mode = combat_mode
        self._setup_mode_visuals()

        self.sprites = SpriteList()
        self.knight = Character()
        self.drake = Character(
            path_or_texture=Path(__file__).parent.parent / "resources" / "drake.png"
        )
        self.sword = Sprite()
        
        self.fireball = Character(path_or_texture=Path(__file__).parent.parent / "resources" / "fire1.gif")
        self.fireball.append_texture(load_texture(Path(__file__).parent.parent / "resources" / "fire2_1.gif"))

        center_x = self.width / 2 + x
        base_y = self.bottom + 200  # position verticale fixe, bas du panel

        padding = 295.0  # écart horizontal fixe

        self.knight.position = (center_x - padding, base_y)
        self.drake.position = (center_x + padding, base_y - 55)

        self.fireball.position = (self.drake.center_x, self.drake.center_y)
        self.fireball.multiply_scale(1.25)
        self.fireball.angle = 90.0
        self.fireball.color = color.TRANSPARENT_BLACK

        self.knight_ipos = (self.knight.center_x, self.knight.center_y)
        self.drake_ipos = (self.drake.center_x, self.drake.center_y)

        self.sword.position = (center_x - padding + 100, base_y + 20)

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

        self.d_healthbar = Sprite()
        self.k_healthbar = Sprite()
        self._healthbar = [x for x in (Path(__file__).parent.parent / "resources" / "Healthbar").iterdir()]
        self._healthbar.sort()
        self._healthbar.reverse()

        self.max_k_lives = self.k_lives
        self.max_d_lives = self.d_lives

        for g in self._healthbar:
            tex = load_texture(g)
            self.d_healthbar.textures.append(tex)
            self.k_healthbar.textures.append(tex)

        self.d_healthbar.position = (float(self.width - self.width / 4), self.height - 175)        
        self.k_healthbar.position = (float(self.width / 4), self.height - 175 )        

        self.k_healthbar.multiply_scale(1.5)
        self.d_healthbar.multiply_scale(1.5)

        self.k_healthbar.set_texture(len(self.k_healthbar.textures) - 1)
        self.d_healthbar.set_texture(len(self.d_healthbar.textures) - 1)

        self._init_knight_gifs()
        self.bg_tex = load_texture(
            Path(__file__).parent.parent / "resources" / "main_bg.png"
        )

        self.n_dec = 20

        x_normal = [gauss(self.width / 2, self.width / 2) for _ in range(self.n_dec)]
        y_normal = linspace(0, self.width, self.n_dec)

        self.decorations = SpriteList()
        self.bats = SpriteList()

        decorations_text = [x for x in (Path(__file__).parent.parent / "resources" / "Props").iterdir() if x.name != "misc_scenery.png"]
        bats_text = [x for x in (Path(__file__).parent.parent / "resources" / "Entities" / "Bats").iterdir()]
        
        for i in range(int(self.n_dec)):
            dec = Sprite(path_or_texture=choice(decorations_text))
            dec.angle = 2 * pi * random()
            dec.position = (self.left + x_normal[i], self.window.height - self.height + 20)
            self.decorations.append(dec)

        for i in range(int(self.n_dec / 2)):
            dec = Sprite(path_or_texture=choice(bats_text))
            dec.angle = 2 * pi * random()
            dec.scale = uniform(1.25, 2.1)
            dec.base_x = self.left + x_normal[int(i + self.n_dec / 2)]
            dec.base_y = self.bottom + y_normal[int(i + self.n_dec / 2)]
            dec.freq_x = uniform(0.5, 1.5)
            dec.freq_y = uniform(0.5, 1.5)
            dec.phase_x = uniform(0, 2 * pi)
            dec.phase_y = uniform(0, 2 * pi)
            dec.center_x, dec.center_y = dec.base_x, dec.base_y
            self.bats.append(dec)

        self.sprites.append(self.drake)
        self.sprites.append(self.fireball)
        self.sprites.append(self.d_healthbar)
        self.sprites.append(self.k_healthbar)

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
            default_scale=2.3,
        )
        # Nombre d'étapes pour le déplacement des projectiles (plus grand = plus lent)
        self.fireball_steps = 24
        
        # Combat encounter system
        self.encounter = CombatEncounter(self)
        # Auto-start combat after a brief delay
        self.encounter_start_timer = 2.0  # Start combat after 2 seconds
        # Reference to SwordStacking (SmallPanel3); set by controller
        
        self.sword_panel_ref = None
    def _setup_mode_visuals(self):
        """Configure visual elements based on combat mode."""
        match self.combat_mode:
            case DragonState.NORMAL:
                self.breath_color = color.RED
                self.bg_tint = None
            case DragonState.FIRE:
                self.breath_color = color.DARK_RED
                self.bg_tint = (255, 140, 0, 40)  # Fire tint (orange)
            case DragonState.ICE:
                self.breath_color = color.SKY_BLUE
                self.bg_tint = (0, 100, 200, 40)  # Ice tint (blue)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.ESCAPE and "defeat" in str(self.encounter.result):
            execl(executable, executable, * argv)

    def set_combat_mode(self, mode: DragonState):
        """Change combat mode without resetting fight state (HP, timers, etc.)"""
        self.combat_mode = mode
        self._setup_mode_visuals()
        # Update projectile color if it exists
        if hasattr(self, 'fireball') and self.fireball:
            self.fireball.color = self.breath_color
        
    def on_draw(self) -> None:
        super().on_draw()
        draw_text("Arena", self.left + 20, self.bottom + 20, color.BLACK, font_name=("Righteous", "arial", "calibri"))
        draw_texture_rect(self.bg_tex, self.rect)
        
        # Apply mode-specific background tint
        if self.bg_tint is not None:
            from arcade import draw_lrbt_rectangle_filled
            draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, self.bg_tint)
        
        # Mise à jour des barres de vie basée sur le système de combat (ratio actuel / max)
        k_ratio = (self.encounter.hero_hp / max(1, self.encounter.max_hero_hp)) if hasattr(self.encounter, 'max_hero_hp') else 1.0
        d_ratio = (self.encounter.dragon_hp / max(1, self.encounter.max_dragon_hp)) if hasattr(self.encounter, 'max_dragon_hp') else 1.0
        # Utiliser un arrondi vers le haut pour éviter une barre vide lorsque les PV > 0
        from math import ceil
        k_index = int(ceil(k_ratio * (len(self.k_healthbar.textures) - 1))) if k_ratio > 0 else 0
        d_index = int(ceil(d_ratio * (len(self.d_healthbar.textures) - 1))) if d_ratio > 0 else 0
        k_index = max(0, min(k_index, len(self.k_healthbar.textures) - 1))
        d_index = max(0, min(d_index, len(self.d_healthbar.textures) - 1))
        self.k_healthbar.set_texture(k_index)
        self.d_healthbar.set_texture(d_index)

        self.decorations.draw()
        self.bats.draw()
        self.sprites.draw()
        
        # Dessiner les explosions
        self.draw_explosions()

        # Draw combat encounter HUD and messages
        self.encounter.draw_hud(self)
        self.encounter.draw_final_messages(self)

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
        steps = self.fireball_steps if projectile else 12
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
        # L'explosion est gérée dans _on_projectile_hit
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
        # Ne pas repasser à STANDBY si le personnage est mort dans l'Encounter
        try:
            if getattr(self, 'encounter', None):
                if self.encounter.hero_hp > 0:
                    self.k_state = SpriteState.STANDBY
                if self.encounter.dragon_hp > 0:
                    self.d_state = SpriteState.STANDBY
        except Exception:
            # Fallback sur l'ancienne logique si jamais l'encounter n'est pas disponible
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
        
        # Auto-start combat encounter
        if self.encounter_start_timer > 0:
            self.encounter_start_timer -= delta_time
            if self.encounter_start_timer <= 0:
                self.encounter.start_encounter()
        
        # Update combat encounter
        self.encounter.update_encounter(delta_time)
        self.encounter.update_final_message(delta_time)
        
        self.state_timer += delta_time 
        if self.state_timer >= self.state_interval : # cycle dragon state very state_interval seconds 
            self.state_timer = 0 
            self.set_combat_mode(next(self.state_cycle))
            print("Next state ", self.combat_mode)

            

        for bat in self.bats:
            offset_x = sin(self.dt * bat.freq_x + bat.phase_x) * 5
            offset_y = cos(self.dt * bat.freq_y + bat.phase_y) * 3
            new_x = bat.base_x + offset_x
            new_y = bat.base_y + offset_y
            new_x = min(max(new_x, self.left), self.right)
            new_y = min(max(new_y, self.bottom), self.top)
            bat.center_x, bat.center_y = new_x, new_y

        # Handle attack animations
        if self.attacking:
            self._tick_attack_anim()

        # Update knight animations
        self._sync_knight_gif_pos()
        # Ne pas forcer de mise à jour d'animation continue sur l'état DEATH pour éviter une boucle gênante
        if self.k_state != SpriteState.DEAD:
            if self.k_state in self.k_gifs and self.k_gifs[self.k_state].visible:
                self.k_gifs[self.k_state].update_animation(delta_time)

