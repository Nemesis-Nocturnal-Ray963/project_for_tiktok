# modules/arcade_system/effects/sticker_particles.py
import arcade
import numpy as np
import os
from modules import config
from arcade import Rect

class StickerLayerSprite(arcade.Sprite):
    """地層化されたステッカー画像を保持するSprite"""
    def __init__(self, tex, window):
        super().__init__()
        self.texture = tex

        # window 全体の中心へ配置
        self.center_x = window.width / 2
        self.center_y = window.height / 2

    def draw(self):
        tex = self.texture
        tw = tex.width
        th = tex.height

        half_w = tw / 2
        half_h = th / 2

        left   = self.center_x - half_w
        right  = self.center_x + half_w
        bottom = self.center_y - half_h
        top    = self.center_y + half_h

        rect = Rect(left, right, bottom, top, tw, th, self.center_x, self.center_y)

        arcade.draw_texture_rect(
            texture = tex,
            rect    = rect,
            angle   = 0.0,
            alpha   = 255,
            pixelated = False
        )

class StickerParticleSystem:
    """
    高速ステッカー粒子システム（GPUテクスチャバッチ対応）
    - NumPyで座標を管理（高速）
    - Arcade の draw_scaled_texture_rectangle を利用（GPUバッチ最適化）
    - 1万〜5万のステッカーを処理しても高速
    """
    def __init__(self, texture_path: str, max_count=10000):
        self.max = max_count
        self.count = 0
        
        # 位置・スケール
        self.x = np.zeros(self.max, dtype=np.float32)
        self.y = np.zeros(self.max, dtype=np.float32)
        self.scale = np.ones(self.max, dtype=np.float32) * 0.5

        # 新規：速度ベクトル
        self.vx = np.zeros(self.max, dtype=np.float32)
        self.vy = np.zeros(self.max, dtype=np.float32)

        self.texture = arcade.load_texture(texture_path)



    # -------------------------------------------
    # スポーン
    # -------------------------------------------
    def spawn(self, x, y, amount=1):
        remain = self.max - self.count
        n = min(remain, amount)

        sl = slice(self.count, self.count + n)

        self.x[self.count:self.count+n] = x + np.random.uniform(-340, 340, n)
        self.y[self.count:self.count+n] = y + np.random.uniform(-640, 640 , n)

        self.count += n


    # -------------------------------------------
    # ★ タップ反発（ここが今回のメイン）
    # -------------------------------------------
    def tap_push(self, tap_x, tap_y, radius=120, power=4.0):
        if self.count == 0:
            return

        # pyglet の c_double/c_long 対策：まず float にする
        tx = float(tap_x)
        ty = float(tap_y)


        
        # count を常に int 化
        count = int(self.count)
        # ★ NumPy の shape を揃える：粒子数と同じサイズの配列にする
        #    （この行が今回最重要）
        tx_arr = np.full(self.count, tx, dtype=np.float32)
        ty_arr = np.full(self.count, ty, dtype=np.float32)

        # 各粒子の差分
        dx = self.x[:self.count] - tx_arr
        dy = self.y[:self.count] - ty_arr

        # 距離判定
        dist2 = dx * dx + dy * dy
        r2 = radius * radius

        hit = dist2 < r2

        if not np.any(hit):
            return

        # 押し出し方向
        dist = np.sqrt(dist2[hit]) + 1e-6
        nx = dx[hit] / dist
        ny = dy[hit] / dist

        # 速度に反映
        self.vx[hit] += nx * power
        self.vy[hit] += ny * power

    # -------------------------------------------
    # update
    # -------------------------------------------
    def update(self, dt):
        if self.count == 0:
            return

        sl = slice(0, self.count)

        # 速度 → 位置
        self.x[sl] += self.vx[sl]
        self.y[sl] += self.vy[sl]

        # 摩擦減衰で自然停止
        self.vx[sl] *= 0.92
        self.vy[sl] *= 0.92

    def draw(self):
        """
        GPUバッチ描画
        for ループだが、Arcade 内部で draw_batch にまとめられるため高速
        """
        tex = self.texture
        tw = tex.width
        th = tex.height
        
        x = self.x
        y = self.y
        s = self.scale
        count = self.count

        for i in range(count):
            w = (tw * s[i]) * 0.5   # ← 半分にする
            h = (th * s[i]) * 0.5

            half_w = w / 2
            half_h = h / 2

            left   = x[i] - half_w
            right  = x[i] + half_w
            bottom = y[i] - half_h
            top    = y[i] + half_h

            rect = Rect(
                left,       # left
                right,      # right
                bottom,     # bottom
                top,        # top
                w,          # width
                h,          # height
                x[i],       # x (center)
                y[i]        # y (center)
            )

            arcade.draw_texture_rect(
                texture = tex,
                rect    = rect,
                angle   = 0.0,
                alpha   = 255,
                pixelated = False
            )

    def flatten_to_texture(self, window):
        """    動的ステッカーを static layer に焼き込む（地層化）    """
        print("[FIRE] flatten_to_texture called. count =", self.count)
        if self.count == 0:
            return

        # --- 1. FBO用テクスチャ作成 ---
        width, height = window.width, window.height
        fbo = arcade.Texture.create_empty(
            "sticker_layer",
            width,
            height
        )

        # --- 2. FBO（FrameBuffer）で描画開始 ---
        with arcade.render_target(fbo) as target:
            # 2-1 既存 static layer があれば先に描画
            for obj in window.layers["stickers_static"]:
                if hasattr(obj, "draw"):
                    obj.draw()

            # 2-2 今までの particles をすべて描画
            tex = self.texture
            x = self.x
            y = self.y
            s = self.scale
            count = self.count
            for i in range(count):
                arcade.draw_scaled_texture_rectangle(
                    x[i], y[i], tex, s[i]
                )

        # --- 3. 新しくできた地層 sprite を static に置く ---
        static_sprite = StickerLayerSprite(fbo,window)
        window.layers["stickers_static"] = [static_sprite]

        # --- 4. 動的ステッカーのリセット ---
        self.count = 0
        self.vx[:] = 0
        self.vy[:] = 0
        print("[FIRE] flatten_to_texture called. count =", self.count)
# controller 呼び出し用
SYSTEM = None

def spawn_sticker_particles(args, window):
    global SYSTEM

    if SYSTEM is None:
        path = os.path.join(config.IMAGES_DIR, "gift", "rose.png")
        SYSTEM = StickerParticleSystem(path)
        window.layers["stickers_particles"].append(SYSTEM)

    amount = int(args[0]) if args else 1
    SYSTEM.spawn(window.width // 2, window.height // 2, amount)
    # --- ★ 自動地層化 ---
    if SYSTEM.count > 2000:   # 調整可能
        SYSTEM.flatten_to_texture(window)