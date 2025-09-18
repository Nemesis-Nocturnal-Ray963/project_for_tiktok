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


#--------------------------------------------------
#このソフトができること
#起動時に指定したURL先に投げられたギフト情報を取得
#ローカルサーバーのマインクラフトにコマンドを送信
#サーバーの指定方法はIPアドレスとポート番号
#グローバルサーバーに対応予定
#受け取ったギフト情報を使ってマインクラフトサーバーにコマンドを送信
#--------------------------------------------------
gift_counter = 0
combo_counter = 0
last_update_time = 0
command_queue = asyncio.Queue()
#--------------------------------------------------
# コマンドワーカー関連
#起動用
async def notification_information():
    print("起動しました。終了するには Ctrl+C を押してください。")
    while True:
        print("10分経過…　このプログラムを終了するには Ctrl+C を押してください。")
        await asyncio.sleep(600)  # 600秒 = 10分
        
# バックグラウンドで動くコマンドワーカー
async def command_worker():
    print("command worker boot now...")
    while True:
        cmd = await command_queue.get()
        try:
            mcr.command(cmd)# 実際にコマンドを送信
        except Exception as e:
            print (f"Error while executing {cmd}:{e}")
        await asyncio.sleep(0.05) # レート制御（高頻度すぎ防止）

async def combo_system():
    global combo_counter,gift_counter,last_update_time,fade_started
    fade_started = False
        # --- OBS 接続設定 ---
    HOST = "localhost"
    PORT = 4455
    PASSWORD = "MjKHwza9OEDkkAuD"

        # --- クライアント作成 ---
    cl = obs.ReqClient(host=HOST, port=PORT, password=PASSWORD)
    
    when_create_settings = {
                "font": {"size": 128, "face": "Arial"},
                "text": "test",
                "vertical": False,
                "color": 0,
                "opacity": 100,
                "gradient": False,
                "gradient_color": 0,
                "bk_color": 0,
                "bk_opacity": 0,
                "align": "right",
                "valign": "bottom",
                "outline": True,
                "outline_size": 20,
                "outline_color": 0,
                "outline_opacity": 100,
                }
    SCENE_NAME = "tiktok ギフトスター用ギフト妨害"#str(input("使用するシーンを入力してください。もしなければ作成されます"))
    USE_NAME = "ギフトカウントテキスト"


    # すでにあるか確認
    scene_list = cl.get_scene_list().scenes
    scene_names = [s["sceneName"] for s in scene_list]

    if SCENE_NAME not in scene_names:
        cl.create_scene(SCENE_NAME)
        print(f"シーン '{SCENE_NAME}' を作成しました")
    else:
        print(f"シーン '{SCENE_NAME}' はすでに存在します")

    # シーン内のソース一覧を取得
    source_list = cl.get_scene_item_list(SCENE_NAME)

    # デバッグ用に中身を確認
    for item in source_list.scene_items:
        print(f"sceneItemId: {item['sceneItemId']}, sourceName: {item['sourceName']}")

    # USE_NAME が存在するかどうかを判定
    source_names = any(item["sourceName"] == USE_NAME for item in source_list.scene_items)

    if not source_names:
        cl.create_input(SCENE_NAME, USE_NAME, "text_gdiplus_v3", when_create_settings, True)
        print(f"{USE_NAME} を作成しました")
    else:
        print(f"{USE_NAME} はすでに存在しています。作成をスキップします。")
    
    
    # ソースのIDを取得　よくシーンと間違えるけど、ソースのIDを取得するんだからね

    resp = cl.get_scene_item_id(SCENE_NAME,USE_NAME)

    scene_item_id = resp.scene_item_id

    print("combo system booted...")
    await asyncio.sleep(0.075)
    color_value = 0

    h = 0.0
    step = 0.02  # 色の変化量

    def rgb_to_int(r, g, b):
        """RGB を 0xRRGGBB の整数に変換"""
        return (r << 16) + (g << 8) + b

    while True:
        now = time.time()
        r, g, b = colorsys.hsv_to_rgb(h,1.0,1.0)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        color_value = rgb_to_int(r, g, b)
        if gift_counter > combo_counter:
            opacity = 100
            combo_counter += 1
            last_update_time = now
            fade_started = False

            for i in range(10):
                
                combosettings = {
                    "text": str(combo_counter)+"combo!",
                    "color": int(color_value),
                    "opacity": int(opacity),
                }
                cl.set_input_settings(USE_NAME, combosettings, overlay=True)
                cl.set_scene_item_transform(SCENE_NAME,scene_item_id,{
                        # "positionX": 50 * (10 - i),
                        # "positionY": 30 * (10 - i),
                        "scaleX":1.0 -(float(i)/20),
                        "scaleY":1.0 -(float(i)/20)
                    })
                await asyncio.sleep(0.015)
            
        if now - last_update_time > 30: #30秒間のコンボ受付時間
            combo_counter = 0
            gift_counter = 0
            fade_started = False
        

        if now - last_update_time > 20:  # 20秒経過したらフェード開始
            fade_started = True
            elapsed = now - (last_update_time + 20)
            opacity = max(0, 100 - (elapsed / 10) * 100)  # 10秒で0に
        
        
        combosettings = {
            "text": str(combo_counter)+"combo!",
            "color": int(color_value),
            "opacity": int(opacity),
            "outline_opacity": int(opacity),
            # color など他の設定はそのまま
        }
        h = (h + step) % 1.0
        
        cl.set_input_settings(USE_NAME, combosettings, overlay=True)

        await asyncio.sleep(0.05)


        # if r > 0 and b == 0:
        #     r -= step
        #     g += step
        # elif g > 0 and r == 0:
        #     g -= step
        #     b += step
        # elif b > 0 and g == 0:
        #     r += step
        #     b -= step

        # # 0～255 の範囲を超えないように clamp
        # r = max(0, min(255, r))
        # g = max(0, min(255, g))
        # b = max(0, min(255, b))


