# modules/arcade_system/controller.py
# ==============================================
# Arcadeコントローラ
# 役割：
#  - main.py や他システムから送られる cmd を受け取り
#  - 登録済みのエフェクト生成関数を実行する
# ==============================================
import arcade
from .effects import sprite, beams, frame, test, sound
import os

# --- コマンドと関数の対応表 ---
EFFECT_REGISTRY = {
    "spawn_gift": sprite.spawn_gift,
    "show_frame": frame.toggle_frame,
    "spawn_Icosahedron": beams.toggle_icosahedron,
    "test_test":test.test_print,
    "play_sound": sound.play_sound,
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




# === MP3音源の絶対パス ===
# SOUND_PATH = "C:/Users/x701c/project_for_tiktok/tiktok_live_reconstruction/assets/sounds/boot_sounds.wav"
BASE_DIR =     os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
SOUND_PATH = os.path.join(BASE_DIR, "assets/sounds/boot_sounds.wav")
SOUND_PATH = os.path.abspath(SOUND_PATH)
#.replace("\\", "/")

print(SOUND_PATH)  # デバッグ確認用
# === サウンドのロード ===
bgm_sound = arcade.load_sound(SOUND_PATH)

# === 再生 ===
player = arcade.play_sound(bgm_sound)