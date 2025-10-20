from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, FollowEvent, LikeEvent
from TikTokLive.client.errors import UserOfflineError
from datetime import datetime
from mcrcon import MCRcon
import random
import asyncio

#--------------------------------------------------
#このソフトができること
#起動時に指定したURL先に投げられたギフト情報を取得
#ローカルサーバーのマインクラフトにコマンドを送信
#サーバーの指定方法はIPアドレスとポート番号
#グローバルサーバーに対応予定
#受け取ったギフト情報を使ってマインクラフトサーバーにコマンドを送信
#--------------------------------------------------

command_queue = asyncio.Queue()
#--------------------------------------------------
# コマンドワーカー関連
#起動用


# バックグラウンドで動くコマンドワーカー
async def command_worker(mcr):
    while True:
        cmd = await command_queue.get()
        try:
            mcr.command(cmd)# 実際にコマンドを送信
        except Exception as e:
            print (f"Error while executing {cmd}:{e}")
        await asyncio.sleep(0.05) # レート制御（高頻度すぎ防止）


#現在実行中のイベントループを取得する。
#asyncio.create_task(command_worker())
def create_client(username):
    client = TikTokLiveClient(unique_id=username)
#--------------------------------------------------
#いいね関連

    # 個別ユーザーごとのいいね数を保持
    user_like_count = {}
    # 配信全体の累計いいね数
    total_likes = 0

    # しきい値
    USER_LIKE_THRESHOLD = 300
    TOTAL_LIKE_THRESHOLD = 10000

    @client.on(LikeEvent)
    async def on_like(event: LikeEvent):
        global total_likes
        user_id = event.user.unique_id

        # 個別カウント更新
        if user_id not in user_like_count:
            user_like_count[user_id] = 0

        user_like_count[user_id] += 1

        # 全体カウント更新
        total_likes += 1

        # 個別ユーザーのイベント
        if user_like_count[user_id] > USER_LIKE_THRESHOLD:
            #ログ　
            now = datetime.now()
            print(f"🎉 {event.user.nickname} reached {user_like_count[user_id]} likes!")
            print(f"{event.user.nickname} ({user_id}) liked at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            # ここにRCONや通知処理を追加可能
            await command_queue.put(f'title @a title {{"text":"{USER_LIKE_THRESHOLD}いいねTNT"}}')
            await command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
            await command_queue.put(f"bedrock tnt 1 {event.user.nickname}")
            user_like_count[user_id] = 0

        # 全体累計のイベント
        if total_likes > TOTAL_LIKE_THRESHOLD:
            #ログ　
            now = datetime.now()
            print(f"🌟 Total likes reached {total_likes}!")
            print(f"User total: {user_like_count[user_id]}, Global total: {total_likes}")
            # ここにRCONや通知処理を追加可能
            await command_queue.put(f'title @a title {{"text":"{TOTAL_LIKE_THRESHOLD}いいね爆撃"}}')
            await command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
            for i in range(150):
                await command_queue.put(f"bedrock tnt 1 {event.user.nickname}")
                await asyncio.sleep(0.075)
            total_likes = 0



    #--------------------------------------------------
    #フォロー関連
    # すでに反応済みのユーザーを保持するセット
    already_triggered = set()
    #  フォローを受け取った時
    @client.on(FollowEvent)
    async def on_follow(event: FollowEvent):
        user_id = event.user.unique_id
        if user_id not in already_triggered:
            already_triggered.add(user_id)
            await command_queue.put(f"bedrock tnt 3 {event.user.nickname}")
            await command_queue.put('title @a title {"text":"§cフォロー、ありがとう！"}')
            await command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')

    # コメントを受け取ったとき
    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        now = datetime.now()
        print(f"{event.user.nickname} >> {event.comment}"f" at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # --- 個別処理を関数化 ---
    async def blank_info(user,giftname):
        print(f"name:{user}  gift:{giftname}")
    async def heart_me(user):
        print(f"{user} send Heart Me...")
    async def spawn_tnt(user, count, delay=0.1):
        await command_queue.put('title @a title {"text":"1TNT"}')
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
        for i in range(count):
            await command_queue.put(f"bedrock tnt 1 {user}")
            await asyncio.sleep(delay)

    async def spawn_multi_tnt(user, count, per, delay):
        await command_queue.put(f'title @a title {{"text":"{per}TNT"}}')
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
        for i in range(count):
            await command_queue.put(f"bedrock tnt {per} {user}")
            await asyncio.sleep(delay)


    async def spawn_donuts_tnt(user, count, per, delay):
        await command_queue.put(f'title @a title {{"text":"{per * 2}TNT"}}')
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
        for i in range(count):
            await command_queue.put(f"bedrock tnt {per} {user}")
            await asyncio.sleep(delay)

    async def summon_zombies(user, count):
        await command_queue.put('title @a title {"text":"ゾンビのお友達～"}')
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
        for z in range(count):
            for i in range(15):
                await command_queue.put(
                    f'execute at @a run summon zombie ~ ~3 ~ '
                    f'{{IsBaby:0,ArmorItems:[{{}},{{}},{{}},{{id:"minecraft:carved_pumpkin",Count:1}}],'
                    f'ArmorDropChances:[0F,0F,0F,0F],'
                    f'CustomName:"{user}の分身",CustomNameVisible:1}}'
                )
                await asyncio.sleep(0.05)

    async def levitation_effect(user,count,delay):
        await command_queue.put('title @a title {"text":"浮遊"}')
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
        for i in range(count):
            await command_queue.put(f"effect give @a minecraft:levitation {delay} 2")
            await asyncio.sleep(delay)

    async def fill_blocks(user,count):
        await command_queue.put('title @a title {"text":"§c400ブロック埋めたて"}')
        await command_queue.put(f'title @a subtitle {{"text":"ありがとう、{user}"}}')
        for i in range(count):
            await command_queue.put("bedrock fillblock 400")
        await asyncio.sleep(1)

    async def fill_area(user):
        await command_queue.put('title @a title {"text":"§c埋立完了!"}')
        await command_queue.put(f'title @a subtitle {{"text":"ありがとう! {user}"}}')
        await command_queue.put("bedrock fill")
        await asyncio.sleep(1)

    async def corgi_messege(user):
        await command_queue.put('title @a title {"text":"とにかく荒らせ!"}')
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')




    # ギフトを受け取ったとき
    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        #ギフトを受け取るたびに取得する情報
        user = event.user.nickname
        name = event.gift.name

        #ログ用
        now = datetime.now()

        x = round(random.uniform(-1,1),2)
        z = round(random.uniform(-1,1),2)

        # streak 終了時のみ処理
        if event.gift.streakable and not event.streaking or not event.gift.streakable:

            print(f"{user} sent a {name} (x{event.repeat_count}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
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

            #名前　なにで？（バトル、妨害、イベント、枠投げだけ）目標 を　達成したいです。配信時間（毎日OR曜日、時間）やってます。最後の一言（オレをのし上げてくれえ！）

            elif name == "Mishka Bear":
                async def mishka_storm():
                    await command_queue.put('title @a title {"text":"§cTNTの嵐"}')
                    await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
                    await asyncio.sleep(3.20)
                    for i in range(165):
                        await command_queue.put("bedrock tnt 2")
                        await asyncio.sleep(0.05)
                asyncio.create_task(mishka_storm())


            elif name == "Corgi":
                asyncio.create_task(corgi_messege(user))

            elif name == "Galaxy":
                asyncio.create_task(blank_info(user,name))

# 実行開始
async def run(username, rcon_host="127.0.0.1", rcon_pass="3699", rcon_port=25575):
    mcr = MCRcon(rcon_host, rcon_pass, port=rcon_port)
    mcr.connect()

    # ワーカー起動
    asyncio.create_task(command_worker(mcr))

    # TikTokクライアント
    client = create_client(username)
    try:
        await client.connect()
    except UserOfflineError:
        print("⚠️ 配信者がオフラインです。")
    finally:
        mcr.disconnect()


