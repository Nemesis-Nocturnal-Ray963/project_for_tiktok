from modules import command_worker_mod as cwm
from modules import logger_viewer
from modules import config
import asyncio
from datetime import datetime
import random
import math
import queue
import os

print("2025年11月日 ズートピア開催")

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
fireworks_buffer_queue = asyncio.Queue()  # 花火専用の中間キュー

admin_command_queue = asyncio.Queue()

# ==== 字幕用コメントログ ====
subtitle_comments = []  # (timestamp_seconds, user_name, comment_text)
stream_start_time = datetime.now()
# ==== 字幕コメントリアルタイム保存 ====
subtitle_dir = None       # 保存先フォルダパス
subtitle_index = 0        # ファイル連番
stream_start_time = datetime.now()

async def admin_console():
    while True:
        cmd = await asyncio.to_thread(input, "[Admin] >>> ")
        await admin_command_queue.put(cmd)

async def admin_processor():
    while True:
        cmd = await admin_command_queue.get()

        if cmd == "fw":
            await arcade_send_queue(("spawn_fireworks", [3, 0.2]))

        elif cmd == "reset":
            config.coin_counter = 0

        elif cmd.startswith("gift "):
            _, file = cmd.split(" ", 1)
            await arcade_send_queue(("spawn_gift", [file]))

        if cmd == "Judy":
            asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia1.png",coin])))

        if cmd == "Nick":
            asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia2.png",coin])))

async def fireworks_queue_worker():
    """花火専用キュー → Arcadeキューへ2秒ごとに流す"""
    while True:
        try:
            data = await fireworks_buffer_queue.get()
            # --- クールタイム指定対応 ---
            if isinstance(data, tuple) and len(data) == 3:
                cmd, args, wait_time = data
            else:
                cmd, args = data
                wait_time = 2.0  # デフォルト

            await arcade_send_queue((cmd, args))
        except Exception as e:
            print(f"[ERROR] fireworks_queue_worker: {e}")
        await asyncio.sleep(wait_time)

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


async def gift_counting(gift_times):
    global gift_counter
    gift_counter += gift_times

async def coin_counting(coin,times):
    global coin_counter
    coin_counter += coin * times
    print("total coin (coin_counter):",coin_counter)

# #いいね関連
# async def on_like_mod(event,streamer_ID):
#     global total_likes
#     # print(event.count)
#     user_id = event.user.unique_id
#     user_like_total_count = event.count
#     minecraft_id = await config.re_mcid(streamer_ID)

#     # print("user:",user_id,"like count... ",user_like_total_count)
#     # 個別カウント更新
#     if user_id not in user_like_count:
#         user_like_count[user_id] = 0

#     user_like_count[user_id] += user_like_total_count
#     # print("user:",user_id,"like count... ",user_like_count[user_id])

#     # 全体カウント更新
#     total_likes += user_like_total_count

#     # 個別ユーザーのイベント
#     if user_like_count[user_id] > USER_LIKE_THRESHOLD:
#         #ログ　
#         now = datetime.now()
#         print(f"🎉 {event.user.nickname} reached {user_like_count[user_id]} likes!")
#         print(f"{event.user.nickname} ({user_id}) liked at {now.strftime('%Y-%m-%d %H:%M:%S')}")
#         # ここにRCONや通知処理を追加可能
#         # await command_send_queue(f'title @a title {{"text":"{USER_LIKE_THRESHOLD}いいねTNT"}}')
#         # await command_send_queue(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
#         # await command_send_queue(f"bedrock tnt 1 {event.user.nickname}")
#         selected = random.choices(
#             config.minecraft_effects,
#             weights=[e[2] for e in config.minecraft_effects],
#             k=1
#         )[0]
#         print(selected)
#         # commandにselectedで取得した０番目内容をフォーマットしたうえで格納
#         command = selected[0].format(player_name=minecraft_id)
#         await command_send_queue(command)
#         await command_send_queue(f'title {minecraft_id} title {{"text":"{selected[1]}"}}')
#         await command_send_queue(f'title {minecraft_id} subtitle {{"text":"{event.user.nickname}"}}')

