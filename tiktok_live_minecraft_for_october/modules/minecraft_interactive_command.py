from modules import command_worker_mod as cwm
from modules import config
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

jump_boost_queue = asyncio.Queue()
async def jumpboost_cooldown_worker():
    while True:
        command_send_queue


async def command_send_queue(code):
    await cwm.command_queue.put(code)

async def blank_info(user,giftname,minecraft_id):
    print(f"name:{user}  gift:{giftname} stremar:{minecraft_id}")
    print(minecraft_id)


async def heart_me(user,count,minecraft_id):
    print(f"{user} send Heart Me...")
    await command_send_queue(f"execute as @a run give {minecraft_id} minecraft:golden_apple 1")
    await command_send_queue(f'title {minecraft_id} title {"text":"§cハートミー！Thx！"}')
    for i in range(count):
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    # print(minecraft_id)

async def Finger_Heart(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {"text":"§c原木  5個 Thx！"}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"execute as @a run give {minecraft_id} minecraft:oak_log 5")

async def Rosa(user,count,minecraft_id):
    for i in range(count):
        await command_send_queue(f"execute as @a run effect give @a minecraft:jump_boost 60 30 false")
        await command_send_queue(f'title {minecraft_id} title {"text":"§cスーパージャンプ！"}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
        await asyncio.sleep(59)

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
    await command_send_queue(f'title {minecraft_id} title {"text":"§c俊敏のゴーレム召喚！！"}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f'execute as {minecraft_id} at {minecraft_id} run summon iron_golem ~ ~ ~ {{Tags:["SpeedyGolem"],CustomName:\'{{"text":"疾走する{user}のゴーレム"}}\',CustomNameVisible:1}}')
    await command_send_queue(f'execute as {minecraft_id} run effect give @e[type=iron_golem,tag=SpeedyGolem] speed 9999 5 true')

async def Hand_Hearts(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {"text":"§cこれで生きろ！"}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f'execute as @a run give {minecraft_id} minecraft:netherite_axe[minecraft:custom_name="{user}の斧"] 1')

async def corgi(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {"text":"§cヒツジの進軍！！"}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for x in range(count):
        for i in range(15):
            # await command_send_queue(f'execute as {minecraft_id} summon minecraft:sheep ~ ~ ~ {{CustomName:"御影蘭",NoAI:0b,attributes:[{id:"generic.movement_speed",base:0.5},{id:"generic.scale",base:2.0}],Passengers:[{id:"silverfish",Silent:1b,NoAI:0b,Fire:0, DeathLootTable:"minecraft:empty",CustomName:"\"mirena\"",attributes:[{id:"generic.scale",base:2.0}],Tags:["sheep_rider0"]}]}}')
            await command_send_queue(f'execute as {minecraft_id} run summon minecraft:sheep ~ ~ ~ {{CustomName:"御影蘭",NoAI:0b,attributes:[{{id:"generic.movement_speed",base:0.5}},{{id:"generic.scale",base:2.0}}],Passengers:[{{id:"silverfish",Silent:1b,NoAI:0b,Fire:0,DeathLootTable:"minecraft:empty",CustomName:"\"怨念\"",attributes:[{{id:"generic.scale",base:2.0}}],Tags:["sheep_rider"]}}]}}')
    await command_send_queue('effect give @e[tag=sheep_rider] invisibility infinite 1 true')

async def five_00_coin(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {"text":"§cポピーーーー！！"}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"clear {minecraft_id}")
        await command_send_queue(f"give {minecraft_id} minecraft:poppy 2304")

async def thirty_00_over_coin(user,count,minecraft_id):
    await command_send_queue(f'title {minecraft_id} title {"text":"§cポピーーーー！！"}')
    await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{user}"}}')
    for i in range(count):
        r = random.uniform(300, 1000)                # 半径4〜6
        theta = random.uniform(0, 2*math.pi)    # 角度0〜360度
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
    minecraft_id = config.re_mcid(streamer_ID)

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
        # await command_send_queue(f'title @a title {{"text":"{USER_LIKE_THRESHOLD}いいねTNT"}}')
        # await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
        # await command_send_queue(f"bedrock tnt 1 {event.user.nickname}")
        selected = random.choices(
            config.minecraft_effects,
            weights=[e[2] for e in config.minecraft_effects],
            k=1
        )[0]
        print(selected)
        command = selected[0].format(player_name=minecraft_id)
        await command_send_queue(command)
        await command_send_queue(f'title {minecraft_id} title {{"text":"{selected[1]}"}}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{event.user.nickname}"}}')

        user_like_count[user_id] -= USER_LIKE_THRESHOLD
    # 全体累計のイベント
    if total_likes > TOTAL_LIKE_THRESHOLD:
        #ログ　
        now = datetime.now()
        print(f"🌟 Total likes reached {total_likes}!")
        print(f"User total: {user_like_count[user_id]}, Global total: {total_likes}")
        # ここにRCONや通知処理を追加可能
        await command_send_queue(f'title @a title {{"text":"{TOTAL_LIKE_THRESHOLD}いいね爆撃"}}')
        await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
        for i in range(150):
            await command_send_queue(f"bedrock tnt 1 {event.user.nickname}")
            await asyncio.sleep(0.075)
        total_likes -= TOTAL_LIKE_THRESHOLD

# フォロー関連
# すでに反応済みのユーザーを保持するセット
# 対応済み
already_triggered = set()
async def on_follow_mod(event,streamer_ID):
    user_id = event.user.unique_id
    minecraft_id = config.re_mcid(streamer_ID)
    if user_id not in already_triggered:
        already_triggered.add(user_id)
        # await command_send_queue(f"bedrock tnt 3 {event.user.nickname}")
        await command_send_queue(f'title {minecraft_id} title {{"text":"§c{event.user.nickname}の試練"}}')
        for i in range(5):
            monster = random.choices(
                config.panic_monsters,
                weights=[m[1]for m in config.panic_monsters],
                k=1
            )[0]
            # 半径4〜6の円形範囲にランダム座標生成
            r = random.uniform(4, 6)          # 半径4〜6
            theta = random.uniform(0, 2*math.pi)  # 角度0〜360度
            x_offset = round(r * math.cos(theta))
            z_offset = round(r * math.sin(theta))
            y_offset = 1  # プレイヤーの頭上1ブロック

            await command_send_queue(f'execute at {minecraft_id} run summon {monster} ~{x_offset} ~{y_offset} ~{z_offset} {{CustomName:"\\"{event.user.nickname}の試験官\\""}}')
        await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{event.user.nickname}"}}')

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

async def time_measurement():
    global finish_time
    if config.time_measurement_running:
        return  # すでに実行中なら何もしない
    config.time_measurement_running = True
    config.current_multiplier = 2
    await command_send_queue(F'bossbar add timer "Countdown"')
    await command_send_queue(f"bossbar set timer players @a")
    await command_send_queue(f'bossbar set timer max {finish_time}')
    # finish_time = datetime.now() + timedelta(minutes=5)
    try:
        while 0 < finish_time:
            if 300 < finish_time:
                await command_send_queue(f"bossbar set timer max {finish_time}")
                await command_send_queue(f"bossbar set timer value {finish_time}")
            else:
                await command_send_queue(f"bossbar set timer value {finish_time}")
            await command_send_queue(f'bossbar set timer name "残り時間：{finish_time}"')
            await asyncio.sleep(1)
            finish_time -= 1
    finally:
        config.current_multiplier = 1
        config.time_measurement_running = False
        await command_send_queue(f"bossbar remove timer")


async def on_gift_mod(event,streamer_ID):
    global gift_counter,coin_counter
    #ギフトを受け取るたびに取得する情報
    user = event.user.nickname
    name = event.gift.name
    coin = event.gift.diamond_count
    times = event.repeat_count

    #ログ用
    now = datetime.now()
    minecraft_id = config.re_mcid(streamer_ID)

    print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # streak 終了時のみ処理
    if event.gift.streakable and not event.streaking or not event.gift.streakable:
        await gift_counting(times)
        await coin_counting(coin,times)

        print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S {minecraft_id}')}")

        if name == "Heart Me":
            asyncio.create_task(heart_me(user,times,minecraft_id))

        # elif name == "Rose":
            # asyncio.create_task(spawn_tnt(user, times,0.1,minecraft_id))

        elif name == "Finger Heart":
            asyncio.create_task(Finger_Heart(user, times,minecraft_id))

        elif name == "Rosa":
            asyncio.create_task(Rosa(user,times,minecraft_id))

        # elif name == "BFF Necklace":
        #     asyncio.create_task(summon_zombies(user, times,minecraft_id))

        elif name == "Perfume":
            asyncio.create_task(iron_Golem(user,times,minecraft_id))

        elif name == "Doughnut":
            asyncio.create_task(doughnut(user,times,minecraft_id))

        elif name == "Genius":
            asyncio.create_task(genius(user,times,minecraft_id))


    elif not event.gift.streakable:
        await gift_counting(times)
        await coin_counting(coin,times)

        if name == "Paper Crane":
            asyncio.create_task(blank_info(user,name,minecraft_id))

        elif name == "Hand Hearts":
            asyncio.create_task(Hand_Hearts(user,times,minecraft_id))

        elif name == "Paper Crane":
            asyncio.create_task(blank_info(user,name,minecraft_id))

        # elif name == "Mishka Bear":
        #     asyncio.create_task(mishka_storm(user,times,minecraft_id))

        elif name == "Corgi":
            asyncio.create_task(corgi(user,times,minecraft_id))

        elif name == "Galaxy":
            asyncio.create_task(blank_info(user,times,minecraft_id))

        elif str(coin) == "500":
            asyncio.create_task(five_00_coin(user,times,minecraft_id))

        elif str(coin) <= "3000":
            asyncio.create_task(thirty_00_over_coin(user,times,minecraft_id))

    # if 5000 <= coin_counter:
    #     while coin_counter > 5000:
    #         await add_time()
    #     asyncio.create_task(time_measurement())