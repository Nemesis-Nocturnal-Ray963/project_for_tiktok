# modules/arcade_system/effects/fireworks.py
# ==============================================
# ギフト花火エフェクト
# - ギフト受信で画面上に花火が上昇→爆発
# - ArcadeのSpriteと粒子描画で実現
# ==============================================

import arcade
import random
import math
import os
from modules import config

sounds_dir = os.path.join(config.SOUNDS_DIR, "fireworks")
FIREWORK_SOUNDS = []
for name in ("fireworks1.mp3", "fireworks2.mp3"):
    path = os.path.join(sounds_dir, name)
    if os.path.exists(path):
        FIREWORK_SOUNDS.append(arcade.load_sound(path))
print(f"[ARC-FIREWORKS] Loaded {len(FIREWORK_SOUNDS)} sounds")

class FireworkParticle:
    """花火の破裂粒子"""
    def __init__(self, x, y, color, speed, angle, lifetime=60):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.angle = angle
        self.timer = 0
        self.lifetime = lifetime

    def update(self):
        self.timer += 1
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        # 重力効果
        self.speed *= 0.98
        self.y -= 0.15
        return self.timer < self.lifetime

    def draw(self):
        fade = max(0, 255 - int((self.timer / self.lifetime) * 255))
        arcade.draw_circle_filled(self.x, self.y, 2, (*self.color[:3], fade))

class Firework:
    """単一花火（上昇→爆発）"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = random.uniform(18, 21)
        self.state = "ascending"
        self.color = random.choice([
            arcade.color.CYAN, arcade.color.PINK, arcade.color.YELLOW,
            arcade.color.RED, arcade.color.MAGENTA, arcade.color.WHITE
        ])
        self.particles = []
        self.sound_played = False  # ← 追加：音再生済みフラグ

    def update(self,dt=1/60):
        if self.state == "ascending":
            self.y += self.vy
            self.vy -= 0.25
            if self.vy <= 0:
                self.state = "exploded"
                for _ in range(80):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1.5, 5)
                    color = (
                        random.randint(100, 255),
                        random.randint(100, 255),
                        random.randint(100, 255),
                        255
                    )
                    self.particles.append(FireworkParticle(self.x, self.y, color, speed, angle))
                        # --- 音を一度だけ再生 ---
                if not self.sound_played and FIREWORK_SOUNDS:
                    snd = random.choice(FIREWORK_SOUNDS)
                    arcade.play_sound(snd, volume=0.5)
                    self.sound_played = True  # ← フラグを立てる

        elif self.state == "exploded":
            alive_particles = []
            for p in self.particles:
                if p.update():
                    alive_particles.append(p)
            self.particles = alive_particles

    def draw(self):
        if self.state == "ascending":
            arcade.draw_circle_filled(self.x, self.y, 3, self.color)
        else:
            for p in self.particles:
                p.draw()

    def is_dead(self):
        return self.state == "exploded" and len(self.particles) == 0


def spawn_fireworks(args, window):
    print("[ARC-FIREWORKS] spawn_fireworks called")

    count = int(args[0]) if args and str(args[0]).isdigit() else 6
    delay = float(args[1]) if len(args) > 1 else 0.1
    delay += round(random.uniform(0.0, 0.3), 2)
    def spawn_one(_):
        fw = Firework(random.randint(100, window.width - 100), 0)
        window.layers["overlay"].append(fw)

    for i in range(count):
        arcade.schedule_once(spawn_one, i * delay)