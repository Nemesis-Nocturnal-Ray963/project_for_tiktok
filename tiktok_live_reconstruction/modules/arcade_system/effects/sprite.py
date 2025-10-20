# modules/arcade_system/effects/sprite.py
# ==============================================
# ギフト画像演出モジュール
# 役割：
#  - ギフト画像を画面上にスポーンさせる
#  - 慣性・重力・反発・ドラッグ対応
# ==============================================

import arcade
import random
import math
import os


class GiftSprite(arcade.Sprite):
    """単一ギフト画像を管理するSprite"""
    def __init__(self, image_path: str, x: float, y: float, scale: float = 0.5):
        super().__init__(image_path, scale=scale)
        self.center_x = x
        self.center_y = y
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.dragging = False

    def update(self, dt: float = 1/60):
        """物理挙動（慣性・重力・減衰）"""
        if not self.dragging:
            gravity = 0.05
            self.vy -= gravity
            self.center_x += self.vx * dt * 60
            self.center_y += self.vy * dt * 60
            self.vx *= 0.99
            self.vy *= 0.99

    def keep_in_bounds(self, width: float, height: float):
        """画面端で反発"""
        margin = 110
        if self.center_x < margin:
            self.center_x = margin
            self.vx *= -0.6
        elif self.center_x > width - margin:
            self.center_x = width - margin
            self.vx *= -0.6
        if self.center_y < 0:
            self.center_y = 0
            self.vy *= -0.6

    def is_dead(self) -> bool:
        """画面外に落ちたか？"""
        return self.center_y < -100


def spawn_gift(args: list, window):
    print("use spanw_gift...")
    
    """
    ギフト画像を生成してウィンドウに登録する。
    args[0] = 画像パス（相対 or 絶対）
    """
    if not args or not isinstance(args[0], str):
        print("[ARC-SPRITE] Invalid args for spawn_gift")
        return

    image_path = args[0]

    # 絶対パスに補完
    if not os.path.isabs(image_path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        image_path = os.path.join(project_root, image_path)
    image_path = os.path.abspath(image_path).replace("\\", "/")

    x = random.randint(100, window.width - 100)
    y = random.randint(window.height // 2, window.height - 100)

    try:
        sprite = GiftSprite(image_path, x, y)
        window.sprites.append(sprite)
        print(f"[ARC-SPRITE] Spawned gift: {os.path.basename(image_path)}")
    except Exception as e:
        print(f"[ARC-SPRITE] Failed to spawn gift: {e}")


def handle_collisions(window):
    sprites = window.sprites
    # 全スプライトで衝突を検出
    for sprite in sprites:
        hit_list = arcade.check_for_collision_with_list(sprite, sprites)
        for other in hit_list:
            if sprite is other:
                continue
            # --- 距離補正 ---
            dx = sprite.center_x - other.center_x
            dy = sprite.center_y - other.center_y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            overlap = (sprite.width / 2 + other.width / 2 - dist)
            if overlap > 0:
                nx, ny = dx / dist, dy / dist
                sprite.center_x += nx * overlap / 2
                sprite.center_y += ny * overlap / 2
                other.center_x -= nx * overlap / 2
                other.center_y -= ny * overlap / 2

                # --- 速度反転（単純弾性衝突）---
                sprite.vx, other.vx = other.vx, sprite.vx
                sprite.vy, other.vy = other.vy, sprite.vy