import arcade
from modules import config
import os

class RoseText:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        
        font_path = config.FONT_TYPE_TOROMAN   # SoukouMincho.ttf の絶対パス
        arcade.load_font(font_path)
        self.font_name = "AnnyantRoman"
        self.arc_text = arcade.Text("バラトータル:0ホン", x, y, arcade.color.WHITE, self.size,font_name=self.font_name,anchor_x="center", anchor_y="center")

    def draw(self):
        text = f"バラトータル:{config.ROSE_TOTAL}ホン"

        # 縁の色
        outline_color = arcade.color.BLACK
        # 本体の色
        main_color = arcade.color.WHITE

        # オフセット（太さ）
        o = 4


        # 四方向にアウトラインを描く
        for dx, dy in [(-o, 0), (o, 0), (0, -o), (0, o)]:
            arcade.draw_text(
                text,
                self.x + dx,
                self.y + dy,
                outline_color,
                self.size,
                font_name=self.font_name,
                anchor_x="center",
                anchor_y="center"
            )

        # 本体の文字
        arcade.draw_text(
            text,
            self.x,
            self.y,
            main_color,
            self.size,
            font_name=self.font_name,
            anchor_x="center",
            anchor_y="center"
        )
        # ここで config の値を読むだけ
        self.arc_text.text = f"バラトータル:{config.ROSE_TOTAL}ホン"
        self.arc_text.draw()
