from modules import workers
from modules import config
from modules import arcade_system_alpha
import asyncio
from datetime import datetime
import random
import math

# その配信でのコインの総量
coin_counter = 0
# コンボカウンター
gift_counter = 0

# 個別ユーザーごとのいいね数を保持
user_like_count = {}
# 配信全体の累計いいね数
total_likes = 0
# しきい値
USER_LIKE_THRESHOLD = 1000
TOTAL_LIKE_THRESHOLD = 10000

finish_time = 0



arcade_queue = None
async def arcade_send_queue(code):
    global arcade_queue
    print("send queue...")
    arcade_queue.put(code)




async def command_send_queue(code):
    # await cwm.command_queue.put(code)
    print("I can't send command!! check your cord")

async def blank_info(user,giftname,minecraft_id):
    print(f"name:{user}  gift:{giftname} stremar:{minecraft_id}")
    print(minecraft_id)


async def heart_me(user,count,minecraft_id):
    print(f"{user} send Heart Me...")
    await command_send_queue(f"execute as @a run give {minecraft_id} minecraft:golden_apple 1")
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cハートミー！Thx！"}}')
    for i in range(count):
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    # print(minecraft_id)

async def Finger_Heart(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§c原木  5個 Thx！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"execute as @a run give {minecraft_id} minecraft:oak_log 5")

async def Rosa(user,count,minecraft_id):
    for i in range(count):
        await command_send_queue(f"execute as @a run effect give @a minecraft:jump_boost 60 30 false")
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
            )[0]
                                                    # 半径4〜6の円形範囲にランダム座標生成
            r = random.uniform(4, 6)                # 半径4〜6
            theta = random.uniform(0, 2*math.pi)    # 角度0〜360度
            x_offset = round(r * math.cos(theta))
            z_offset = round(r * math.sin(theta))
            y_offset = 1                            # プレイヤーの頭上1ブロック

            await command_send_queue(f'execute at {minecraft_id} run summon {monster} ~{x_offset} ~{y_offset} ~{z_offset} {{CustomName:"\\"{user}の試練\\""}}')
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
        await command_send_queue(f'execute as @a run give {minecraft_id} minecraft:netherite_axe[minecraft:custom_name="{user}の斧"] 1')
        await command_send_queue(f'execute as @a run effect give {minecraft_id} haste 30 5')
        await command_send_queue(f'execute as @a run effect give {minecraft_id} instant_health 30 5')
        await command_send_queue(f'execute as @a run effect give {minecraft_id} darkness 30')
        await command_send_queue(f'execute as @a run effect give {minecraft_id} speed 30 3')
        await command_send_queue(f'execute as @a run effect give {minecraft_id} jump_boost 30')

