from modules import command_worker_mod as cwm
from modules import config
import asyncio
from datetime import datetime,timedelta
# その配信でのコインの総量
coin_counter = 0
# コンボカウンター
gift_counter = 0

# 個別ユーザーごとのいいね数を保持
user_like_count = {}
# 配信全体の累計いいね数
total_likes = 0
# しきい値
USER_LIKE_THRESHOLD = 300
TOTAL_LIKE_THRESHOLD = 10000



async def command_send_queue(code):
    await cwm.command_queue.put(code)

async def blank_info(user,giftname):
    print(f"name:{user}  gift:{giftname}")
async def heart_me(user,count):
    print(f"{user} send Heart Me...")
    await command_send_queue(f"bedrock tnt 3 {user}")
    await command_send_queue('title @a title {"text":"§cハートミー！Thx！"}')
    for i in range(count):
        await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
async def spawn_tnt(user, count, delay=0.1):
    await command_send_queue('title @a title {"text":"1TNT"}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"bedrock tnt 1 {user}")
        await asyncio.sleep(delay)

async def spawn_multi_tnt(user, count, per, delay):
    await command_send_queue(f'title @a title {{"text":"{per}TNT"}}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"bedrock tnt {per} {user}")
        await asyncio.sleep(delay)


async def spawn_donuts_tnt(user, count, per, delay):
    await command_send_queue(f'title @a title {{"text":"{per * 2}TNT"}}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"bedrock tnt {per} {user}")
        await asyncio.sleep(delay)

async def summon_zombies(user, count):
    await command_send_queue('title @a title {"text":"ゾンビのお友達～"}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
    for z in range(count):
        for i in range(15):
            await command_send_queue(f'execute at @a run summon zombie ~ ~3 ~ {{IsBaby:0,ArmorItems:[{{}},{{}},{{}},{{id:"minecraft:carved_pumpkin",Count:1}}],ArmorDropChances:[0F,0F,0F,0F],CustomName:"{user}の分身",CustomNameVisible:1}}')
            await asyncio.sleep(0.05)

async def levitation_effect(user,count,delay):
    await command_send_queue('title @a title {"text":"浮遊"}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
    for i in range(count):
        await command_send_queue(f"effect give @a minecraft:levitation {delay} 2")
        await asyncio.sleep(delay)

async def fill_blocks(user,count):
    await command_send_queue('title @a title {"text":"§c400ブロック埋めたて"}')
    await command_send_queue(f'title @a subtitle {{"text":"ありがとう、{user}"}}')
    for i in range(count):
        await command_send_queue("bedrock fillblock 400")
    await asyncio.sleep(1)

async def fill_area(user):
    await command_send_queue('title @a title {"text":"§c埋立完了!"}')
    await command_send_queue(f'title @a subtitle {{"text":"ありがとう! {user}"}}')
    await command_send_queue("bedrock fill")
    await asyncio.sleep(1)

async def corgi_messege(user):
    await command_send_queue('title @a title {"text":"とにかく荒らせ!"}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')

async def mishka_storm(user):
    await command_send_queue('title @a title {"text":"§cTNTの嵐"}')
    await command_send_queue(f'title @a subtitle {{"text":"{user}"}}')
    await asyncio.sleep(3.20)
    for i in range(165):
        await command_send_queue("bedrock tnt 2")
        await asyncio.sleep(0.05)

async def gift_counting(gift_times):
    global gift_counter
    gift_counter += gift_times

async def coin_counting(coin,times):
    global coin_counter
    coin_counter += coin * times
    print("total coin :",coin_counter)





#いいね関連

async def on_like_mod(event):
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
        await command_send_queue(f'title @a title {{"text":"{USER_LIKE_THRESHOLD}いいねTNT"}}')
        await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
        await command_send_queue(f"bedrock tnt 1 {event.user.nickname}")
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
already_triggered = set()
async def on_follow_mod(event):
    user_id = event.user.unique_id
    if user_id not in already_triggered:
        already_triggered.add(user_id)
        await command_send_queue(f"bedrock tnt 3 {event.user.nickname}")
        await command_send_queue('title @a title {"text":"§cフォロー、ありがとう！"}')
        await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')


async def on_comment_mod(event):
    now = datetime.now()
    print(f"{event.user.nickname} >> {event.comment}"f" at {now.strftime('%Y-%m-%d %H:%M:%S')}")


async def add_time(seconds=300):
    global finish_time,coin_counter
    now = datetime.now()
    if finish_time <= 0:
        # 初めて追加する場合、今から5分後
        finish_time = seconds
    else:
        # すでに残り時間がある場合は延長
        finish_time += seconds
    await command_send_queue(f'bossbar set timer max {finish_time}')
    
    coin_counter -= 5000

async def time_measurement():
    global finish_time
    if config.time_measurement_running:
        return  # すでに実行中なら何もしない
    config.time_measurement_running = True
    config.current_multiplier = 2
    
    # finish_time = datetime.now() + timedelta(minutes=5)
    await command_send_queue(f'bossbar add timer "Countdown"')
    try:
        await command_send_queue(f"bossbar set timer players @a")
        while 0 < finish_time:
            await command_send_queue(f"bossbar set timer value {finish_time}")
            asyncio.sleep(1)
            finish_time -= 1
    finally:
        config.current_multiplier = 1
        config.time_measurement_running = False
        await command_send_queue(f"bossbar remove timer")
async def on_gift_mod(event):
    global gift_counter,coin_counter

    #ギフトを受け取るたびに取得する情報
    user = event.user.nickname
    name = event.gift.name
    coin = event.gift.diamond_count
    times = event.repeat_count
    #ログ用
    now = datetime.now()

    print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # streak 終了時のみ処理
    if event.gift.streakable and not event.streaking or not event.gift.streakable:
        await gift_counting(times)
        await coin_counting(coin,times)


        print(f"{user} sent a {name} (x{times}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        if name == "Heart Me":
            asyncio.create_task(heart_me(user,times))

        elif name == "Rose":
            asyncio.create_task(spawn_tnt(user, times))

        elif name == "Finger Heart":
            asyncio.create_task(spawn_multi_tnt(user, times, per=5,delay=0.1))

        elif name == "Rosa":
            asyncio.create_task(levitation_effect(user,times,delay=15))

        elif name == "BFF Necklace":
            asyncio.create_task(summon_zombies(user, times))

        elif name == "Perfume":
            asyncio.create_task(fill_blocks(user,times))

        elif name == "Doughnut":
            asyncio.create_task(spawn_donuts_tnt(user, 2 * times, per=20, delay=2))

        elif name == "Paper Crane":
            asyncio.create_task(blank_info(user,name))

    elif not event.gift.streakable:
        await gift_counting(times)
        await coin_counting(coin,times)


        if name == "Hand Hearts":
            asyncio.create_task(fill_area(user))

        elif name == "Mishka Bear":
            asyncio.create_task(mishka_storm(user))

        elif name == "Corgi":
            asyncio.create_task(corgi_messege(user))

        elif name == "Galaxy":
            asyncio.create_task(blank_info(user,name))

        if 5000 <= coin_counter:
            while coin_counter > 5000:
                await add_time()
            asyncio.create_task(time_measurement())