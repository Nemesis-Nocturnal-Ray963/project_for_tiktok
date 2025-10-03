

# MIT License
# Copyright (c) 2024 Isaac Kogan
# Copyright (c) 2025 Nemesis-Nocturnal-Ray963

#
# This file is part of software distributed under the MIT License.
# See the LICENSE file in the project root for full license information.



import sys
import os
# print("//sys.path")
# print(sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules import config,setup,combo_system
from modules import minecraft_interactive_command as m_intr_c
from modules import command_worker_mod as cwm
from modules import combo_system as c_sys

from TikTokLive import TikTokLiveClient
from TikTokLive.events import *





# CommentEvent, GiftEvent, FollowEvent, LikeEvent
from TikTokLive.client.errors import UserOfflineError
from datetime import datetime
from mcrcon import MCRcon
import random
import asyncio
import time
import obsws_python as obs
import colorsys
import json


#--------------------------------------------------
#このソフトができること
#起動時に指定したURL先に投げられたギフト情報を取得
#ローカルサーバーのマインクラフトにコマンドを送信
#サーバーの指定方法はIPアドレスとポート番号
#グローバルサーバーに対応予定
#受け取ったギフト情報を使ってマインクラフトサーバーにコマンドを送信
#--------------------------------------------------
combo_counter = 0
last_update_time = 0
#--------------------------------------------------

# バックグラウンドで動くコマンドワーカー
async def command_worker():
    await cwm.command_worker_mod()


async def combo_system():
    await c_sys.combo_system_mod()





class TikTokLiveManager:
    def __init__(self,tiktok_user_id):
        self.client = TikTokLiveClient(unique_id=tiktok_user_id)
        # 日付文字列を作成
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # ファイル名を作成
        self.DATA_FILE = f"data_{tiktok_user_id}_{date_str}.json"
        self.gifts_data = {}
        self.register()

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                self.gifts_data = json.load(f)
            print("💾 データをロードしました")
        else:
            self.gifts_data = {}



    def save_data(self):
        sorted_data = dict(sorted(self.gifts_data.items(), key=lambda x: x[1], reverse=False))  # 昇順
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        print("💾 データを保存しました")





    async def add_gift(self,name, coins):
        if name not in self.gifts_data:  # 未登録なら追加
            self.gifts_data[name] = coins
            print(f"✅ 新しいギフトを保存しました: {name} - {coins}コイン")


    async def start_client_session(self):
        """クラス内の main 的なメソッド"""
        self.load_data()              # データロード
        try:
            await self.client.connect()  # TikTok に接続（非同期）
        except UserOfflineError:
            print("⚠️ 配信者がオフラインです。")
        finally:
            self.save_data()


    # TikTokのユーザー名
    # name = input("TikTokのユーザー名を入力してください（@は不要）: ") or config.name
    # client = TikTokLiveClient(unique_id=name)
    # print(name)
    # マイクラのプレイヤー名
    def register(self):
        from TikTokLive.events import LikeEvent,FollowEvent,CommentEvent,GiftEvent,LinkMicBattleEvent,LinkmicAnimationEvent,LinkMicAdEvent,LinkMicBattleVictoryLapEvent,LinkMicBattleVictoryLapEvent,LinkMicSignalingMethodEvent,LinkMicSignalingMethodEvent,LinkMicBattlePunishFinishEvent,LinkmicAudienceNoticeEvent,LinkMicBattleItemCardEvent,LinkmicBattleTaskEvent,LinkMicAnchorGuideEvent,LinkmicBattleNoticeEvent,LinkMicArmiesEvent,LinkMicFanTicketMethodEvent,LinkMicMethodEvent
        # streamer_ID = self.client.unique_id
    # いいねを受け取った時
        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            # print("配信者ID：",self.client.unique_id)
            await m_intr_c.on_like_mod(event,self.client.unique_id)


        # フォローを受け取った時
        @self.client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            await m_intr_c.on_follow_mod(event,self.client.unique_id)
            # print("thx follow ",event.user.nickname)

        # コメントを受け取ったとき
        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            await m_intr_c.on_comment_mod(event,self.client.unique_id)

        # ギフトを受け取ったとき
        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            for i in range(config.current_multiplier):
                await m_intr_c.on_gift_mod(event,self.client.unique_id)
            if event.gift.streakable and not event.streaking or not event.gift.streakable:
                await self.add_gift(event.gift.name, event.gift.diamond_count)

class Tiktok_Client:
    def __init__(self, unique_id):
        self.unique_id = unique_id

