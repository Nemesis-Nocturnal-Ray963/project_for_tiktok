from modules import command_worker_mod as cwm
# from modules import arcade_system_alpha
# from modules.arcade_system import core as arcade_system
from modules import config
import asyncio
from datetime import datetime
import random
import math
import queue
import os
print("2025年11月日 ギフトギャラリー+α+イベント+ズートピア開催前")

# その配信でのコインの総量
coin_counter = 0
# コンボカウンター
gift_counter = 0

# 個別ユーザーごとのいいね数を保持
user_like_count = {}
# 配信全体の累計いいね数
total_likes = 0
# しきい値
USER_LIKE_THRESHOLD = 100000
TOTAL_LIKE_THRESHOLD = 10000


finish_time = 0
arcade_queue = None
async def command_send_queue(code):
    if config.is_minecraft_server_connect:
        await cwm.command_queue.put(code)

async def arcade_send_queue(data):
    """Arcadeスレッドへ安全送信"""
    # print("sender id:", id(arcade_system_alpha.arcade_queue))
    global arcade_queue
    if not arcade_queue:
        print("[WARN] arcade_queue 未初期化")
        return

    try:
        print("I senf queue...")
        await asyncio.to_thread(arcade_queue.put, data)
    except Exception as e:
        print(f"[ERROR] arcade_send_queue failed: {e}")

async def blank_info(user,giftname,minecraft_id):
    print(f"name:{user}  gift:{giftname} stremar:{minecraft_id}")
    print(minecraft_id)

async def spawn_test():
    config.gift_counter += 15
    print("spawn test now...")
    await asyncio.sleep(1)
    asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/whale_diving.png"])))
    await asyncio.sleep(0.1)
    asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/mooncake.png"])))
    await asyncio.sleep(0.1)
    asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/strawberry_moon.png"])))
    await asyncio.sleep(0.1)
    asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/magic_hat.png"])))
    await asyncio.sleep(0.1)
    asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/flating_lanterns.png"])))



async def heart_me(user,count,minecraft_id):
    print(f"{user} send Heart Me...")
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cハートミー！Thx！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"execute as {minecraft_id} run give {minecraft_id} minecraft:golden_apple 1")

    # print(minecraft_id)

async def Finger_Heart(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§c原木  5個 Thx！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"execute as {minecraft_id} run give {minecraft_id} minecraft:oak_log 5")

async def Rosa(user,count,minecraft_id):
    for i in range(count):
        await command_send_queue(f"execute as {minecraft_id} run effect give {minecraft_id} minecraft:jump_boost 60 30 false")
        await command_send_queue(f'title {minecraft_id} title {{"text":"§cスーパージャンプ！"}}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')

async def doughnut(user,count,minecraft_id):
    for i in range(count):
        selected = random.choices(
            config.minecraft_enhanced_effects,
            weights=[e[2] for e in config.minecraft_enhanced_effects],
            k=1
        )[0]
        print(selected)
        command = selected[0].format(player_name=minecraft_id)
        await command_send_queue(command)
        await command_send_queue(f'title {minecraft_id} title {{"text":"{selected[1]}"}}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')

