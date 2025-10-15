

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
from modules import receive
from modules import workers
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


import atexit
import signal
import sys
import os
import csv
from datetime import date
import platform
import aiofiles
import win32api
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
# log_queue = asyncio.queue()

async def boot_workers():
    # await cwm.command_worker_mod()
    await workers.coin_total_count_worker()

async def combo_system():
    await c_sys.combo_system_mod()




class TikTokLiveManager:
    def __init__(self,tiktok_user_id,base_dir="logs"):
        self.client = TikTokLiveClient(unique_id=tiktok_user_id)
        self.base_dir=base_dir
        os.makedirs(base_dir, exist_ok=True)
        # 今月用ファイル
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

        # イベント受けとり
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
            # self.save_data()
            print('FINI')

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
            await receive.on_like_mod(event,self.client.unique_id)


        # フォローを受け取った時
        @self.client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            await receive.on_follow_mod(event,self.client.unique_id)
            # print("thx follow ",event.user.nickname)

        # コメントを受け取ったとき
        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            await receive.on_comment_mod(event,self.client.unique_id)

        # ギフトを受け取ったとき
        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            for i in range(config.current_multiplier):
                await receive.on_gift_mod(event,self.client.unique_id)
            if event.gift.streakable and not event.streaking :
                # await self.add_gift(event.gift.name, event.gift.diamond_count)
                self.log(event.user.nickname,event.gift.name,event.gift.diamond_count*event.repeat_count)
            if not event.gift.streakable:
                self.log(event.user.nickname,event.gift.name,event.gift.diamond_count*event.repeat_count)

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
            if event.action.name == "BATTLE_ACTION_FINISH":
                print("バトル終了…")
            print(event.battle_result)
            # print(event.m_battle_display_config)
            # print(event.invitee_gift_permission_type)　必ず存在するわけではないらしい。最後に見たときに記載があったのはLinkmicBattleNoticeEvent 2025-09-19 03:25:44
            # print(event.armies)
            # print(event.anchor_info)
            # print(event.bubble_text)
            # print(event.supported_actions)
            # print(event.battle_combos)
            # print(event.team_users)
            # print(event.invitee_gift_permission_types)
            # print(event.action_by_user_id)
            # print(event.team_battle_result)
            # print(event.team_armies)
            # print(event.abtest_settings)
            # print(event.team_match_campaign)
            # print(event.fuzzy_display_config_v2)
            # バトル開始時と終了時

        @self.client.on(LinkmicAnimationEvent)
        async def Linkmic_Animation_Event(event: LinkmicAnimationEvent):
            now = datetime.now()
            print(f"LinkmicAnimationEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)

        @self.client.on(LinkMicAdEvent)
        async def LinkMic_Ad_Event(event: LinkMicAdEvent):
            now = datetime.now()
            print(f"LinkMicAdEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)
        @self.client.on(LinkMicBattleVictoryLapEvent)
        async def LinkMic_Battle_Victory_LapEvent(event: LinkMicBattleVictoryLapEvent):
            now = datetime.now()
            print(f"LinkMicBattleVictoryLapEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"勝利の時間ってやつ？")
            # print(event)

        @self.client.on(LinkMicSignalingMethodEvent)
        async def LinkMic_Signaling_Method_Event(event: LinkMicSignalingMethodEvent):
            now = datetime.now()
            print(f"LinkMicSignalingMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)

        @self.client.on(LinkMicBattlePunishFinishEvent)
        async def LinkMic_Battle_PunishFinish_Event(event: LinkMicBattlePunishFinishEvent):
            now = datetime.now()
            print(f"LinkMicBattlePunishFinishEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"バトルで負けたとき？")
            # print(event)

        @self.client.on(LinkmicAudienceNoticeEvent)
        async def Linkmic_Audience_NoticeEvent(event: LinkmicAudienceNoticeEvent):
            now = datetime.now()
            print(f"LinkmicAudienceNoticeEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)

        @self.client.on(LinkMicBattleItemCardEvent)
        async def LinkMic_Battle_ItemCard_Event(event: LinkMicBattleItemCardEvent):
            now = datetime.now()
            print(f"LinkMicBattleItemCardEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)

        @self.client.on(LinkmicBattleTaskEvent)
        async def LinkMic_Battle_Task_Event(event: LinkmicBattleTaskEvent):
            now = datetime.now()
            print(f"LinkmicBattleTaskEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"スピードチャレンジについて")
            # print(event.base_message)
            # if event._battle_task_message_type is not None:
            #     print(event.battle_task_message_type)
            # else:
            #     print("battle_task_message_type は None です")
                # print(event.battle_task_message_type)
            print(event.task_start.battle_bonus_config.preview_period_config)
            # print(first_prompt_key))
            print(event.task_start)
            print(event.task_update)
            print(event.task_settle)
            print(event.reward_settle)
            print(event.battle_id)
            # print(event)
            # 開始時と終了時に、発火
            # スピードチャレンジタスク開始時、解決時、未解決時、スピードチャレンジ開始時、終了時
        @self.client.on(LinkMicAnchorGuideEvent)
        async def LinkMic_Anchor_Guide_Event(event: LinkMicAnchorGuideEvent):
            now = datetime.now()
            print(f"LinkMicAnchorGuideEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"ラスト10秒？")
            print(f"ユーザー：{event.user.nickname}…多分")
            # print(event)

        @self.client.on(LinkmicBattleNoticeEvent)
        async def Linkmic_Battle_Notice_Event(event: LinkmicBattleNoticeEvent):
            now = datetime.now()
            print(f"LinkmicBattleNoticeEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)
            # バトル開始時
        @self.client.on(LinkMicArmiesEvent)
        async def LinkMic_Armies_Event(event: LinkMicArmiesEvent):
            now = datetime.now()
            # print(f"LinkMicArmiesEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event.base_message)
            # print(event.battle_id)
            # print(event.armies)
            # print(event.channel_id)
            # print(event.gift_sent_time)
            # print(event.score_update_time)
            # print(event.trigger_reason)
            # print(event.from_user_id)
            # print(event.gift_id)
            # print(event.gift_count)
            # print(event.gif_icon_image)
            # print(event.total_diamond_count)
            # print(event.repeat_count)
            # print(event.team_armies)
            # print(event.trigger_critical_strike)
            # print(event.has_team_match_mvp_sfx)
            # print(event.log_id)
            # print(event.battle_settings)
            # print(event.fuzzy_display_config_v2)
        # 配信にいてバトルに参加している人の情報、画像やらギフトやら、うまく使えば、バトル終了時に、貢献者１位２位３位とか表示できるかも？
        # バトルしてる配信に入っただけで、強制的に反応しそう？どのタイミングで反応するんだろうか？trigger_reason...トリガー理由…
        @self.client.on(LinkMicFanTicketMethodEvent)
        async def LinkMic_FanTicket_Method_Event(event: LinkMicFanTicketMethodEvent):
            now = datetime.now()
            print(f"LinkMicFanTicketMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)
            # ギフトが投げられたとき、反応した
            # 特殊ギフトが投げられたとき。例えば、ハートミー。ファンクラブ系統のギフトが投げられると反応する。

        @self.client.on(LinkMicMethodEvent)
        async def LinkMicMethodEvent(event: LinkMicMethodEvent):
            now = datetime.now()
            print(f"LinkMicMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(event)
            # ギフトが投げられたとき、反応した
            # for attr in [
            #     "base_message", "m_type", "access_key", "anchor_link_mic_id", "user_id",
            #     "fan_ticket", "total_fan_ticket", "channel_id", "layout", "vendor",
            #     "dimension", "theme", "invite_uid", "reply", "duration", "match_type",
            #     "win", "prompts", "to_user_id", "tips", "start_time_ms", "confluence_type",
            #     "from_room_id", "invite_type", "sub_type", "rtc_ext_info", "app_id",
            #     "app_sign", "anchor_link_mic_id_str", "rival_anchor_id", "rival_linkmic_id",
            #     "rival_linkmic_id_str", "should_show_popup", "rtc_join_channel", "fan_ticket_type"
            #     ]:
            #     print(attr, "=", getattr(event, attr, None))
            # print(event.base_message)
            # print(event.m_type)
            # print(event.access_key)
            # print(event.anchor_link_mic_id)
            # print(event.user_id)
            # print(event.fan_ticket)
            # print(event.total_fan_ticket)
            # print(event.channel_id)
            # print(event.layout)
            # print(event.vendor)
            # print(event.dimension)
            # print(event.theme)
            # print(event.invite_uid)
            # print(event.reply)
            # print(event.duration)
            # print(event.match_type)
            # print(event.win)
            # print(event.prompts)
            # print(event.to_user_id)
            # print(event.tips)
            # print(event.start_time_ms)
            # print(event.confluence_type)
            # print(event.from_room_id)
            # print(event.invite_type)
            # print(event.sub_type)
            # print(event.rtc_ext_info)
            # print(event.app_id)
            # print(event.app_sign)
            # print(event.anchor_link_mic_id_str)
            # print(event.rival_anchor_id)
            # print(event.rival_linkmic_id)
            # print(event.rival_linkmic_id_str)
            # print(event.should_show_popup)
            # print(event.rtc_join_channel)
            # print(event.fan_ticket_type)

async def main():
    # ワーカー開始
    is_use_obs = input("OBSを使いますか？ (y/n): ").lower() == "y"

    if is_use_obs:
        config.obs_client = obs.ReqClient(config.HOST, config.PORT, config.PASSWORD)
        await setup.setup_scene_and_source(config.obs_client, config.SCENE_NAME, config.SOURCES_NAMES)
        asyncio.create_task(combo_system())

    # TikTok アカウント登録
    tiktok_usernames = []
    while True:
        user = input("TikTokのユーザーIDを入力してください（@は不要）: ").strip()
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

# 実行開始
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました。配信お疲れ様でした。")
        input("Enterキーを押して閉じてください…")