class Gift:
    def __init__(self, name, diamond_count,streakable):
        self.name = name
        self.diamond_count = diamond_count
        self.streakable = streakable

class User:
    def __init__(self, nickname):
        self.nickname = nickname

class GiftEvent:
    def __init__(self, client, user, gift, repeat_count, streaking):
        self.client = client
        self.user = user
        self.gift = gift
        self.repeat_count = repeat_count
        self.streaking = streaking
class RepeatCount:
    def __init__(self, times):
        self.repeat_count = times
    def __int__(self):
        return self.repeat_count
    def __str__(self):
        return str(self.repeat_count)

class CheckStraking:
    def __init__(self, streaking):
        self.streaking = streaking
    def __str__(self):
        return str(self.streaking)  # print したとき "True" か "False"

    def __bool__(self):
        return self.streaking

class MinecraftTest:
    def __init__(self):
        self.client = Tiktok_Client("muzukiray963")
        self.user = User("test_user_3699")
        self.gift = Gift("Heart Me", 9,True)
        self.repeat_count = RepeatCount(1)
        self.streaking = CheckStraking(False)
        args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
        self.event = GiftEvent(*args)

    async def test_input_cord(self):
        while True:
            test_message = """
            使用方法

            # ギフトを変更
            self.gift.name = "Diamond"
            self.repeat_count = RepeatCount(1)
            self.gift.streakable = True

            # args に最新状態を反映させる
            args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)

            # GiftEvent を更新
            self.event = GiftEvent(*args)



            self.client = Tiktok_Client("muzukiray963")
            self.user = User("test_user_3699")
            self.gift = Gift("Heart Me", 9,True)
            self.repeat_count = RepeatCount(1)
            self.streaking = CheckStraking(False)
            args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
            self.event = GiftEvent(*args)



            # 実行するとき
            asyncio.create_task(m_intr_c.on_gift_mod(self.event, self.client.unique_id))
            """
            print(test_message)
            for i in range(3):
                print("=== テストプログラム ===")

            test_code = await asyncio.to_thread(input,"I wait enter...>>>")
            if test_code.strip().lower() == "exit":
                print("テスト終了")
                break
            try:
                exec(test_code)
            except Exception as e:
                print("エラー:",e)
async def main():
    # ワーカー開始
    test_message = """
    使用方法

    # ギフトを変更
    self.gift.name = "Diamond"
    self.repeat_count = RepeatCount(1)
    self.gift.streakable = True

    # args に最新状態を反映させる
    args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)

    # GiftEvent を更新
    self.event = GiftEvent(*args)
    
    # 実行するとき
    asyncio.create_task(m_intr_c.on_gift_mod(self.event, self.client.unique_id))
    """
    print(test_message)
    for i in range(3):
        print("=== テストプログラム ===")


    is_use_obs = input("OBSを使いますか？ (y/n): ").lower() == "y"
    is_use_minecraft = input("Minecraftを使いますか？ (y/n): ").lower() == "y"

    if is_use_obs:
        config.obs_client = obs.ReqClient(config.HOST, config.PORT, config.PASSWORD)
        await setup.setup_scene_and_source(config.obs_client, config.SCENE_NAME, config.SOURCES_NAMES)
        asyncio.create_task(combo_system())

    if is_use_minecraft:
        asyncio.create_task(command_worker())

    test_env = MinecraftTest()
    # ここで REPL を開始
    await test_env.test_input_cord()

    # # TikTok アカウント登録
    # tiktok_usernames = []
    # while True:
    #     user = input("TikTokのユーザーIDを入力してください（@は不要）: ").strip()
    #     if user:
    #         tiktok_usernames.append(user)
    #     else:
    #         print("入力が空です。スキップします。")

    #     more = input("さらにユーザーを追加しますか？ (y/n): ").lower()
    #     if more != "y":
    #         break

    # print("登録されたユーザー:", tiktok_usernames)

    # # 各ユーザーごとにマネージャー作成
    # managers = [TikTokLiveManager(user) for user in tiktok_usernames]

    # # 全員同時接続
    # try:
    #     if len(managers) == 1:
    #         # 1人だけなら直接 await
    #         await managers[0].start_client_session()
    #     elif len(managers) > 1:
    #         # 複数なら gather で並列実行
    #         await asyncio.gather(*(m.start_client_session() for m in managers))
    # except UserOfflineError:
    #     print("⚠️ 配信者がオフラインです。配信を開始してください。")
    #     print("\n✅ 📺配信が終了しました。お疲れさまでした…💤")

# 実行開始
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました。配信お疲れ様でした。")
        input("Enterキーを押して閉じてください…")


