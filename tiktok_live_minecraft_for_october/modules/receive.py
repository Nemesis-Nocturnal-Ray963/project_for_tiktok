import sys
import os
print("//sys.path")
print(sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import setup,config,receive,VRPG_system

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

#いいね関連



# @client.on(LikeEvent)
# async def on_like(event: LikeEvent):
#     # global total_likes
#     user_id = event.user.unique_id

#     # 個別カウント更新
#     if user_id not in config.user_like_count:
#         config.user_like_count[user_id] = 0

#     config.user_like_count[user_id] += 1

#     # 全体カウント更新
#     config.total_likes += 1

#     # 個別ユーザーのイベント
#     if config.user_like_count[user_id] > config.USER_LIKE_THRESHOLD:
#         #ログ　
#         now = datetime.now()
#         print(f"🎉 {event.user.nickname} reached {config.user_like_count[user_id]} likes!")
#         print(f"{event.user.nickname} ({user_id}) liked at {now.strftime('%Y-%m-%d %H:%M:%S')}")
#         # ここにRCONや通知処理を追加可能
#         await config.command_queue.put(f'title @a title {{"text":"{config.USER_LIKE_THRESHOLD}いいねTNT"}}')
#         await config.command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
#         await config.command_queue.put(f"bedrock tnt 1 {event.user.nickname}")
#         config.user_like_count[user_id] = 0

#     # 全体累計のイベント
#     if config.total_likes > config.TOTAL_LIKE_THRESHOLD:
#         #ログ　
#         now = datetime.now()
#         print(f"🌟 Total likes reached {config.total_likes}!")
#         print(f"User total: {config.user_like_count[user_id]}, Global total: {config.total_likes}")
#         # ここにRCONや通知処理を追加可能
#         await config.command_queue.put(f'title @a title {{"text":"{config.TOTAL_LIKE_THRESHOLD}いいね爆撃"}}')
#         await config.command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
#         for i in range(150):
#             await config.command_queue.put(f"bedrock tnt 1 {event.user.nickname}")
#             await asyncio.sleep(0.075)
#         config.total_likes = 0



#--------------------------------------------------
#フォロー関連
# すでに反応済みのユーザーを保持するセット
already_triggered = set()
#  フォローを受け取った時
async def handle_follow(event: FollowEvent):
    user_id = event.user.unique_id
    if user_id not in already_triggered:
        already_triggered.add(user_id)
        await config.command_queue.put(f"bedrock tnt 3 {event.user.nickname}")
        await config.command_queue.put('title @a title {"text":"§cフォロー、ありがとう！"}')
        await config.command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')

    # コメントを受け取ったとき
async def handle_comment(event: CommentEvent):
    now = datetime.now()
    print(f"{event.user.nickname} >> {event.comment}"f" at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # --- 個別処理を関数化 ---
async def blank_info(user,giftname):
    print(f"name:{user}  gift:{giftname}")
async def heart_me(user):
    print(f"{user} send Heart Me...")
async def spawn_tnt(user, count, delay=0.1):
    await config.command_queue.put('title @a title {"text":"1TNT"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await config.command_queue.put(f"bedrock tnt 1 {user}")
        await asyncio.sleep(delay)

async def spawn_multi_tnt(user, count, per, delay):
    await config.command_queue.put(f'title @a title {{"text":"{per}TNT"}}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await config.command_queue.put(f"bedrock tnt {per} {user}")
        await asyncio.sleep(delay)


async def spawn_donuts_tnt(user, count, per, delay):
    await config.command_queue.put(f'title @a title {{"text":"{per * 2}TNT"}}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await config.command_queue.put(f"bedrock tnt {per} {user}")
        await asyncio.sleep(delay)

async def summon_zombies(user, count):
    await config.command_queue.put('title @a title {"text":"ゾンビのお友達～"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    for z in range(count):
        for i in range(15):
            await config.command_queue.put(
                f'execute at @a run summon zombie ~ ~3 ~ '
                f'{{IsBaby:0,ArmorItems:[{{}},{{}},{{}},{{id:"minecraft:carved_pumpkin",Count:1}}],'
                f'ArmorDropChances:[0F,0F,0F,0F],'
                f'CustomName:"{user}の分身",CustomNameVisible:1}}'
            )
            await asyncio.sleep(0.05)

async def levitation_effect(user,count,delay):
    await config.command_queue.put('title @a title {"text":"浮遊"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await config.command_queue.put(f"effect give @a minecraft:levitation {delay} 2")
        await asyncio.sleep(delay)

async def fill_blocks(user,count):
    await config.command_queue.put('title @a title {"text":"§c400ブロック埋めたて"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"ありがとう、{user}"}}')
    for i in range(count):
        await config.command_queue.put("bedrock fillblock 400")
    await asyncio.sleep(1)

async def fill_area(user):
    await config.command_queue.put('title @a title {"text":"§c埋立完了!"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"ありがとう! {user}"}}')
    await config.command_queue.put("bedrock fill")
    await asyncio.sleep(1)

async def corgi_messege(user):
    await config.command_queue.put('title @a title {"text":"とにかく荒らせ!"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')

async def mishka_storm(user):
    await config.command_queue.put('title @a title {"text":"§cTNTの嵐"}')
    await config.command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    await asyncio.sleep(3.20)
    for i in range(165):
        await config.command_queue.put("bedrock tnt 2")
        await asyncio.sleep(0.05)


    # ギフトを受け取ったとき

async def handle_gift(event: GiftEvent):
    # global gift_counter
    #ギフトを受け取るたびに取得する情報
    user = event.user.nickname
    name = event.gift.name
    attack_time = event.repeat_count
    gift_coin = event.gift.diamond_count
    #ログ用
    now = datetime.now()

    # streak 終了時のみ処理
    if event.gift.streakable and not event.streaking or not event.gift.streakable:
        config.gift_counter += event.repeat_count
        print(f"{user} sent a {name} (x{event.repeat_count}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        if config.is_running_vrpg:
            attack = await VRPG_system.get_attack_by_gift(name)
            if attack:
                await VRPG_system.calculate_system(user, name, attack_time,attack["id"])
                print("current_attacks:", [a['gift'] for a in config.current_attacks])
                print("attack_id:", attack["id"])


        if name == "Heart Me":
            asyncio.create_task(heart_me(user))

        elif name == "Rose":
            asyncio.create_task(spawn_tnt(user, event.repeat_count))

        elif name == "Finger Heart":
            asyncio.create_task(spawn_multi_tnt(user, event.repeat_count, per=5,delay=0.1))

        elif name == "Rosa":
            asyncio.create_task(levitation_effect(user,event.repeat_count,delay=15))

        elif name == "BFF Necklace":
            asyncio.create_task(summon_zombies(user, event.repeat_count))

        elif name == "Perfume":
            asyncio.create_task(fill_blocks(user,event.repeat_count))

        elif name == "Doughnut":
            asyncio.create_task(spawn_donuts_tnt(user, 2 * event.repeat_count, per=20, delay=2))

        elif name == "Paper Crane":
            asyncio.create_task(blank_info(user,name))
    elif not event.gift.streakable:

        if name == "Hand Hearts":
            asyncio.create_task(fill_area(user))

        elif name == "Mishka Bear":
            asyncio.create_task(mishka_storm(user))

        elif name == "Corgi":
            asyncio.create_task(corgi_messege(user))

        elif name == "Galaxy":
            asyncio.create_task(blank_info(user,name))

        #名前　なにで？（バトル、妨害、イベント、枠投げだけ）目標 を　達成したいです。配信時間（毎日OR曜日、時間）やってます。最後の一言（オレをのし上げてくれえ！）