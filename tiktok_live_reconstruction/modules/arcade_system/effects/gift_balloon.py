# modules/arcade_system/effects/sprite.py
# ==============================================
# ギフト画像演出モジュール
# 役割：
#  - ギフト画像を画面上にスポーンさせる
#  - 慣性・重力・反発・ドラッグ対応  装甲明朝
# ==============================================

import arcade
import random
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BASE_DIR = os.path.abspath(BASE_DIR).replace("\\", "/")

SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds", "spawn_sounds")
SOUND_PATHS = [os.path.join(SOUND_DIR, f"spawn{i}.mp3") for i in range(1, 4)]

SOUNDS = []
for path in SOUND_PATHS:
    try:
        SOUNDS.append(arcade.load_sound(path))
    except Exception as e:
        print(f"[ARC-SOUND] Failed to load: {path} ({e})")

class GiftSprite(arcade.Sprite):
    def __init__(self, image_path,coin, x: float, y: float, scale: float = 0.1):
        super().__init__(image_path, scale=scale)
        self.target_scale = 0.5
        self.center_x = x
        self.center_y = y
        self.spawn_timer = 0.0
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.dragging = False
        
        self.image_path = image_path
        # --- 上昇パラメータ ---
        self.float_timer = 0.0
        self.ascent_time = 1.0 * float(coin)      # フレーム単位で上昇する時間
        self.ascent_power = 0.3      # 上昇の強さ（初期値）
        self.coin = float(coin)
        
        # --- 角度系の追加 ---
        self.angle = random.uniform(0, 360)
        self.angular_velocity = random.uniform(-60, 60)  # 度/秒
        
        if SOUNDS:
            arcade.play_sound(random.choice(SOUNDS))

    def update(self, dt: float = 1/60):
        # --- 回転（自然転がり）---
        self.angle += self.angular_velocity * dt
        self.angular_velocity *= 0.98  # 減衰

        # 出現アニメーション
        current_scale = self.scale[0] if isinstance(self.scale, tuple) else self.scale
        if current_scale < self.target_scale:
            self.spawn_timer += dt
            duration = 0.25
            progress = min(self.spawn_timer / duration, 1.0)
            ease = 1 - math.pow(1 - progress, 3)
            self.scale = self.target_scale * ease

        # === 浮遊時間管理 ===
        if not self.dragging:
            # self.float_timer += 1
            if self.float_timer < self.ascent_time:
                # 上昇期
                gravity = -self.ascent_power
                
            else:
                # 徐々に下降
                gravity = 0.05

            self.vy -= gravity
            self.center_x += self.vx * dt * 60
            self.center_y += self.vy * dt * 60
            self.vx *= 0.99
            self.vy *= 0.99

            if self.float_timer < self.ascent_time:
                # --- 上限高度チェック ---
                max_height = 960  # 例: 上昇上限 (window.height * 0.8 程度)
                if self.center_y > max_height:
                    self.center_y = max_height
                    # 上にぶつかったら反発または静止
                    self.vy = -abs(self.vy) * 0.3  # 軽く跳ね返る or
                    # self.vy = 0.0                # 完全に静止させる場合はこちら

    def keep_in_bounds(self, width: float, height: float):
        """画面端で反発"""
        margin = 100
        if self.center_x < margin:
            self.center_x = margin
            self.vx *= -0.6
        elif self.center_x > width - margin:
            self.center_x = width - margin
            self.vx *= -0.6
    
    def is_dead(self) -> bool:
        """画面外に落下したら削除"""
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
    coin = args[1]
    # 絶対パスに補完
    if not os.path.isabs(image_path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        image_path = os.path.join(project_root, image_path)
    image_path = os.path.abspath(image_path).replace("\\", "/")

    x = random.randint(100, window.width - 100)
    y = random.randint(window.height // 2, window.height - 100)

    try:
        sprite = GiftSprite(image_path,coin, x, y)
        window.layers["sprites"].append(sprite)
        print(f"[ARC-SPRITE] Spawned gift: {os.path.basename(image_path)}")
    except Exception as e:
        print(f"[ARC-SPRITE] Failed to spawn gift: {e}")


def handle_collisions(window):
    restitution = 0.85
    separation = 0.15
    sprites = window.layers["sprites"]
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
                sprite.center_x += nx * overlap * separation / 2
                sprite.center_y += ny * overlap * separation / 2
                other.center_x -= nx * overlap * separation / 2
                other.center_y -= ny * overlap * separation / 2

                def _get_scale(s):
                    return s.scale[0] if isinstance(s.scale, (tuple, list)) else s.scale
                # === 合体処理 ===
                if sprite.image_path == other.image_path:
                    # 新しいスプライト作成
                    merged = GiftSprite(
                    sprite.image_path,
                    sprite.coin,
                    (sprite.center_x + other.center_x) / 2,
                    (sprite.center_y + other.center_y) / 2,
                    scale=max(_get_scale(sprite), _get_scale(other)) * 1.2
                    )
                    # 適当な初速
                    merged.vx = (sprite.vx + other.vx) / 2
                    merged.vy = (sprite.vy + other.vy) / 2 + 1.5
                    sprites.append(merged)

                    # 元を削除
                    sprite.remove_from_sprite_lists()
                    other.remove_from_sprite_lists()
                    print(f"[ARC-SPRITE] 合体: {os.path.basename(sprite.image_path)}")
                    break
                # --- 速度反転（単純弾性衝突）---
                # --- 通常反発（別画像）---
                else:
                    tmp_vx,tmp_vy = sprite.vx , sprite.vy
                    sprite.vx = other.vx * restitution
                    sprite.vy = other.vy * restitution
                    other.vx = tmp_vx * restitution
                    other.vy = tmp_vy * restitution


                # --- 追加：衝突による回転発生 ---
                # 相対速度の大きさをトルクの強さに変換
                relative_speed = math.hypot(sprite.vx - other.vx, sprite.vy - other.vy)

                # 接触方向に基づいてランダムな回転方向を付与
                torque = (random.random() - 0.5) * relative_speed * 2

                if hasattr(sprite, "angular_velocity"):
                    sprite.angular_velocity += torque
                if hasattr(other, "angular_velocity"):
                    other.angular_velocity -= torque