

# MIT License
# Copyright (c) 2024 Isaac Kogan
# Copyright (c) 2025 Nemesis-Nocturnal-Ray963

#
# This file is part of software distributed under the MIT License.
# See the LICENSE file in the project root for full license information.
import sys, os, asyncio, json, csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from TikTokLive import TikTokLiveClient
from TikTokLive.events import *
from TikTokLive.client.errors import UserOfflineError
from modules import config, setup, receive
from modules import minecraft_interactive_command as m_intr_c
from modules import command_worker_mod as cwm
from modules import combo_system as c_sys
from modules import arcade_system_alpha
import obsws_python as obs
from multiprocessing import Process,Queue


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
class TikTokLiveManager:
    def __init__(self,tiktok_user_id,base_dir="logs"):
        self.client = TikTokLiveClient(unique_id=tiktok_user_id)
        # self.enable_visuals = tiktok_user_id in config.VISUAL_ENABLED_USERS  # ←特定のIDのみ演出ON
        # if self.enable_visuals:
        shared_queue = Queue()
        self.arcade_process = Process(target=arcade_system_alpha.run,args=(shared_queue,), daemon=True)
        self.arcade_process.start()
        m_intr_c.arcade_queue = shared_queue
            
            
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        today = date.today()
        self.filename = os.path.join(base_dir, f"{tiktok_user_id}_{today.year}-{today.month:02d}.csv")
        # メモリ上にデータを保持
        self.data = []

        # ファイルがあればロード
        if os.path.exists(self.filename):
            with open(self.filename, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        else:
            # 新規ファイルならヘッダー作成
            with open(self.filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["日付", "ユーザー", "ギフト名","合計コイン数"])
                writer.writeheader()

        # キューとワーカー
        self.queue = asyncio.Queue()
        asyncio.create_task(self._log_save_worker())  # バックグラウンドで保存

        self.register()

    async def _log_save_worker(self):
        """キューに入ったログを逐次CSVに追記"""
        print("boot _log_save_worker...")
        while True:
            item = await self.queue.get()
            with open(self.filename, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["日付", "ユーザー", "ギフト名","合計コイン数"])
                writer.writerow(item)
            print("sava now...")
    def log(self, user_name,gift_name,total_coin):
        today = date.today()
        item = ({"日付": str(today), "ユーザー": user_name,"ギフト名":gift_name,"合計コイン数":total_coin})
        self.data.append(item)
        # キューに追加

        self.queue.put_nowait(item)




    async def start_client_session(self):
        """クラス内の main 的なメソッド"""
        # self.load_data()              # データロード
        try:
            await self.client.connect()  # TikTok に接続（非同期）
        except UserOfflineError:
            print("⚠️ 配信者がオフラインです。")
        finally:
            print('FINI')


    # TikTokのユーザー名
    # name = input("TikTokのユーザー名を入力してください（@は不要）: ") or config.name
    # client = TikTokLiveClient(unique_id=name)
    # print(name)
    # マイクラのプレイヤー名
    def register(self):
        # from TikTokLive.events import LikeEvent,FollowEvent,CommentEvent,GiftEvent,LinkMicBattleEvent,LinkmicAnimationEvent,LinkMicAdEvent,LinkMicBattleVictoryLapEvent,LinkMicBattleVictoryLapEvent,LinkMicSignalingMethodEvent,LinkMicSignalingMethodEvent,LinkMicBattlePunishFinishEvent,LinkmicAudienceNoticeEvent,LinkMicBattleItemCardEvent,LinkmicBattleTaskEvent,LinkMicAnchorGuideEvent,LinkmicBattleNoticeEvent,LinkMicArmiesEvent,LinkMicFanTicketMethodEvent,LinkMicMethodEvent
        from TikTokLive.events import (
            LikeEvent, FollowEvent, CommentEvent, GiftEvent,
            LinkMicBattleEvent, LinkmicAnimationEvent, LinkMicAdEvent,
            LinkMicBattleVictoryLapEvent, LinkMicSignalingMethodEvent,
            LinkMicBattlePunishFinishEvent, LinkmicAudienceNoticeEvent,
            LinkMicBattleItemCardEvent, LinkmicBattleTaskEvent,
            LinkMicAnchorGuideEvent, LinkmicBattleNoticeEvent,
            LinkMicArmiesEvent, LinkMicFanTicketMethodEvent, LinkMicMethodEvent
        )
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
            for _ in range(config.current_multiplier):
                print("got gift...")
                # await m_intr_c.on_gift_mod(event,self.client.unique_id)
            # ログ追記
            if (event.gift.streakable and not event.streaking) or (not event.gift.streakable):
                total_coin = event.gift.diamond_count * int(event.repeat_count)
                self.log(event.user.nickname, event.gift.name, total_coin)



        @self.client.on(LinkMicBattleEvent)
        async def on_battle(event: LinkMicBattleEvent):
            print("バトルについて")
            print(event.base_message)
            print(event.battle_id)
            print(event.battle_setting)
            print(event.action)
            battle_action = event.action
            print(type(battle_action), battle_action)
            # enumオブジェクト は name や value 属性を持っている
            if event.action.name == "BATTLE_ACTION_OPEN":
                print("バトル開始ッ…！")
                await m_intr_c.on_battle_start(event,self.client.unique_id)
            if event.action.name == "BATTLE_ACTION_FINISH":
                print("バトル終了…")
                await m_intr_c.on_battle_end(event,self.client.unique_id)
            print(event.battle_result)



class Tiktok_Client:
    "this is use TestSystem"
    def __init__(self, unique_id):
        self.unique_id = unique_id

class Gift:
    "this is use TestSystem"
    def __init__(self, name, diamond_count,streakable):
        self.name = name
        self.diamond_count = diamond_count
        self.streakable = streakable

class User:
    "this is use TestSystem"
    def __init__(self, nickname):
        self.nickname = nickname

class GiftEvent:
    "this is use TestSystem"
    def __init__(self, client, user, gift, repeat_count, streaking):
        self.client = client
        self.user = user
        self.gift = gift
        self.repeat_count = repeat_count
        self.streaking = streaking
class RepeatCount:
    "this is use TestSystem"
    def __init__(self, times):
        self.repeat_count = times
    def __int__(self):
        return self.repeat_count
    def __str__(self):
        return str(self.repeat_count)

class CheckStraking:
    "this is use TestSystem"
    def __init__(self, streaking):
        self.streaking = streaking
    def __str__(self):
        return str(self.streaking)  # print したとき "True" か "False"

    def __bool__(self):
        return self.streaking

class TestSystem:
    "this is use TestSystem"
    def __init__(self):
        self.client = Tiktok_Client("muzukiray963")
        self.user = User("test_user_3699")
        self.gift = Gift("test_icosa_1", 1337,True)
        self.repeat_count = RepeatCount(1)
        self.streaking = CheckStraking(False)
        args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
        self.event = GiftEvent(*args)
        
        shared_queue = Queue()
        self.arcade_process = Process(target=arcade_system_alpha.run,args=(shared_queue,), daemon=True)
        self.arcade_process.start()
        
        m_intr_c.arcade_queue = shared_queue
        
    async def change_gift(self,gift_name,coin,streakings):
        self.gift = Gift(gift_name,coin,streakings)
        args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
        self.event = GiftEvent(*args)
# print(arcade_system_alpha.arcade_queue.qsize())
        
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

便利関数
change_gift
入力引数：ギフト名,コイン数,連続可能ギフト(True or False)
await self.change_gift(gift_name,coin,streakings)
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


    is_test = input("test mode? (y/n)").lower() == "y"
    is_use_obs = input("OBSを使いますか？ (y/n): ").lower() == "y"
    is_use_minecraft = input("Minecraftを使いますか？ (y/n): ").lower() == "y"

    is_test = input("test mode? (y/n)").lower() == "y"
    is_use_obs = input("OBSを使いますか？ (y/n): ").lower() == "y"
    is_use_minecraft = input("Minecraftを使いますか？ (y/n): ").lower() == "y"

    config.is_test = is_test
    if is_use_obs:
        config.obs_client = obs.ReqClient(config.HOST, config.PORT, config.PASSWORD)
        await setup.setup_scene_and_source(config.obs_client, config.SCENE_NAME, config.SOURCES_NAMES)
        asyncio.create_task(combo_system())

    if is_use_minecraft:
        asyncio.create_task(command_worker())
    else:
        config.is_minecraft_server_connect = is_use_minecraft

    if is_test:
        for i in range(3):
            print("=== テストプログラム ===")
        test_env = TestSystem()
        # ここで REPL を開始
        await test_env.test_input_cord()
    else:
        # TikTok アカウント登録
        tiktok_usernames = []
        while True:
            user = input("TikTokのユーザーIDを入力してください（@は不要）ちなみにkai.mirena: ").strip()
            if user:
                tiktok_usernames.append(user)
            else:
                print("入力が空です。スキップします。")

            more = input("さらにユーザーを追加しますか？ (y/n): ").lower()
            if more != "y":
                break

        print("登録されたユーザー:", tiktok_usernames)

        # 各ユーザーごとにマネージャー作成
        managers = [TikTokLiveManager(user) for user in tiktok_usernames]

        # 全員同時接続
        try:
            if len(managers) == 1:
                # 1人だけなら直接 await
                await managers[0].start_client_session()
            elif len(managers) > 1:
                # 複数なら gather で並列実行
                await asyncio.gather(*(m.start_client_session() for m in managers))
        except UserOfflineError:
            print("⚠️ 配信者がオフラインです。配信を開始してください。")
            print("\n✅ 📺配信が終了しました。お疲れさまでした…💤")
    
    print("====== main finish line... ======")

# 実行開始
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました。配信お疲れ様でした。")
        input("Enterキーを押して閉じてください…")


