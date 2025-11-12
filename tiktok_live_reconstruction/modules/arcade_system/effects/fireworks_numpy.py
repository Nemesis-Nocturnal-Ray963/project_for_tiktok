# NumPy版 花火エフェクト（追加ファイル）
# 使い方：
#   1) Windowで NumpyFireworksEffect を生成
#   2) on_updateで update(dt)、on_drawで draw() を呼ぶ
#   3) 既存の「花火発火」から trigger(x, y, color) を呼ぶ
#   4) 互換用：init_global(effect) 後に trigger_global(x, y, color) も可
import os, config
import arcade
import numpy as np
import math
import random
from typing import Tuple, Optional

Color = Tuple[int, int, int]

# --- 効果音ロード ---
SOUNDS_DIR = os.path.join(config.SOUNDS_DIR, "fireworks")
FIREWORK_SOUNDS = []
for name in ("fireworks1.mp3", "fireworks2.mp3", "fireworks3.mp3"):
    path = os.path.join(SOUNDS_DIR, name)
    if os.path.exists(path):
        FIREWORK_SOUNDS.append(arcade.load_sound(path))
print(f"[ARC-FW_NP] Loaded {len(FIREWORK_SOUNDS)} firework sounds")

class _FireworkSystem:
    """NumPy配列で粒子を一括管理"""
    def __init__(self, max_particles: int = 20000):
        self.max = int(max_particles)
        self.count = 0
        self.x = np.zeros(self.max, dtype=np.float32)
        self.y = np.zeros(self.max, dtype=np.float32)
        self.vx = np.zeros(self.max, dtype=np.float32)
        self.vy = np.zeros(self.max, dtype=np.float32)
        self.life = np.zeros(self.max, dtype=np.float32)
        self.rgb = np.zeros((self.max, 3), dtype=np.uint8)

    def spawn(self, x: float, y: float, color: Color = (255, 200, 128),num: int = 80, speed_min: float = 1.5, speed_max: float = 5.0,life_frames: float = 90.0):
        num = int(num)
        if num <= 0:
            return

        remain = self.max - self.count
        if remain <= 0:
            return
        num = min(int(num), remain)
        start = self.count
        end = start + num

        angles = np.linspace(0.0, 2.0 * math.pi, num, endpoint=False, dtype=np.float32)
        speeds = np.random.uniform(speed_min, speed_max, num).astype(np.float32)
        self.vx[start:end] = np.cos(angles) * speeds
        self.vy[start:end] = np.sin(angles) * speeds
        self.x[start:end] = x
        self.y[start:end] = y
        self.life[start:end] = life_frames
        self.rgb[start:end] = np.array(color, dtype=np.uint8)
        self.count = end

    def update(self, gravity: float = 0.25):
        if self.count == 0:
            return
        sl = slice(0, self.count)
        self.x[sl] += self.vx[sl]
        self.y[sl] += self.vy[sl]
        self.vy[sl] -= gravity
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


class NumpyFireworksEffect:
    """GiftWindowから描画範囲を受け取ってランダム生成"""
    def __init__(self, max_particles: int = 20000, particle_radius: float = 2.0):
        self.sys = _FireworkSystem(max_particles)
        self.radius = particle_radius

    def trigger(self, window, num: int = 80):
        # GiftWindowの幅・高さを利用してランダム座標を決定
        x = random.uniform(100, window.width - 100)
        y = random.uniform(window.height / 3, window.height * 0.9)
        color = random.choice([
            (255, 128, 64),
            (128, 255, 255),
            (255, 128, 255),
            (255, 255, 128),
            (128, 200, 255)
        ])
        self.sys.spawn(x, y, color=color, num=num)

        # --- 効果音を再生（音ファイルがある場合のみ）---
        if FIREWORK_SOUNDS:
            snd = random.choice(FIREWORK_SOUNDS)
            arcade.play_sound(snd, volume=0.5)

    def update(self, dt: float):
        self.sys.update()

    def draw(self):
        if self.sys.count == 0:
            return
        for i in range(self.sys.count):
            # --- フェードアウト処理 ---
            # 寿命を 0〜1 に正規化
            life_ratio = max(0.0, min(1.0, self.sys.life[i] / 90.0))
            alpha = int(255 * life_ratio)

            # 色に透明度を追加
            rgb = tuple(int(v) for v in self.sys.rgb[i])
            color_with_alpha = (*rgb, alpha)

            # 描画
            arcade.draw_circle_filled(self.sys.x[i],self.sys.y[i],self.radius,color_with_alpha)


# --- controller互換関数 ---
_GLOBAL_EFFECT: Optional[NumpyFireworksEffect] = None

def init_global(effect: NumpyFireworksEffect):
    global _GLOBAL_EFFECT
    _GLOBAL_EFFECT = effect

def trigger_global(args, window):
    """ controllerから func(args, window) の形式で呼ばれる
        args = [count, delay] の旧形式に対応
    """
    global _GLOBAL_EFFECT
    if _GLOBAL_EFFECT is None:
        return

    # --- パラメータ抽出 ---
    count = 5
    delay = 0.1
    if isinstance(args, (list, tuple)):
        if len(args) >= 1:
            try:
                count = int(args[0])
            except Exception:
                pass
        if len(args) >= 2:
            try:
                delay = float(args[1])
            except Exception:
                pass

    # --- 花火をスケジュール発射 ---
    def spawn_one(_):
        _GLOBAL_EFFECT.trigger(window)

    for i in range(count):
        arcade.schedule_once(spawn_one, i * delay)
