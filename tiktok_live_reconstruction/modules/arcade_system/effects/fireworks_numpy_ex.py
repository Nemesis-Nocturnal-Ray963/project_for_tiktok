# modules/arcade_system/effects/fireworks_numpy_ex.py
# =====================================================
# 座標データ参照型 花火エフェクト (Extended)
# - assets/fireworks_shapes/ に保存した形状JSONを読み込む
# - 花火ごとに独立した形状を描画できる
# =====================================================

import arcade
import numpy as np
import math, random, os, json
from typing import Tuple, Optional
from modules import config

Color = Tuple[int, int, int]

# --- 効果音ロード ---
SOUNDS_DIR = os.path.join(config.SOUNDS_DIR, "fireworks")
FIREWORK_SOUNDS = []
for name in ("fireworks1.mp3", "fireworks2.mp3", "fireworks3.mp3"):
    path = os.path.join(SOUNDS_DIR, name)
    if os.path.exists(path):
        FIREWORK_SOUNDS.append(arcade.load_sound(path))
print(f"[ARC-FW_NP] Loaded {len(FIREWORK_SOUNDS)} firework sounds")

# 形状フォルダ
SHAPE_DIR = os.path.join(config.ASSETS_DIR, "fireworks_shapes")
os.makedirs(SHAPE_DIR, exist_ok=True)



