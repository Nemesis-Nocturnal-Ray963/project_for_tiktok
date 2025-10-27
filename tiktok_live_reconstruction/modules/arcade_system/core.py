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

arcade_queue: queue.Queue | None = None


class GiftWindow(arcade.View):
    """Arcadeの描画・演出を統括するView"""
    def __init__(self):
        super().__init__()
        self.layers = {
            "background": [],                     # 枠・固定UI
            "light": [],                          # LightBeam類（加算/半加算）
            "sprites": arcade.SpriteList(use_spatial_hash=True),  # ギフト画像
            "overlay": []                         # テキスト、パーティクル、HUD
        }
        self.drag_target = None
        self.background_color = (0, 0, 0, 0)

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
                print("lost queue...")
                break
            controller.handle_command(cmd, args, self)

    # --- 更新処理 ---
    def on_update(self, dt):
        # 動的スプライト更新
        self.layers["sprites"].update()
        for s in list(self.layers["sprites"]):
            if hasattr(s, "keep_in_bounds"): s.keep_in_bounds(self.width, self.height)
            if getattr(s, "is_dead", lambda: False)(): s.remove_from_sprite_lists()

        # 衝突（必要なら）
        try:
            from .effects.sprite import handle_collisions
            handle_collisions(self)  # ← 内部で self.layers["sprites"] を参照する実装に変更
        except Exception:
            pass

        # light / overlay 側の独自エフェクト（クラスに update があれば呼ぶ）
        for key in ("light", "overlay"):
            for obj in list(self.layers[key]):
                if hasattr(obj, "update"): obj.update(dt)

    # --- 描画処理 ---
    def on_draw(self):
        self.clear()
        # 描画順序を固定
        for obj in self.layers["background"]:
            obj.draw()
        for obj in self.layers["light"]:
            obj.draw()
        self.layers["sprites"].draw()
        for obj in self.layers["overlay"]:
            obj.draw()

    # --- マウス操作（ドラッグ対応）---
    def on_mouse_press(self, x, y, button, modifiers):
        for sprite in reversed(self.layers["sprites"]):  # 上にあるもの優先
            if sprite.collides_with_point((x, y)):
                self.drag_target = sprite
                sprite.dragging = True
                sprite.vx = sprite.vy = 0
                break

    def on_mouse_release(self, x, y, button, modifiers):
        if self.drag_target:
            self.drag_target.dragging = False
            self.drag_target = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag_target:
            s = self.drag_target
            s.center_x += dx
            s.center_y += dy
            s.vx = dx / 2
            s.vy = dy / 2


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