async def genius(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§c{user}からの極限試練"}}')
    for z in range(count):
        for i in range(5):
            monster = random.choices(
                config.enhanced_panic_monsters,
                weights=[m[1]for m in config.enhanced_panic_monsters],
                k=1
            )[0][0]
                                                    # 半径4〜6の円形範囲にランダム座標生成
            r = random.uniform(4, 6)                # 半径4〜6
            theta = random.uniform(0, 2*math.pi)    # 角度0〜360度
            x_offset = round(r * math.cos(theta))
            z_offset = round(r * math.sin(theta))
            y_offset = 1                            # プレイヤーの頭上1ブロック
            print(f'execute as {minecraft_id} run summon {monster} ~{x_offset} ~{y_offset} ~{z_offset} {{CustomName:"\\"{user}の試練\\""}}')
            await command_send_queue(f'execute as {minecraft_id} at {minecraft_id} run summon {monster} ~{x_offset} ~{y_offset} ~{z_offset} {{CustomName:"\\"{user}の試練\\""}}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')

async def iron_Golem(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§c俊敏のゴーレム召喚！！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f'execute as {minecraft_id} at {minecraft_id} run summon iron_golem ~ ~ ~ {{Tags:["SpeedyGolem"],CustomName:\'{{"text":"疾走する{user}のゴーレム"}}\',CustomNameVisible:1}}')
    await command_send_queue(f'execute as {minecraft_id} run effect give @e[type=iron_golem,tag=SpeedyGolem] speed 9999 5 true')

async def Hand_Hearts(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cこれで生きろ！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f'execute as {minecraft_id} run effect give {minecraft_id} haste 30 5')
        await command_send_queue(f'execute as {minecraft_id} run effect give {minecraft_id} instant_health 30 5')
        await command_send_queue(f'execute as {minecraft_id} run effect give {minecraft_id} darkness 30')
        await command_send_queue(f'execute as {minecraft_id} run effect give {minecraft_id} speed 30 3')
        await command_send_queue(f'execute as {minecraft_id} run effect give {minecraft_id} jump_boost 30')
        await command_send_queue(f'execute as {minecraft_id} run give {minecraft_id} minecraft:netherite_axe[minecraft:custom_name="{user}の斧"] 1')


async def corgi(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cヒツジの進軍！！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    # for x in range(count):
    for i in range(15):
        # await command_send_queue(f'execute as {minecraft_id} summon minecraft:sheep ~ ~ ~ {{CustomName:"御影蘭",NoAI:0b,attributes:[{id:"generic.movement_speed",base:0.5},{id:"generic.scale",base:2.0}],Passengers:[{id:"silverfish",Silent:1b,NoAI:0b,Fire:0, DeathLootTable:"minecraft:empty",CustomName:"\"mirena\"",attributes:[{id:"generic.scale",base:2.0}],Tags:["sheep_rider0"]}]}}')
        await command_send_queue(f'execute as {minecraft_id} at {minecraft_id} run summon sheep ~ ~ ~ {{CustomName:"御影蘭",NoAI:0b,attributes:[{{id:"generic.movement_speed",base:0.5}},{{id:"generic.scale",base:2.0}}],Passengers:[{{id:"silverfish",Silent:1b,NoAI:0b,Fire:0,DeathLootTable:"minecraft:empty",CustomName:"\"怨念\"",attributes:[{{id:"generic.scale",base:2.0}}],Tags:["sheep_rider"]}}]}}')
        await command_send_queue(f'execute as {minecraft_id} at {minecraft_id} run summon sheep ~ ~ ~ {{NoAI:0b,attributes:[{{id:"generic.movement_speed",base:0.5}},{{id:"generic.scale",base:2.0}}],Passengers:[{{id:"silverfish",Silent:1b,NoAI:0b,Fire:0,DeathLootTable:"minecraft:empty",attributes:[{{id:"generic.scale",base:2.0}}],Tags:["sheep_rider"]}}]}}')
    await command_send_queue('effect give @e[tag=sheep_rider] invisibility infinite 1 true')

async def Star_Map_Polaris(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cポピーーーー！！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for _ in range(count):
        await command_send_queue(f"execute as {minecraft_id} at {minecraft_id} run clear {minecraft_id}")
        await command_send_queue(f"execute as {minecraft_id} at {minecraft_id} run give {minecraft_id} minecraft:poppy 2304")

async def Meteor_Shower(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cこの世界のどこかへ"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        r = random.uniform(300, 1000)                # 半径4〜6
        theta = random.uniform(0, 2*math.pi)    # 角度0〜360度
        x_offset = round(r * math.cos(theta))
        z_offset = round(r * math.sin(theta))
        y_offset = 10
        await command_send_queue(f"execute as {minecraft_id} at {minecraft_id} run clear {minecraft_id}")
        await command_send_queue(f"execute as {minecraft_id} at {minecraft_id} run tp ~{x_offset} ~{y_offset} ~{z_offset}")

async def gift_counting(gift_times):
    global gift_counter
    gift_counter += gift_times

async def coin_counting(coin,times):
    global coin_counter
    coin_counter += coin * times
    print("total coin (coin_counter):",coin_counter)

#いいね関連
async def on_like_mod(event,streamer_ID):
    global total_likes
    # print(event.count)
    user_id = event.user.unique_id
    user_like_total_count = event.count
    minecraft_id = await config.re_mcid(streamer_ID)

    # print("user:",user_id,"like count... ",user_like_total_count)
    # 個別カウント更新
    if user_id not in user_like_count:
        user_like_count[user_id] = 0

    user_like_count[user_id] += user_like_total_count
    # print("user:",user_id,"like count... ",user_like_count[user_id])

    # 全体カウント更新
    total_likes += user_like_total_count

    # 個別ユーザーのイベント
    if user_like_count[user_id] > USER_LIKE_THRESHOLD:
        #ログ　
        now = datetime.now()
        print(f"🎉 {event.user.nickname} reached {user_like_count[user_id]} likes!")
        print(f"{event.user.nickname} ({user_id}) liked at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        # ここにRCONや通知処理を追加可能
        # await command_send_queue(f'title @a title {{"text":"{USER_LIKE_THRESHOLD}いいねTNT"}}')
        # await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
        # await command_send_queue(f"bedrock tnt 1 {event.user.nickname}")
        selected = random.choices(
            config.minecraft_effects,
            weights=[e[2] for e in config.minecraft_effects],
            k=1
        )[0]
        print(selected)
        # commandにselectedで取得した０番目内容をフォーマットしたうえで格納
        command = selected[0].format(player_name=minecraft_id)
        await command_send_queue(command)
        await command_send_queue(f'title {minecraft_id} title {{"text":"{selected[1]}"}}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{event.user.nickname}"}}')

        user_like_count[user_id] -= USER_LIKE_THRESHOLD
    # 全体累計のイベント
    # if total_likes > TOTAL_LIKE_THRESHOLD:
    #     #ログ　
    #     now = datetime.now()
    #     print(f"🌟 Total likes reached {total_likes}!")
    #     print(f"User total: {user_like_count[user_id]}, Global total: {total_likes}")
    #     # ここにRCONや通知処理を追加可能
    #     await command_send_queue(f'title @a title {{"text":"{TOTAL_LIKE_THRESHOLD}いいね爆撃"}}')
    #     await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
    #     for i in range(150):
    #         await command_send_queue(f"bedrock tnt 1 {event.user.nickname}")
    #         await asyncio.sleep(0.075)
    #     total_likes -= TOTAL_LIKE_THRESHOLD

# フォロー関連
# すでに反応済みのユーザーを保持するセット
# 対応済み
already_triggered = set()
async def on_follow_mod(event,streamer_ID):
    user_id = event.user.unique_id
    if user_id not in already_triggered:
        already_triggered.add(user_id)

# 対応済み
async def on_comment_mod(event,streamer_ID):
    now = datetime.now()
    print(f"{event.user.nickname} >> {event.comment} at {now.strftime('%Y-%m-%d %H:%M:%S')} form {streamer_ID}")

async def add_time(seconds=300):
    global finish_time,coin_counter
    # now = datetime.now()t
    if finish_time <= 0:
        # 初めて追加する場合、今から5分後
        finish_time = seconds
    else:
        # すでに残り時間がある場合は延長
        finish_time += seconds
    coin_counter -= 5000


async def on_gift_mod(event,streamer_ID):
    global gift_counter,coin_counter
    #ギフトを受け取るたびに取得する情報
    user = event.user.nickname
    name = event.gift.name
    coin = event.gift.diamond_count
    times = int(event.repeat_count)
    count = times
    #ログ用
    now = datetime.now()
    # minecraft_id = await config.re_mcid(streamer_ID)
    print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    if config.is_test:
        print(user)
        print(name)


        # streak 終了時のみ処理
        print("event.gift.streakable:",event.gift.streakable)
        print("event.streaking:",event.streaking)
    # if event.gift.streakable and not event.streaking or not event.gift.streakable:
        # config.gift_counter += event.repeat_count

    if event.gift.streakable and not event.streaking:
        # asyncio.create_task(gift_counting(times))
        asyncio.create_task(coin_counting(coin,times))


        if name == "Rose":
            # asyncio.create_task(spawn_tnt(user, times,0.1,minecraft_id))
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/rose.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_sticker", [1])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/rose.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "substitute":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Suprised Fish":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "You're awesome":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Ice Cream Cone":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Cat Paws":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Nice to meet ":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Well done":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Love you so muc":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Love Letter":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "GG":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Baseball":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Pumpkin":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Autumn heart":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Cake Slice":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Cute Cat":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "TikTok":
            # asyncio.create_task(spawn_tnt(user, times,0.1,minecraft_id))
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/tiktok.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/tiktok.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Popular Vote":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/go_popular.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/go_popular.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Finger Heart":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/finger_heart.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/finger_heart.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Fighting":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/fighting.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/fighting.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Rosa":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/rosa.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/rosa.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "BFF Necklace":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/bff_necklace.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/bff_necklace.png",coin])))
                await asyncio.sleep(0.1)
        #     asyncio.create_task(summon_zombies(user, times,minecraft_id))

        elif name == "Perfume":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Carbuncle":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/puyopuyo_1.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/puyopuyo_1.png",coin])))

                await asyncio.sleep(0.1)


        elif name == "Doughnut":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/doughnut.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/doughnut.png",coin])))
                await asyncio.sleep(0.1)


        elif name == "Shield Token":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/shield_token.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/shield_token.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "Genius":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)

        elif name == "test":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/rose.png",coin])))
                
            # asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [3, 1.0, "devil_ran_shape"])))
            # asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
            # asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/heart_me.png",1000])))
                # asyncio.create_task(arcade_send_queue(("spawn_sticker", [1])))
            # await on_fireworks(event)

        elif name == "test1":
            asyncio.create_task(arcade_send_queue(("show_frame", ("shutdown",))))
        elif name == "test_icosa_1":
            asyncio.create_task(arcade_send_queue(("spawn_Icosahedron", ("light up",))))
        elif name == "test_icosa_2":
            asyncio.create_task(arcade_send_queue(("spawn_Icosahedron", ("light down",))))
        elif name == "spawn_test":
            await spawn_test()
            
            
            
        # zootopia1
        if name == "Judy":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia1.png",coin])))
                await asyncio.sleep(0.1)
        # zootopia2
        if name == "Nick":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia2.png",coin])))
                await asyncio.sleep(0.1)

      
    elif not event.gift.streakable and not event.streaking:
        asyncio.create_task(gift_counting(times))
        asyncio.create_task(coin_counting(coin,times))

        if name == "Heart Me":
            # asyncio.create_task(heart_me(user,times,minecraft_id))
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/heart_me.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/heart_me.png"])))
                await asyncio.sleep(0.1)
        
        elif name == "WIN!":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/puyopuyo_2.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/puyopuyo_2.png"])))
                await asyncio.sleep(0.1)

        elif name == "LOSE":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/puyopuyo_3.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/puyopuyo_3.png"])))
                await asyncio.sleep(0.1)

        elif name == "Cap":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/caps.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/caps.png"])))
                await asyncio.sleep(0.1)

        elif name == "Paper Crane":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                await asyncio.sleep(0.1)
            # asyncio.create_task(blank_info(user,times,minecraft_id))
            print("notting intreactive...")
        elif name == "Hat and Mustache":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/hat_and_mustache.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/hat_and_mustache.png"])))
                await asyncio.sleep(0.1)
        elif name == "Hand Heart":
            # asyncio.create_task(Hand_Hearts(user,times,minecraft_id))
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/hand_hearts.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/hand_hearts.png"])))
                await asyncio.sleep(0.1)
        # elif name == "Mishka Bear":
        #     asyncio.create_task(mishka_storm(user,times,minecraft_id))
        elif name == "Breakthrough Star":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/angel_ran.png"])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/devil_ran.png"])))
                await asyncio.sleep(0.1)
        elif name == "Hearts":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/hearts.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/hearts.png"])))
                await asyncio.sleep(0.1)

        elif name == "Corgi":
            asyncio.create_task(corgi(user,times,minecraft_id))
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/corgi.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/corgi.png"])))
                await asyncio.sleep(0.1)

        elif name == "Shield Gift":
            asyncio.create_task(corgi(user,times,minecraft_id))
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/shield_gift.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/shield_gift.png"])))
                await asyncio.sleep(0.1)

        elif name == "Money Gun":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/money_gun.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/money_gun.png"])))
                await asyncio.sleep(0.1)

        elif name == "DJ Glasses":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/dj_glasses.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/dj_glasses.png"])))
                await asyncio.sleep(0.1)


        elif name == "Galaxy":
            asyncio.create_task(blank_info(user,times,minecraft_id))
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/galaxy.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/galaxy.png"])))
                await asyncio.sleep(0.1)

        elif name == "Fireworks":
            for _ in range(count):
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/fireworks.png"])))
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/fireworks.png",coin])))
                asyncio.create_task(on_fireworks())
                await asyncio.sleep(0.1)

        elif name == "Under Control":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/under_control.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/under_control.png"])))
                await asyncio.sleep(0.1)

        elif name == "Whale Diving":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/whale_diving.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/whale_diving.png"])))
                await asyncio.sleep(0.1)

        elif name == "Star Map Polaris":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/angel_ran.png"])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/devil_ran.png"])))
                await asyncio.sleep(0.1)
            # print("DEBUG: Star_Map_Polaris called", user, times, minecraft_id)
            # await Star_Map_Polaris(user,times,minecraft_id)

        elif name == "Puyo Shuffle!":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/puyopuyo_4.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/puyopuyo_4.png"])))
                await asyncio.sleep(0.1)
        

        elif name == "Meteor Shower":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/meteor_shower.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/meteor_shower.png"])))
                await asyncio.sleep(0.1)
            asyncio.create_task(Meteor_Shower(user,times,minecraft_id))

        elif name == "Leon the Kitten":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/leon_the_kitten.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/leon_the_kitten.png"])))
                await asyncio.sleep(0.1)

        elif name == "Medieval Crown":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/medieval_crown.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/medieval_crown.png"])))
                await asyncio.sleep(0.1)

        elif name == "Flying Jets":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/flying_jets.png",coin])))
                # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/flying_jets.png"])))
                await asyncio.sleep(0.1)
    
        elif name == "Puppy Kisses":
            for _ in range(count):
                print("test")
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
    
        elif name == "Puyopuyo Chain!":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/0000.png",coin])))
                asyncio.create_task(arcade_send_queue(("play_sound", ["assets/sounds/Raffina_Voice_Chain.wav"])))

        # zootopia3
        if name == "Judy Pose":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia3.png",coin])))
                await asyncio.sleep(0.1)

        if name == "Last take":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia4.png",coin])))
                await asyncio.sleep(0.1)

        if name == "Movie Moment":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia5.png",coin])))
                await asyncio.sleep(0.1)

        if name == "Rollercoaster":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia6.png",coin])))
                await asyncio.sleep(0.1)

        if name == "zootopia Family":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia7.png",coin])))
                await asyncio.sleep(0.1)

    # if 5000 <= coin_counter:
    #     while coin_counter > 5000:
    #         await add_time()
    #     asyncio.create_task(time_measurement())

async def on_battle_start():
    print("ballte start...")
    asyncio.create_task(arcade_send_queue(("show_frame", (True,))))
    # asyncio.create_task(arcade_send_queue(("spawn_Icosahedron", ("light up",))))
    # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/dj_glasses.png"])))
async def on_battle_end():
    print("ballte end...")
    asyncio.create_task(arcade_send_queue(("show_frame", (False,))))
    # asyncio.create_task(arcade_send_queue(("spawn_Icosahedron", ("light down",))))

async def on_fireworks(event):
    user = event.user.nickname
    name = event.gift.name
    print("on fireworks...")
    if name == "rose":
        asyncio.create_task(arcade_send_queue(("spawn_fireworks", [18, 0.3])))

    if name == "test":
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"Judith1"])))
        await asyncio.sleep(3.1)
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"Judith2"])))
        await asyncio.sleep(3.1)
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"nick1"])))
        await asyncio.sleep(3.1)
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"nick2"])))
        await asyncio.sleep(3.1)
        await fireworks_buffer_queue.put(("spawn_fireworks_ex",[1, 3.0,"nick2"]))