# -----------------------------------------------------
# 形状ロード関数
# -----------------------------------------------------
def load_shape(name: str) -> Optional[np.ndarray]:
    """assets/fireworks_shapes/name.json を読み込む"""
    path = os.path.join(SHAPE_DIR, f"{name}.json")
    if not os.path.exists(path):
        print(f"[FW_EX] Shape not found: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pts = np.array(data.get("points", []), dtype=np.float32)
        scale = float(data.get("scale", 100.0))
        return pts * scale
    except Exception as e:
        print(f"[FW_EX] Failed to load shape {name}: {e}")
        return None


# -----------------------------------------------------
# 花火システム（NumPy版）
# -----------------------------------------------------
class _FireworkSystem:
    def __init__(self, max_particles: int = 20000):
        self.max = max_particles
        self.count = 0
        self.x = np.zeros(self.max, dtype=np.float32)
        self.y = np.zeros(self.max, dtype=np.float32)
        self.vx = np.zeros(self.max, dtype=np.float32)
        self.vy = np.zeros(self.max, dtype=np.float32)
        self.life = np.zeros(self.max, dtype=np.float32)
        self.rgb = np.zeros((self.max, 3), dtype=np.uint8)

    def spawn_shape(self, x: float, y: float, shape_pts: np.ndarray,color: Color = (255, 200, 150), life_frames: float = 90.0):
        """ 形を保ったまま外側へ拡散する（スケール拡散型）花火
        shape_pts : [-1,1] 範囲の正規化座標リスト
        """
        if shape_pts is None or len(shape_pts) == 0:
            return
        num = len(shape_pts)
        remain = self.max - self.count
        if remain <= 0:
            return
        num = min(num, remain)
        sl = slice(self.count, self.count + num)

        # === 座標セット ===
        self.x[sl] = x + shape_pts[:num, 0]
        self.y[sl] = y + shape_pts[:num, 1]

        # === スケール拡散（形状を保ちながら全体が拡大） ===
        # 元の形の各点の方向そのものを速度として使用
        spread_strength = 0.02  # 拡散の強さ（値を上げると速く広がる）
        rand = np.random.uniform(-0.05, 0.05, (num, 2))  # 微小ランダムで自然さ
        self.vx[sl] = (shape_pts[:num, 0] + rand[:, 0]) * spread_strength
        self.vy[sl] = (shape_pts[:num, 1] + rand[:, 1]) * spread_strength

        # === 残り設定 ===
        self.life[sl] = life_frames
        self.rgb[sl] = np.array(color, dtype=np.uint8)
        self.count += num

    def update(self, gravity: float = 0.0):
        if self.count == 0:
            return
        sl = slice(0, self.count)
        self.x[sl] += self.vx[sl]
        self.y[sl] += self.vy[sl]
        # self.vy[sl] -= gravity
        self.vx[sl] *= 0.98
        self.vy[sl] *= 0.98
        self.life[sl] -= 1.0
        alive = self.life[sl] > 0.0
        n_alive = int(np.count_nonzero(alive))
        if n_alive == 0:
            self.count = 0
            return
        if n_alive != self.count:
            self.x[:n_alive] = self.x[sl][alive]
            self.y[:n_alive] = self.y[sl][alive]
            self.vx[:n_alive] = self.vx[sl][alive]
            self.vy[:n_alive] = self.vy[sl][alive]
            self.life[:n_alive] = self.life[sl][alive]
            self.rgb[:n_alive] = self.rgb[sl][alive]
            self.count = n_alive


# -----------------------------------------------------
# エフェクト本体
# -----------------------------------------------------
class NumpyFireworksEffectEX:
    """形状データを読み込み描画するタイプ"""
    def __init__(self, max_particles: int = 20000, particle_radius: float = 2.0):
        self.sys = _FireworkSystem(max_particles)
        self.radius = particle_radius

    def trigger_shape(self, window, shape_name: str = "heart"):
        shape_pts = load_shape(shape_name)
        if shape_pts is None:
            print(f"[FW_EX] Shape '{shape_name}' not found, using fallback.")
            return

        # ランダム位置に表示
        x = random.uniform(100, window.width - 100)
        y = random.uniform(window.height / 3, window.height * 0.9)
        color = random.choice([
            (255, 150, 180),
            (200, 255, 255),
            (255, 255, 150),
            (255, 180, 255),
        ])
        self.sys.spawn_shape(x, y, shape_pts, color=color)

        # --- 効果音を再生（音ファイルがある場合のみ）---
        if FIREWORK_SOUNDS:
            snd = random.choice(FIREWORK_SOUNDS)
            arcade.play_sound(snd, volume=0.5)

    def update(self, dt: float):
        self.sys.update()

    def draw(self):
        if self.sys.count == 0:
            return
        # for i in range(self.sys.count):
        #     rgb = tuple(int(v) for v in self.sys.rgb[i])
        #     arcade.draw_circle_filled(self.sys.x[i], self.sys.y[i], self.radius, rgb)
        for i in range(self.sys.count):
            # --- フェードアウト処理 ---
            # 寿命を 0〜1 に正規化
            life_ratio = max(0.0, min(1.0, self.sys.life[i] / 90.0))
            alpha = int(255 * life_ratio)

            # 色に透明度を追加
            rgb = tuple(int(v) for v in self.sys.rgb[i])
            color_with_alpha = (*rgb, alpha)

            # 描画
            arcade.draw_circle_filled(
                self.sys.x[i],
                self.sys.y[i],
                self.radius,
                color_with_alpha
            )
# -----------------------------------------------------
# controller 互換関数
# -----------------------------------------------------
_GLOBAL_EX: Optional["NumpyFireworksEffectEX"] = None

def init_global(effect: "NumpyFireworksEffectEX"):
    global _GLOBAL_EX
    _GLOBAL_EX = effect

def trigger_global(args, window):
    """args = [count, delay, shape_name]
       未初期化なら自動的にインスタンス化する
    """
    global _GLOBAL_EX
    # --- 自動初期化 ---
    if _GLOBAL_EX is None:
        print("[FW_EX] Global effect not initialized → auto-create")
        _GLOBAL_EX = NumpyFireworksEffectEX()
        try:
            window.layers["overlay"].append(_GLOBAL_EX)
        except Exception:
            print("[FW_EX] Warning: cannot append to window.layers")
        print("[FW_EX] Initialized global effect instance")

    shape_name = None
    if isinstance(args, (list, tuple)) and len(args) >= 3:
        shape_name = args[2]

    def spawn_one(_):
        _GLOBAL_EX.trigger_shape(window, shape_name or "heart")

    count = 1
    delay = 0.1
    if len(args) >= 1:
        try:
            count = int(args[0])
        except:
            pass
    if len(args) >= 2:
        try:
            delay = float(args[1])
        except:
            pass

    for i in range(count):
        arcade.schedule_once(spawn_one, i * delay)




