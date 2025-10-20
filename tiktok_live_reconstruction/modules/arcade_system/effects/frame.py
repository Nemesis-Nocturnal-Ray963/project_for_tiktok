# modules/arcade_system/effects/frame.py
# ==============================================
# 静的フレーム表示モジュール
# 役割：
#  - 枠やUIなどの静的画像を表示・非表示
#  - controllerから "show_frame" コマンドで呼ばれる
# ==============================================

import arcade
import os


class FrameSprite(arcade.Sprite):
    """静的フレーム画像"""
    def __init__(self, image_path: str, window_width: int, window_height: int, scale: float = 1.0):
        super().__init__(image_path, scale=scale)
        self.width = window_width
        self.height = window_height
        self.center_x = window_width // 2
        self.center_y = window_height // 2


def toggle_frame(args: list, window):
    """
    配信フレームをON/OFFで切り替える。
    args[0] = "deployment" → 表示
    args[0] = "shutdown" → 削除
    """
    if not args or not isinstance(args[0], str):
        print("[ARC-FRAME] Invalid args")
        return

    action = args[0]
    image_path = "assets/images/frame/frame_1.png"

    # 絶対パス補完
    if not os.path.isabs(image_path):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base, image_path)
    image_path = os.path.abspath(image_path).replace("\\", "/")

    if action == "deployment":
        # 既に存在していない場合のみ生成
        if not any(isinstance(f, FrameSprite) for f in window.static_layers):
            try:
                frame_sprite = FrameSprite(image_path, window.width, window.height)
                window.static_layers.append(frame_sprite)
                print("[ARC-FRAME] Frame deployed")
            except Exception as e:
                print(f"[ARC-FRAME] Failed to deploy frame: {e}")
        else:
            print("[ARC-FRAME] Frame already exists")

    elif action == "shutdown":
        # 存在していれば削除
        before = len(window.static_layers)
        window.static_layers = [f for f in window.static_layers if not isinstance(f, FrameSprite)]
        after = len(window.static_layers)
        print(f"[ARC-FRAME] Frame removed ({before - after} deleted)")

    else:
        print(f"[ARC-FRAME] Unknown action: {action}")