#         user_like_count[user_id] -= USER_LIKE_THRESHOLD


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
    user_id = event.user.unique_id
    nickname = event.user.nickname
    avatar_urls = event.user.avatar_thumb.m_urls
    now_date = datetime.now().strftime("%Y-%m-%d")
    db = config.nickname_history
    comment = event.comment
    
    # --- キャッシュに無い場合だけ保存 ---
    if user_id not in config.avatar_url_cache:
        if avatar_urls:
            config.avatar_url_cache[user_id] = avatar_urls[0]
            print("[Avatar] New icon saved:", user_id, avatar_urls[0])

            # JSONファイルへの永続保存
            config.save_avatar_cache(config.avatar_url_cache)


    # 初回ユーザー
    if user_id not in db:
        db[user_id] = {
            "history": [
                {"name": nickname, "first_seen": now_date}
            ],
            "latest": nickname
        }
        config.save_nickname_history(db)
        print("[Nickname] 初回登録:", user_id, nickname)
    else:
        # 既存ユーザー → 最新と違うなら履歴追加
        if db[user_id]["latest"] != nickname:
            db[user_id]["latest"] = nickname
            db[user_id]["history"].append({
                "name": nickname,
                "first_seen": now_date
            })
            config.save_nickname_history(db)
            print("[Nickname] 変更検出:", user_id, nickname)


    # あとは通常の処理
    now = datetime.now()
    
    elapsed = (now - stream_start_time).total_seconds()

    # 字幕形式用の蓄積
    write_single_subtitle(nickname, comment)
    print(f"{event.user.nickname} >> {event.comment} at {now.strftime('%Y-%m-%d %H:%M:%S')} form {streamer_ID}")
    logger_viewer.add_log(
        user_id,
        nickname,
        "comment",
        event.comment
    )

def seconds_to_timestamp(sec: float):
    # 00:00:05,123 の形式に変換
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')



def write_single_subtitle(user: str, text: str):
    global subtitle_index, subtitle_dir, stream_start_time

    if subtitle_dir is None:
        print("[SRT] subtitle_dir not initialized")
        return

    subtitle_index += 1
    index_str = f"{subtitle_index:05d}"    # 00001.srt 形式
    filepath = os.path.join(subtitle_dir, f"{index_str}.srt")

    elapsed = (datetime.now() - stream_start_time).total_seconds()
    start = seconds_to_timestamp(elapsed)
    end   = seconds_to_timestamp(elapsed + 3)   # 表示3秒

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"1\n")
        f.write(f"{start} --> {end}\n")
        f.write(f"{user}: {text}\n")

    print(f"[SRT] 字幕保存: {filepath}")

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
        # zootopia1
        if name == "Judy":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia1.png",coin])))
                # --- ランダム選択（nick1 or nick2）---
                shape_name = random.choices(["Judith1", "Judith2"], weights=[0.7, 0.3])[0]
                asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                # await fireworks_buffer_queue.put(("spawn_fireworks_ex", [1, 3.0, shape_name]))

                await asyncio.sleep(0.1)
        # zootopia2
        if name == "Nick":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia2.png",coin])))
                # --- ランダム選択（nick1 or nick2）---
                shape_name = random.choices(["nick1", "nick2"], weights=[0.7, 0.3])[0]
                asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                # await fireworks_buffer_queue.put(("spawn_fireworks_ex", [1, 3.0, shape_name]))

                await asyncio.sleep(0.1)

    elif not event.gift.streakable and not event.streaking:
        asyncio.create_task(gift_counting(times))
        asyncio.create_task(coin_counting(coin,times))

        # zootopia3
        if name == "Judy Pose":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia3.png",coin])))
                for _ in range(3):
                    shape_name = random.choices(["Judith1", "Judith2","nick1", "nick2"], weights=[4, 4,1, 1])[0]
                    asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                    await asyncio.sleep(1.2)

        if name == "Last take":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia4.png",coin])))
                for _ in range(9):
                    shape_name = random.choices(["Judith1", "Judith2","nick1", "nick2"], weights=[1,1,1,1])[0]
                    asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                    await asyncio.sleep(1.2)

        if name == "Movie Moment":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia5.png",coin])))
                for _ in range(9):
                    shape_name = random.choices(["Judith1", "Judith2","nick1", "nick2"], weights=[1,1,1,1])[0]
                    asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                    await asyncio.sleep(1.2)

        if name == "Rollercoaster":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia6.png",coin])))
                for _ in range(9):
                    shape_name = random.choices(["Judith1", "Judith2","nick1", "nick2"], weights=[1,1,1,1])[0]
                    asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                    await asyncio.sleep(1.2)

        if name == "Zootopia Family":
            for _ in range(count):
                asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia7.png",coin])))
                for _ in range(9):
                    shape_name = random.choices(["Judith1", "Judith2","nick1", "nick2"], weights=[1,1,1,1])[0]
                    asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,shape_name])))
                    await asyncio.sleep(1.2)

    # if 5000 <= coin_counter:
    #     while coin_counter > 5000:
    #         await add_time()
    #     asyncio.create_task(time_measurement())
    logger_viewer.add_log(
    event.user.unique_id,
    event.user.nickname,
    "gift",
    f"{event.gift.name} x{event.repeat_count} ({event.gift.diamond_count}coin)"
    )

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
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"Judith2"],2.0)))
        await asyncio.sleep(3.1)
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"nick1"])))
        await asyncio.sleep(3.1)
        asyncio.create_task(arcade_send_queue(("spawn_fireworks_ex", [1, 3.0,"nick2"])))
        await asyncio.sleep(3.1)

async def Zootopia_Family():
    asyncio.create_task(arcade_send_queue(("spawn_gift_balloon", ["assets/images/gift/zootopia7.png",1])))