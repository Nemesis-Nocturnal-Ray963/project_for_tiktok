import arcade, time
from modules import config
import colorsys

class ComboText:
    RELATIVE_FONT_PATH = "assets/images/fonts/SoukouMincho.ttf"
    """Arcade上でコンボ数を表示するエフェクト"""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.text = "0 combo!"
        self.color = arcade.color.CYAN
        self.opacity = 255
        self.last_update = time.time()
        self.fade_started = False
        self.hue = 0.0
        self.timer = 0
        self.text_obj = arcade.Text(
            self.text,
            self.x,
            self.y,
            (0, 255, 255, 255),
            48,
            anchor_x="center",
            anchor_y="center",
            font_name="装甲明朝"
        )

    def update(self, dt):
        now = time.time()
        # combo更新時
        if config.gift_counter > config.combo_counter:
            config.combo_counter += 1
            self.text = f"{config.combo_counter} combo!"
            self.last_update = now
            self.fade_started = False
            self.opacity = 255
            # self.hue = (self.hue + 0.1) % 1.0

        # 経過処理
        if now - self.last_update > 20:
            self.fade_started = True
        if self.fade_started:
            self.opacity = max(0, self.opacity - 2)

        # 30秒経過でリセット
        if now - self.last_update > 30:
            config.combo_counter = 0
            config.gift_counter = 0
            self.text = "0 combo!"


        self.timer += dt
        self.hue = (self.hue + dt * 0.2) % 1.0  # 色相をゆっくり回転
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)

        self.text_obj.text = self.text
        # self.text_obj.color = (r, g, b, int(self.opacity))
        self.text_obj.color = (int(r * 255), int(g * 255), int(b * 255), int(self.opacity))
    def draw(self):
        self.text_obj.draw()
# def spawn_combo_text(args, window):
#     combo_text = ComboText(window.width / 2, window.height - 200)
#     window.layers["overlay"].append(combo_text)
#     print("[ARC-COMBO] Combo counter spawned")