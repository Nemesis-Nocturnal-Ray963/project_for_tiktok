# modules/arcade_system/controller.py
# ==============================================
# Arcadeコントローラ
# 役割：
#  - main.py や他システムから送られる cmd を受け取り
#  - 登録済みのエフェクト生成関数を実行する
# ==============================================
import arcade
from modules import config

from .effects import sprite, gift_balloon, beams, frame, test, sound,fireworks,fireworks_numpy,fireworks_numpy_ex,sticker_particles,point_text,point_controller
import os

# --- コマンドと関数の対応表 ---
EFFECT_REGISTRY = {
    "spawn_gift": sprite.spawn_gift,
    "spawn_gift_balloon": gift_balloon.spawn_gift,
    "show_frame": frame.toggle_frame,
    "spawn_Icosahedron": beams.toggle_icosahedron,
    "test_test":test.test_print,
    "play_sound": sound.play_sound,
    # "spawn_combo": combo.spawn_combo_text,
    # "spawn_fireworks": fireworks.spawn_fireworks,
	"spawn_fireworks": fireworks_numpy.trigger_global,
	"spawn_fireworks_ex": fireworks_numpy_ex.trigger_global,
    "spawn_sticker": sticker_particles.spawn_sticker_particles,
    "update_point_text":point_controller.update_point_text
}


def handle_command(cmd: str, args: list, window):
    """
    受け取ったコマンドを対応する処理関数へ転送。
    引数:
        cmd: 文字列（例 'spawn_gift'）
        args: 引数リスト
        window: GiftWindowインスタンス（エフェクト追加に使用）
    """
    print("use handle_command...")
    func = EFFECT_REGISTRY.get(cmd)
    if func:
        try:
            func(args, window)
        except Exception as e:
            print(f"[ARC-CONTROLLER] Error: {cmd} failed → {e}")
    else:
        print(f"[ARC-CONTROLLER] Unknown command: {cmd}")

