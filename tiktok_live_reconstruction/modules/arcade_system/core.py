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

arcade_queue: queue.Queue | None = None


class GiftWindow(arcade.View):
    """Arcadeの描画・演出を統括するView"""
    def __init__(self):
        super().__init__()
        self.effects = []          # 登録中の演出（SpriteやBeamなど）
        self.static_layers = []    # 背景やフレームなど固定要素
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
            try:
                cmd, args = arcade_queue.get_nowait()
            except Exception:
                break
            controller.handle_command(cmd, args, self)

    # --- 更新処理 ---
    def on_update(self, dt):
        for eff in list(self.effects):
            eff.update(dt)
            # エフェクトが寿命を迎えたら削除
            if getattr(eff, "is_dead", lambda: False)():
                self.effects.remove(eff)

    # --- 描画処理 ---
    def on_draw(self):
        self.clear()
        # 静的レイヤ
        for s in self.static_layers:
            s.draw()
        # 動的エフェクト
        for eff in self.effects:
            eff.draw()

    # --- マウス操作（ドラッグ対応）---
    def on_mouse_press(self, x, y, button, modifiers):
        for eff in reversed(self.effects):
            if hasattr(eff, "collides_with_point") and eff.collides_with_point((x, y)):
                eff.dragging = True
                self.drag_target = eff
                if hasattr(eff, "vx"): eff.vx = 0
                if hasattr(eff, "vy"): eff.vy = 0
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
            if hasattr(s, "vx"): s.vx = dx / 2
            if hasattr(s, "vy"): s.vy = dy / 2


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