async def corgi(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cヒツジの進軍！！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for x in range(count):
        for i in range(15):
            # await command_send_queue(f'execute as {minecraft_id} summon minecraft:sheep ~ ~ ~ {{CustomName:"御影蘭",NoAI:0b,attributes:[{id:"generic.movement_speed",base:0.5},{id:"generic.scale",base:2.0}],Passengers:[{id:"silverfish",Silent:1b,NoAI:0b,Fire:0, DeathLootTable:"minecraft:empty",CustomName:"\"mirena\"",attributes:[{id:"generic.scale",base:2.0}],Tags:["sheep_rider0"]}]}}')
            await command_send_queue(f'execute as {minecraft_id} run summon minecraft:sheep ~ ~ ~ {{CustomName:"御影蘭",NoAI:0b,attributes:[{{id:"generic.movement_speed",base:0.5}},{{id:"generic.scale",base:2.0}}],Passengers:[{{id:"silverfish",Silent:1b,NoAI:0b,Fire:0,DeathLootTable:"minecraft:empty",CustomName:"\"怨念\"",attributes:[{{id:"generic.scale",base:2.0}}],Tags:["sheep_rider"]}}]}}')
    await command_send_queue('effect give @e[tag=sheep_rider] invisibility infinite 1 true')

async def five_00_coin(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cポピーーーー！！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"clear {minecraft_id}")
        await command_send_queue(f"give {minecraft_id} minecraft:poppy 2304")

async def thirty_00_over_coin(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {{"text":"§cポピーーーー！！"}}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        r = random.uniform(300, 1000)        # 半径4〜6
        theta = random.uniform(0, 2*math.pi) # 角度0〜360度
        x_offset = round(r * math.cos(theta))
        z_offset = round(r * math.sin(theta))
        y_offset = 10
        await command_send_queue(f"clear {minecraft_id}")
        await command_send_queue(f"/tp ~{x_offset} ~{y_offset} ~{z_offset}")

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

    # print("user:",user_id,"like count... ",user_like_total_count)
    # 個別カウント更新
    if user_id not in user_like_count:
        user_like_count[user_id] = 0

    user_like_count[user_id] += user_like_total_count
    print("user:",user_id,"like count... ",user_like_count[user_id])

    # 全体カウント更新
    total_likes += user_like_total_count

    # 個別ユーザーのイベント
    if user_like_count[user_id] > USER_LIKE_THRESHOLD:
        #ログ　
        now = datetime.now()
        print(f"🎉 {event.user.nickname} reached {user_like_count[user_id]} likes!")
        print(f"{event.user.nickname} ({user_id}) liked at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        # ここにRCONや通知処理を追加可能

        user_like_count[user_id] -= USER_LIKE_THRESHOLD
    # 全体累計のイベント
    if total_likes > TOTAL_LIKE_THRESHOLD:
        #ログ　
        now = datetime.now()
        print(f"🌟 Total likes reached {total_likes}!")
        print(f"User total: {user_like_count[user_id]}, Global total: {total_likes}")
        # ここにRCONや通知処理を追加可能

        total_likes -= TOTAL_LIKE_THRESHOLD

# フォロー関連
# すでに反応済みのユーザーを保持するセット
# 対応済み
already_triggered = set()
async def on_follow_mod(event,streamer_ID):
    user_id = event.user.unique_id
    if user_id not in already_triggered:
        already_triggered.add(user_id)
        print(f"thank you follow {event.user.nickname}")

# 対応済み
async def on_comment_mod(event,streamer_ID):
    now = datetime.now()
    print(f"{event.user.nickname} >> {event.comment} at {now.strftime('%Y-%m-%d %H:%M:%S')} form {streamer_ID}")

async def on_gift_mod(event,streamer_ID):
    global gift_counter,coin_counter
    #ギフトを受け取るたびに取得する情報
    user = event.user.nickname
    name = event.gift.name
    coin = event.gift.diamond_count
    times = event.repeat_count

    #ログ用
    now = datetime.now()
    # minecraft_id = await config.re_mcid(streamer_ID)

    print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # streak 終了時のみ処理
    if event.gift.streakable and not event.streaking or not event.gift.streakable:
        await gift_counting(times)
        await coin_counting(coin,times)
        # await workers.coin_count_queue.put(coin * times)
        print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S')} ")

    #     if name == "Heart Me":
    #         asyncio.create_task(heart_me(user,times,minecraft_id))




    elif not event.gift.streakable:
    # 多分映像演出のあるギフトはすべてここに入れる必要あり？
    # 理由説明不可
        await gift_counting(times)
        await coin_counting(coin,times)
        await workers.coin_count_queue.put(coin * times)



async def on_battle_start(event,streamer_ID):
    print("ballte start...")
    asyncio.create_task(arcade_send_queue(("show_frame", (True,))))
    # asyncio.create_task(arcade_send_queue(("spawn_gift", ["assets/images/gift/dj_glasses.png"])))
async def on_battle_end(event,streamer_ID):
    print("ballte end...")
    asyncio.create_task(arcade_send_queue(("show_frame", (False,))))