from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from arcade import Sprite, SpriteList, load_texture


def _load_explosion_textures(base_dir: Path) -> list:
    # Charge tous les PNG du dossier dans l'ordre alphabétique
    if not base_dir.exists() or not base_dir.is_dir():
        return []
    files = sorted([p for p in base_dir.iterdir() if p.suffix.lower() == ".png"])
    if not files:
        return []
    return [load_texture(p) for p in files]


def create_explosion_system(
    explosions_dir: Path,
    *,
    frame_step: int = 1,
    default_scale: float = 1.0,
) -> tuple[SpriteList, Callable[[float, float, float | None], None], Callable[[float], None], Callable[[], None]]:
    """
    Crée un système d'explosions basé sur une SpriteList et une animation image-par-image.

    API publique (seule fonction exposée par le module):
      - retourne: (sprite_list, spawn(x, y), update(dt), draw())

    Paramètres:
      - explosions_dir: répertoire contenant les PNG d'animation (ex: resources/Explosion/X_Plosion)
      - frame_step: pas d'incrément des frames (1 = normal, 2 = jouer 2 images à la fois)
    """

    textures = _load_explosion_textures(explosions_dir)
    sprite_list: SpriteList = SpriteList()

    class Explosion(Sprite):
        def __init__(self, frames: list):
            super().__init__()
            self._frames: list = frames
            self._frame_index: int = 0
            self.texture = self._frames[0] if self._frames else None
            self._time_acc: float = 0.0
            self._frame_time: float = 0.04  # 25 FPS

        def advance(self, dt: float) -> None:
            if not self._frames:
                self.remove_from_sprite_lists()
                return
            self._time_acc += dt
            while self._time_acc >= self._frame_time:
                self._time_acc -= self._frame_time
                self._frame_index += max(1, int(frame_step))
                if self._frame_index >= len(self._frames):
                    self.remove_from_sprite_lists()
                    return
                self.texture = self._frames[self._frame_index]

    def spawn(x: float, y: float, scale: float | None = None) -> None:
        # Si aucune texture n'est disponible, ne rien faire (évite TypeError)
        if not textures:
            return
        exp = Explosion(textures)
        exp.center_x, exp.center_y = x, y
        exp.scale = float(scale) if scale is not None else float(default_scale)
        sprite_list.append(exp)

    def update(dt: float) -> None:
        for s in list(sprite_list):
            if isinstance(s, Explosion):
                s.advance(dt)

    def draw() -> None:
        sprite_list.draw()

    return sprite_list, spawn, update, draw


