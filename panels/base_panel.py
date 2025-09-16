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
    speed: float = 1.0

    # runtime
    incrementer: float = 0.0

    def update(self, delta_time: float) -> None:
        self.incrementer += self.speed * delta_time

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
        arcade.draw_text(
            f"{self.incrementer:.2f}",
            self.x + 20,
            self.y + 12,
            arcade.color.WHITE,
            16,
        )

