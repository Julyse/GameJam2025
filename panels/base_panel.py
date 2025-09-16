from dataclasses import dataclass
import arcade


@dataclass
class BasePanel:
    x: int
    y: int
    width: int
    height: int
    color: arcade.color
    label: str

    def update(self, delta_time: float) -> None:
        # Méthode à surcharger par chaque panel
        pass

    def draw(self) -> None:
        arcade.draw_lrbt_rectangle_filled(
            self.x,
            self.x + self.width,
            self.y,
            self.y + self.height,
            self.color,
        )
        arcade.draw_text(
            self.label,
            self.x + 20,
            self.y + self.height // 2 - 12,
            arcade.color.WHITE,
            20,
        )

