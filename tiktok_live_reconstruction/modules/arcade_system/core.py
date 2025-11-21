# modules/arcade_system/core.py
# ==============================================
# Arcade演出中核モジュール
# 役割：
#  - Arcadeウィンドウを生成
#  - 描画ループとエフェクト更新
#  - Queue経由でcontrollerに命令を渡す
# ==============================================

import arcade
import queue
import random
from . import controller
from .effects.sprite import handle_collisions
# from .effects.combo import ComboText

from .effects.fireworks_numpy import NumpyFireworksEffect, init_global as _fw_init_global
# from .effects.reconnect import ReconnectButton
from .effects.point_text import PointText
arcade_queue: queue.Queue | None = None


class GiftWindow(arcade.View):
    """Arcadeの描画・演出を統括するView"""
    def __init__(self):
        super().__init__()
        self.layers = {
            "background": [],                     # 枠・固定UI
            "background_static":[],
            "background_dynamic":[],
            
            "stickers_static":[],
            "stickers_particles":[],
            "stickers_sprites":arcade.SpriteList(use_spatial_hash=True),

            "effects":[],
            "sprites": arcade.SpriteList(use_spatial_hash=True),  # ギフト画像
            "ui":[],
            "overlay": [],                         # テキスト、パーティクル、HUD
        }
        self.drag_target = None
        self.background_color = (0, 0, 0, 0)

        
        self.last_queue_time = 0  # ← 追加
        self.queue_cooldown = 2.0  # ← クールタイム秒
        
        self.point_ui = PointText(self.width/2, self.height - 100)
        self.layers["overlay"].append(self.point_ui)
        # combo_display = ComboText(self.width / 2, self.height - 200)
        # self.layers["overlay"].append(combo_display)
        print("[ARC-COMBO] 常駐コンボシステム起動")
        
        self.fx_fireworks = NumpyFireworksEffect(max_particles=20000, particle_radius=2.0)
        _fw_init_global(self.fx_fireworks)

        # 60FPSでqueue監視
        arcade.schedule(self.update_queue, 1 / 60)

    # --- Queue監視 ---
    def update_queue(self, dt):
        """mainスレッドからの命令を受信しcontrollerへ転送"""
        if not arcade_queue:
            return
        while not arcade_queue.empty():
            print("use updata_queue")
            
            try:
                cmd, args = arcade_queue.get_nowait()
            except Exception:
                print("[reporting core.py]lost queue...")
                break
            controller.handle_command(cmd, args, self)

    # --- 更新処理 ---
    def on_update(self, dt):
        # 動的スプライト更新
        self.layers["sprites"].update()
        for s in list(self.layers["sprites"]):
            if hasattr(s, "keep_in_bounds"): s.keep_in_bounds(self.width, self.height)
            if getattr(s, "is_dead", lambda: False)(): s.remove_from_sprite_lists()


        self.layers["stickers_sprites"].update()

        # 衝突（必要なら）
        try:
            from .effects.gift_balloon import handle_collisions
            handle_collisions(self)  # ← 内部で self.layers["sprites"] を参照する実装に変更
        except Exception as e:
            print("[DEBUG] Error:", e)

       # 2) 更新フック
        self.fx_fireworks.update(dt)


        # マウス掴み補正（衝突でズレても元に戻す）
        if self.drag_target and getattr(self.drag_target, "dragging", False):
            s = self.drag_target
            mx, my = self.window._mouse_x, self.window._mouse_y
            s.center_x = mx - getattr(s, "_drag_offset_x", 0)
            s.center_y = my - getattr(s, "_drag_offset_y", 0)

    # --- 描画処理 ---
    def on_draw(self):
        self.clear()
        draw_order = [
            "background",
            "background_static",
            "background_dynamic",
            "stickers_static",
            "stickers_particles",
            "stickers_sprites",
            "effects",
            "ui",
            "overlay",
        ]
        
        for key in draw_order:
            layer = self.layers[key]
            if key == "stickers_sprites":
                layer.draw()
                continue
            for obj in layer:
                if hasattr(obj, "draw"):
                    obj.draw()
        # 描画順序を固定

        self.layers["sprites"].draw()


        # 3) 描画フック
        self.fx_fireworks.draw()
    # --- マウス操作（ドラッグ対応）---
    def on_mouse_press(self, x, y, button, modifiers):

        for sprite in reversed(self.layers["sprites"]):  # 上にあるもの優先
            if sprite.collides_with_point((x, y)):
                self.drag_target = sprite
                sprite.dragging = True
                sprite.vx = sprite.vy = 0
                # --- 追加部分 ---
                sprite._drag_offset_x = x - sprite.center_x
                sprite._drag_offset_y = y - sprite.center_y
                # ----------------
                break
        # ★ 新規：ステッカー押しのけ
        for system in self.layers["stickers_particles"]:
            if hasattr(system, "tap_push"):
                system.tap_push(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.drag_target:
            self.drag_target.dragging = False
            self.drag_target = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag_target:
            s = self.drag_target

            # 位置更新
            s.center_x = x - getattr(s, "_drag_offset_x", 0)
            s.center_y = y - getattr(s, "_drag_offset_y", 0)

            # 速度設定
            s.vx = dx / 2
            s.vy = dy / 2

            # --- 新規：回転慣性付与 ---
            s.angular_velocity += (dx + dy) * 2

# --- 外部実行用 ---
def run(shared_queue: queue.Queue):
    """main.py から呼ばれる起動エントリ"""
    global arcade_queue
    arcade_queue = shared_queue

    window = arcade.Window(720, 1280, "Gift Effects", resizable=True, gl_version=(3, 3))
    window.clear_color = (0, 0, 0, 0)

    game = GiftWindow()
    window.show_view(game)
    arcade.run()