# modules/arcade_system/effects/test.py
# ==============================================
# テスト用モジュール
# 目的：
#  - controller 登録確認やキュー動作確認に使用
# ==============================================

def test_print(args, window):
    """
    Arcadeシステムの動作確認用テスト関数。
    controller から呼び出される。
    """
    print("[ARC-TEST] success: controller and queue working properly.")
    if args:
        print(f"[ARC-TEST] args: {args}")