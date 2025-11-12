import arcade
import os

SOUND_CACHE = {}

def play_sound(args, window):
    print("test0")
    """args[0]: 相対 or 絶対パスで音声ファイル"""
    if not args or not isinstance(args[0], str):
        print("[ARC-SOUND] Invalid args")
        return

    sound_path = args[0]
    print("test1")
    # 絶対パス補完（effects → modules → tiktok_live_reconstruction → assets）
    if not os.path.isabs(sound_path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        sound_path = os.path.join(project_root, sound_path)
    sound_path = os.path.abspath(sound_path)
    #.replace("\\", "/")
    print(sound_path)
    try:
        if sound_path not in SOUND_CACHE:
            SOUND_CACHE[sound_path] = arcade.load_sound(sound_path)
        arcade.play_sound(SOUND_CACHE[sound_path])
        print(f"[ARC-SOUND] Play: {os.path.basename(sound_path)}")
    except Exception as e:
        print(f"[ARC-SOUND] Failed to play sound: {e}")
