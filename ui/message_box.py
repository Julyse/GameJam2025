import os
import arcade


class MessageBox:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        *,  # les paramètres suivants sont optionnels
        characters_per_second: float = 20.0,
        font_path: str | None = None,
        font_name: str = "Righteous",
        font_size: int = 14,
        padding: int = 16,
        background_color: arcade.color = arcade.color.DARK_SLATE_GRAY,
        border_color: arcade.color = arcade.color.LIGHT_GRAY,
        text_color: arcade.color = arcade.color.WHITE,
        border_width: int = 2,
        corner_radius: int = 8,
        background_texture_path: str | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.full_text = text
        self.visible_count = 0
        self.characters_per_second = characters_per_second
        self._accumulator = 0.0

        self.padding = padding
        self.background_color = background_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_width = border_width
        self.corner_radius = corner_radius
        self._background_texture = None

        self.font_size = font_size
        # Gestion de la font
        resolved_font_path = os.path.join("ressources", "fonts", f"{font_name}.ttf")
        print(os.path.isfile(resolved_font_path))
        if resolved_font_path and os.path.isfile(resolved_font_path):
            try:
                arcade.load_font(resolved_font_path)
                self._font_name = font_name or resolved_font_path
            except Exception:
                self._font_name = resolved_font_path
        else:
            self._font_name = font_name or "Arial"

        if background_texture_path and os.path.isfile(background_texture_path):
            try:
                self._background_texture = arcade.load_texture(background_texture_path)
                
            except Exception:
                self._background_texture = None


    def set_text(self, text: str, *, reset_speed: bool = True) -> None:
        self.full_text = text
        self.visible_count = 0
        if reset_speed:
            self._accumulator = 0.0

    def skip(self) -> None:
        self.visible_count = len(self.full_text)

    def is_finished(self) -> bool:
        return self.visible_count >= len(self.full_text)

    def update(self, delta_time: float) -> None:
        if self.is_finished() or self.characters_per_second <= 0.0:
            return
        self._accumulator += delta_time * self.characters_per_second
        advance = int(self._accumulator)
        if advance > 0:
            self.visible_count = min(len(self.full_text), self.visible_count + advance)
            self._accumulator -= advance

    ## le * impose que les paramètres soient passés en tant 
    def draw(self, *, offset_x: int = 0, offset_y: int = 0) -> None:
        left = self.x + offset_x
        bottom = self.y + offset_y
        right = left + self.width
        top = bottom + self.height

        # Fond
        if self._background_texture is not None:

            arcade.draw_texture_rect(
                self._background_texture,
                arcade.LBWH(left, bottom, self.width, self.height),
            )

        else:
            arcade.draw_lrbt_rectangle_filled(
                left, right, bottom, top, self.background_color
            )

        if self._background_texture is None and self.border_width > 0:
            arcade.draw_lrbt_rectangle_outline(
                left,
                right,
                bottom,
                top,
                self.border_color,
                border_width=self.border_width,
            )

        visible_text = self.full_text[: self.visible_count]
        text_left = left + self.padding
        text_top = top - self.padding
        text_width = max(0, self.width - 2 * self.padding)
        text_height = max(0, self.height - 2 * self.padding)

        arcade.draw_text(
            visible_text,
            text_left,
            text_top,
            self.text_color,
            self.font_size,
            width=text_width,
            align="left",
            font_name=self._font_name,
            anchor_y="top",
        )
