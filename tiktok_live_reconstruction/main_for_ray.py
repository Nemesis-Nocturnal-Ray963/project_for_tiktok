

# MIT License
# Copyright (c) 2024 Isaac Kogan
# Copyright (c) 2025 Nemesis-Nocturnal-Ray963

#
# This file is part of software distributed under the MIT License.
# See the LICENSE file in the project root for full license information.
import sys, os, asyncio, json, csv,queue,threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from TikTokLive import TikTokLiveClient
from TikTokLive.events import *
from TikTokLive.client.errors import UserOfflineError
from modules import config, setup
from modules import receive
from modules import command_worker_mod as cwm
from modules import combo_system as c_sys
# from modules import arcade_system_alpha
from modules.arcade_system import core as arcade_system
from modules import tiktok_live_system
import obsws_python as obs



#--------------------------------------------------
#このソフトができること
#起動時に指定したURL先に投げられたギフト情報を取得
#ローカルサーバーのマインクラフトにコマンドを送信
#サーバーの指定方法はIPアドレスとポート番号
#グローバルサーバーに対応予定
#受け取ったギフト情報を使ってマインクラフトサーバーにコマンドを送信
#--------------------------------------------------
# ==========================================================
# バックグラウンドで動くコマンドワーカー
# ==========================================================
async def command_worker():
    await cwm.command_worker_mod()

async def combo_system():
    await c_sys.combo_system_mod()

# ==========================================================
# TikTok クライアント管理クラス
# ==========================================================
async def backend_async():
    print("=== Backend systems started ===")

    print("test mode (y/n)")
    # --- 設定入力 ---
    is_test = False
    is_use_obs = False
    is_use_minecraft = False

    # --- Minecraftワーカー ---
    if is_use_minecraft:
        asyncio.create_task(cwm.command_worker_mod())
        config.is_minecraft_server_connect = True

    # --- OBSシステム ---
    if is_use_obs:
        config.obs_client = obs.ReqClient(config.HOST, config.PORT, config.PASSWORD)
        await setup.setup_scene_and_source(config.obs_client, config.SCENE_NAME, config.SOURCES_NAMES)
        asyncio.create_task(c_sys.combo_system_mod())

    if is_test:
        for i in range(3):
            print("=== テストプログラム ===")
        test_env = tiktok_live_system.TestSystem()
        # ここで REPL を開始
        await test_env.test_input_cord()
    else:
        # --- TikTok Live クライアント ---
        tiktok_usernames = ["muzukiray963"]
        print("登録されたユーザー:", tiktok_usernames)
        await tiktok_live_system.start_tiktok_clients(tiktok_usernames)

async def main():
    print("=== Arcade Main Thread ===")
    # --- スレッド共有Queue（multiprocessing不使用） ---
    shared_queue = queue.Queue()
    # receive.arcade_queue = shared_queue
    receive.arcade_queue = shared_queue
    # --- バックエンドを別スレッドで非同期実行 ---
    backend_thread = threading.Thread(target=lambda: asyncio.run(backend_async()), daemon=True)
    backend_thread.start()

    # --- Arcadeウィンドウ起動（メインスレッドで実行） ---
    arcade_system.run(shared_queue)
    print("====== main finish line... ======")

# 実行開始
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました。配信お疲れ様でした。")
        input("Enterキーを押して閉じてください…")


