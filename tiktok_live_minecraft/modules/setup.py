import sys
import os
print("//sys.path")
print(sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import setup,config,receive

import asyncio
import obsws_python as obs
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, FollowEvent, LikeEvent
from TikTokLive.client.errors import UserOfflineError
from datetime import datetime

import random
import asyncio
import time
import obsws_python as obs
import colorsys
import math
from mcrcon import MCRcon


async def setup_scene_and_source(obs_client,SCENE_NAME, SOURCES_NAMES):
    when_create_settings = {
            "font": {"size": 128, "face": "Arial"},
            "text": "test",
            "vertical": False,
            "color": 0,
            "opacity": 100,
            "gradient": False,
            "gradient_color": 0,
            "bk_color": 0,
            "bk_opacity": 0,
            "align": "right",
            "valign": "bottom",
            "outline": True,
            "outline_size": 20,
            "outline_color": 0,
            "outline_opacity": 100,
            }

    print("called setup_scene_and_source")
    # シーンが存在しなければ作成
    scene_list = obs_client.get_scene_list().scenes
    scene_names = [s["sceneName"] for s in scene_list]

    if SCENE_NAME not in scene_names:
        obs_client.create_scene(SCENE_NAME)
        print(f"シーン '{SCENE_NAME}' を作成しました")
    else:
        print(f"シーン '{SCENE_NAME}' はすでに存在します")

    # シーン内のソース一覧を取得
    source_list = obs_client.get_scene_item_list(SCENE_NAME)

    # 既存のソース名をリスト化
    existing_sources = [item["sourceName"] for item in source_list.scene_items]
    # for item in source_list.scene_items:
    #     print(f"sceneItemId: {item['sceneItemId']}, sourceName: {item['sourceName']}")
    for source_name, when_create_settings in SOURCES_NAMES.items():
        if source_name not in existing_sources:
            obs_client.create_input(
                SCENE_NAME,                # シーン名
                source_name,               # ソース名
                "text_gdiplus_v3",         # テキストソースの種類
                when_create_settings,      # 初期設定（辞書で渡せる）
                True
            )
            print(f"{source_name} を作成しました")
        else:
            print(f"{source_name} はすでに存在します。作成をスキップします。")

async def setup_system():
    enable_check = input("テストしますか？ (y/n): ").strip().lower() or "y"
    config.is_test_now = enable_check == "y"

async def setup_server():

    print("接続先を選んでください：")
    print("1: 任意のTikTok Live")
    print("2: Weather News Live(テスト用)")
    choice = input("番号を入力してください（1 または 2）: ").strip()

    if choice == "1":
        # TikTok Live 接続
        config.tiktok_name = input("TikTokのユーザー名を入力してください（@は不要）空白なら、muzukiray963: ").strip() or "muzukiray963"


    elif choice == "2":
        # Weather News Live 接続
        print("Weather News Live に接続します。テスト用")
        # ここに weathernewslive 用の接続コードを追加
        config.tiktok_name = "weathernewslive"
    else:
        print("無効な入力です。1 または 2 を入力してください。")





    # --- Minecraft 接続設定 ---
    config.is_minecraft_server_connect = input(
        "Minecraft に接続しますか？\n"
        "つなげる場合は空白でEnter、繋げない場合は文字を入力してEnter："
    ).strip() == ""



    # --- TikTok Live 接続設定（コンボシステム） ---
    config.is_combo_system_connect = input(
        "コンボシステムは起動しますか？\n"
        "起動する場合は空白でEnter、しない場合は文字を入力してEnter："
    ).strip() == ""




    config.tiktok_client = TikTokLiveClient(unique_id=config.tiktok_name)
    # await config.tiktok_client.connect()
    




    # if config.is_minecraft_server_connect:
    #     mcr = MCRcon("127.0.0.1", "3699", port=25575)
    #     mcr.connect()
    #     print("Minecraft サーバーに接続しました。")
    # else:
    #     print("Minecraft サーバー接続をスキップしました。")

    if config.is_combo_system_connect:
        print("test")