async def main():
    # ワーカー開始
    asyncio.create_task(command_worker())
    asyncio.create_task(combo_system())
    # TikTok 接続（イベントループ内で動く）
        # TikTokクライアント起動
    try:
        await client.connect()
    except UserOfflineError:
        print("⚠️ 配信者がオフラインです。配信を開始してください。")
    finally:
        mcr.disconnect()
        print("\n✅ 📺配信が終了しました。お疲れさまでした…💤")
        print("y を押して、Enterで閉じます")

#--------------------------------------------------
#接続基本情報
#サーバー情報
mcr = MCRcon("127.0.0.1", "3699", port=25575)
mcr.connect()

# TikTokのユーザー名
name = input("TikTokのユーザー名を入力してください（@は不要）: ")
client = TikTokLiveClient(unique_id=name)
print(name)
# マイクラのプレイヤー名
playername = "@a"


#現在実行中のイベントループを取得する。
#asyncio.create_task(command_worker())

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
        await command_queue.put(f'title @a title {{"text":"{USER_LIKE_THRESHOLD}いいねTNT"}}')
        await command_queue.put(f'title @a subtitle {{"text":"{event.user.nickname}"}}')
        await command_queue.put(f"bedrock tnt 1 {event.user.nickname}")
        user_like_count[user_id] -= USER_LIKE_THRESHOLD

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
        total_likes -= TOTAL_LIKE_THRESHOLD



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
async def heart_me(user,count):
    print(f"{user} send Heart Me...")
    await command_queue.put(f"bedrock tnt 3 {user}")
    await command_queue.put('title @a title {"text":"§cハートミー！Thx！"}')
    for i in range(count):
        await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
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

async def mishka_storm(user):
    await command_queue.put('title @a title {"text":"§cTNTの嵐"}')
    await command_queue.put(f'title @a subtitle {{"text":"{user}"}}')
    await asyncio.sleep(3.20)
    for i in range(165):
        await command_queue.put("bedrock tnt 2")
        await asyncio.sleep(0.05)

async def gift_counting(gift_times):
    global gift_counter
    gift_counter += gift_times

async def coin_counting(coin,times):
    global coin_counter
    coin_counter += coin * times
    print("total coin :",coin_counter)
    
coin_counter = 0
# ギフトを受け取ったとき
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    global gift_counter,coin_counter
    #ギフトを受け取るたびに取得する情報
    user = event.user.nickname
    name = event.gift.name
    coin = event.gift.diamond_count
    #ログ用
    now = datetime.now()
    x = round(random.uniform(-1,1),2)
    z = round(random.uniform(-1,1),2)
    print(f"{user} sent a {name} (x{event.repeat_count}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # streak 終了時のみ処理
    if event.gift.streakable and not event.streaking or not event.gift.streakable:
        await gift_counting(event.repeat_count)
        await coin_counting(coin,event.repeat_count)


        print(f"{user} sent a {name} (x{event.repeat_count}) at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        if name == "Heart Me":
            asyncio.create_task(heart_me(user,event.repeat_count))

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
        await gift_counting(event.repeat_count)
        await coin_counting(coin,event.repeat_count)


        if name == "Hand Hearts":
            asyncio.create_task(fill_area(user))

        elif name == "Mishka Bear":
            asyncio.create_task(mishka_storm(user))

        elif name == "Corgi":
            asyncio.create_task(corgi_messege(user))

        elif name == "Galaxy":
            asyncio.create_task(blank_info(user,name))


@client.on(LinkMicBattleEvent)
async def on_battle(event: LinkMicBattleEvent):
    print("バトルについて")
    print(event)
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
    print(f"LinkMicArmiesEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)
    # 団結イベント。みんなで、どうやって攻略したかってこと？それとも、すぴちゃれ？人数のタスク？
    # ４コラとか？

@client.on(LinkMicFanTicketMethodEvent)
async def LinkMic_FanTicket_Method_Event(event: LinkMicFanTicketMethodEvent):
    now = datetime.now()
    print(f"LinkMicFanTicketMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)
    # ギフトが投げられたとき、反応した

@client.on(LinkMicMethodEvent)
async def LinkMicMethodEvent(event: LinkMicMethodEvent):
    now = datetime.now()
    print(f"LinkMicMethodEvent {now.strftime('%Y-%m-%d %H:%M:%S')}")
    # print(event)
    # ギフトが投げられたとき、反応した

# 実行開始
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました。配信お疲れ様でした。")
        input("Enterキーを押して閉じてください…")


