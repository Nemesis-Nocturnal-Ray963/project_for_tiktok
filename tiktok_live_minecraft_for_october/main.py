

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
from TikTokLive.events import * # CommentEvent, GiftEvent, FollowEvent, LikeEvent
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


async def main():
    # ワーカー開始
    is_use_obs = input("OBSを使いますか？ (y/n): ").lower() == "y"
    is_use_minecraft = input("Minecraftを使いますか？ (y/n): ").lower() == "y"

    if is_use_obs:
        config.obs_client = obs.ReqClient(config.HOST,config.PORT,config.PASSWORD)
        await setup.setup_scene_and_source(config.obs_client,config.SCENE_NAME,config.SOURCES_NAMES)
        asyncio.create_task(combo_system())
    if is_use_minecraft:
        asyncio.create_task(command_worker())
    # TikTok 接続（イベントループ内で動く）
        # TikTokクライアント起動
    try:
        load_data()
        await client.connect()
    except UserOfflineError:
        print("⚠️ 配信者がオフラインです。配信を開始してください。")
        print("\n✅ 📺配信が終了しました。お疲れさまでした…💤")
        print("y を押して、Enterで閉じます")
    finally:
        save_data()
#--------------------------------------------------
DATA_FILE = config.data_file_default
gifts_data = {}
def load_data():
    global gifts_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            gifts_data = json.load(f)
        print("💾 データをロードしました")
    else:
        gifts_data = {}



def save_data():
    sorted_data = dict(sorted(gifts_data.items(), key=lambda x: x[1], reverse=False))  # 昇順
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print("💾 データを保存しました")





def add_gift(name, coins):
    if name not in gifts_data:  # 未登録なら追加
        gifts_data[name] = coins
        print(f"✅ 新しいギフトを保存しました: {name} - {coins}コイン")





# TikTokのユーザー名
name = input("TikTokのユーザー名を入力してください（@は不要）: ") or config.name
client = TikTokLiveClient(unique_id=name)
print(name)
# マイクラのプレイヤー名

# いいねを受け取った時
@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    await m_intr_c.on_like_mod(event)


# フォローを受け取った時
@client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    await m_intr_c.on_follow_mod(event)
    print("thx follow ",event.user.nickname)

# コメントを受け取ったとき
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    await m_intr_c.on_comment_mod(event)

# ギフトを受け取ったとき
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    for i in range(config.current_multiplier):
        await m_intr_c.on_gift_mod(event)
    if event.gift.streakable and not event.streaking or not event.gift.streakable:
        add_gift(name, event.gift.diamond_count)
        




@client.on(LinkMicBattleEvent)
async def on_battle(event: LinkMicBattleEvent):
    print("バトルについて")
    print(event.base_message)
    print(event.battle_id)
    print(event.battle_setting)
    print(event.action)
    print(event.battle_result)
    print(event.m_battle_display_config)
    # print(event.invitee_gift_permission_type)　必ず存在するわけではないらしい。最後に見たときに記載があったのはLinkmicBattleNoticeEvent 2025-09-19 03:25:44
    print(event.armies)
    print(event.anchor_info)
    print(event.bubble_text)
    print(event.supported_actions)
    print(event.battle_combos)
    print(event.team_users)
    print(event.invitee_gift_permission_types)
    print(event.action_by_user_id)
    print(event.team_battle_result)
    print(event.team_armies)
    print(event.abtest_settings)
    print(event.team_match_campaign)
    print(event.fuzzy_display_config_v2)
    # バトル開始時と終了時

@client.on(LinkmicAnimationEvent)
async def Linkmic_Animation_Event(event: LinkmicAnimationEvent):
    now = datetime.now()
    print(f"LinkmicAnimationEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)

@client.on(LinkMicAdEvent)
async def LinkMic_Ad_Event(event: LinkMicAdEvent):
    now = datetime.now()
    print(f"LinkMicAdEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)
@client.on(LinkMicBattleVictoryLapEvent)
async def LinkMic_Battle_Victory_LapEvent(event: LinkMicBattleVictoryLapEvent):
    now = datetime.now()
    print(f"LinkMicBattleVictoryLapEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"勝利の時間ってやつ？")
    # print(event)

@client.on(LinkMicSignalingMethodEvent)
async def LinkMic_Signaling_Method_Event(event: LinkMicSignalingMethodEvent):
    now = datetime.now()
    print(f"LinkMicSignalingMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)

@client.on(LinkMicBattlePunishFinishEvent)
async def LinkMic_Battle_PunishFinish_Event(event: LinkMicBattlePunishFinishEvent):
    now = datetime.now()
    print(f"LinkMicBattlePunishFinishEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"バトルで負けたとき？")
    # print(event)

@client.on(LinkmicAudienceNoticeEvent)
async def Linkmic_Audience_NoticeEvent(event: LinkmicAudienceNoticeEvent):
    now = datetime.now()
    print(f"LinkmicAudienceNoticeEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)

@client.on(LinkMicBattleItemCardEvent)
async def LinkMic_Battle_ItemCard_Event(event: LinkMicBattleItemCardEvent):
    now = datetime.now()
    print(f"LinkMicBattleItemCardEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)

@client.on(LinkmicBattleTaskEvent)
async def LinkMic_Battle_Task_Event(event: LinkmicBattleTaskEvent):
    now = datetime.now()
    print(f"LinkmicBattleTaskEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"スピードチャレンジについて")
    print(event.base_message)
    print(event.battle_task_message_type)
    print(event.task_start)
    print(event.task_update)
    print(event.task_settle)
    print(event.reward_settle)
    print(event.battle_id)
    # print(event)
    # 開始時と終了時に、発火
    # スピードチャレンジタスク開始時、解決時、未解決時、スピードチャレンジ開始時、終了時 
@client.on(LinkMicAnchorGuideEvent)
async def LinkMic_Anchor_Guide_Event(event: LinkMicAnchorGuideEvent):
    now = datetime.now()
    print(f"LinkMicAnchorGuideEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ラスト10秒？")
    print(f"ユーザー：{event.user.nickname}…多分")
    # print(event)

@client.on(LinkmicBattleNoticeEvent)
async def Linkmic_Battle_Notice_Event(event: LinkmicBattleNoticeEvent):
    now = datetime.now()
    print(f"LinkmicBattleNoticeEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)
    # バトル開始時
@client.on(LinkMicArmiesEvent)
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
@client.on(LinkMicFanTicketMethodEvent)
async def LinkMic_FanTicket_Method_Event(event: LinkMicFanTicketMethodEvent):
    now = datetime.now()
    print(f"LinkMicFanTicketMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)
    # ギフトが投げられたとき、反応した
    # 特殊ギフトが投げられたとき。例えば、ハートミー。ファンクラブ系統のギフトが投げられると反応する。

@client.on(LinkMicMethodEvent)
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


# 実行開始
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました。配信お疲れ様でした。")
        input("Enterキーを押して閉じてください…")


