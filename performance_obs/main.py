
import sys
import os
print("//sys.path")
print(sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import asyncio
import math
import time
import obsws_python 
import random
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, FollowEvent, LikeEvent

from modules import config,setup
"""
バージョンv0.1
"""
RABBIT_SOURCES = ["雪うさぎ"]

JUMP_HEIGHT = 50  # ピクセル
# 跳ねるスピード（秒）
JUMP_SPEED = 1.0

BASE_PATH = [
    (200, 200),
    (600, 200),
    (600, 600),
    (200, 600),
]

OFFSET_X = 20  # X方向のずれ幅
OFFSET_Y = 160  # Y方向のずれ幅

BASE_Y = 600
JUMP_HEIGHT = 100  # 最大ジャンプの高さ
JUMP_DURATION = 0.25  # 1回のジャンプにかかる時間（秒）
X_SPACING = 100

SCENE_NAME = config.SCENE_NAME
USAGI_FILE = "D:/画像/ギフト画像/雪うさぎ.webp"
usagi_count = 0  # 累計うさぎカウント

def set_source_position(obs_client, source, x, y,scene_item_id):
    """ソースを指定座標に移動"""
    obs_client.set_scene_item_transform(config.SCENE_NAME,scene_item_id,{
            # "positionX": x,
            "positionY": y,
        }
    )



async def smooth_move(obs_client, source, start, end, scene_item_id,duration=2.0, steps=60,):
    """
    ソースをスムーズに移動させる
    :param obs_client: obsws インスタンス
    :param source: ソース名
    :param start: (x, y) 開始位置
    :param end: (x, y) 終了位置
    :param duration: 移動時間 (秒)
    :param steps: 分割数（FPSイメージ）
    """
    start_x, start_y = start
    end_x, end_y = end

    for i in range(steps + 1):
        t = i / steps
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        await asyncio.to_thread(set_source_position,obs_client, source, x, y,scene_item_id)
        await asyncio.sleep(duration / steps)

async def jump(obs_client, source, base_x, base_y, phase_shift=0):
    t = 0.0
    resp = config.obs_client.get_scene_item_id(config.SCENE_NAME,source)
    print(resp)
    scene_item_id = resp.scene_item_id
    print(scene_item_id)
    while True:
        # ジャンプ周期を0〜1に正規化
        t_norm = ((t + phase_shift) % JUMP_DURATION) / JUMP_DURATION
        # 放物線の計算
        offset_y = 4 * JUMP_HEIGHT * t_norm * (1 - t_norm)
        await asyncio.to_thread(set_source_position,obs_client, source, base_x, base_y - offset_y,scene_item_id)
        await asyncio.sleep(1/60)
        t += 1/60

async def bounce(obs_client, source, base_pos, phase_shift=0):
    """
    ソースを上下にバウンドさせる
    base_pos: (x, y) の基準位置
    phase_shift: 動きにずれを入れるための位相
    """
    resp = config.obs_client.get_scene_item_id(config.SCENE_NAME,source)
    print(resp)
    scene_item_id = resp.scene_item_id
    print(scene_item_id)
    
    base_x, base_y = base_pos
    t = 0.0
    while True:
        # サイン波で上下運動
        offset = math.sin((t + phase_shift) * math.pi * 2 / JUMP_SPEED) * JUMP_HEIGHT
        await asyncio.to_thread(set_source_position,obs_client, source, base_x, base_y - offset,scene_item_id)
        await asyncio.sleep(1/60)  # 60fps想定
        t += 1/60
async def performance_system(client,source,index):
    
    # while True:
    SOURCE_NAME = "コメントテキスト-vrpg"
    # text_source = config.SOURCES_NAMES.get(SOURCE_NAME)
    # print(text_source)
    resp = config.obs_client.get_scene_item_id(config.SCENE_NAME,source)
    print(resp)
    scene_item_id = resp.scene_item_id
    print(scene_item_id)
    
    
        # """1つのソースをループで動かす（indexでオフセットを決める）"""
    # オフセットを計算
    offset_x = OFFSET_X * index
    offset_y = OFFSET_Y * index

    # このソース専用のルートを作成
    path = [(x + offset_x, y + offset_y) for (x, y) in BASE_PATH]
    
    
    current = path[0]
    while True:
        for next_pos in path[1:] + [path[0]]:  # ループ
            await smooth_move(config.obs_client, source, current, next_pos,scene_item_id, duration=2.0, steps=120,)
            current = next_pos


used_rabbit_sources = []
async def spawn_usagi(obs_client, index: int):
    """1匹のうさぎを走らせる"""
    source_name = f"usagi_{index}_{int(time.time()*1000)}"
    used_rabbit_sources = source_name
    await asyncio.to_thread(obs_client.create_input,
        SCENE_NAME,
        source_name,
        "image_source",
        {
        "file": USAGI_FILE,
        "positionX": 1000
        },
        True
    )
    resp = config.obs_client.get_scene_item_id(config.SCENE_NAME,source_name)
    # print(resp)
    scene_item_id = resp.scene_item_id
    print(scene_item_id)
    # 初期位置（右端スタート）
    start_x, end_x = 1500 + random.randint(0,100), -200
    base_y = random.randint(200, 1000)
    jump_height = 80
    speed = 15 + random.randint(0,5)
    jump_freq = 0.25

    # ちょっと位置をずらして重なり防止
    offset_y = index * 40

    x = start_x
    t = 0
    await asyncio.sleep(1)
    while x > end_x:
        x -= speed
        y = base_y + offset_y - jump_height * abs(math.sin(t * jump_freq))
        t += 1
        try:
                
            await asyncio.to_thread(obs_client.set_scene_item_transform,
                SCENE_NAME,
                scene_item_id,
                {
                    "positionX": x,
                    "positionY": y,
                }
            )
        except obsws_python.OBSSDKRequestError as e:
            if "!!! No scene items were found !!!" in str(e):
        # すでに削除されている場合は無視
                pass
            else:
                raise
        await asyncio.sleep(0.0166)  # 60fps

    # 走り終わったら削除
    await asyncio.sleep(1)
    await asyncio.to_thread(obs_client.remove_scene_item,SCENE_NAME,scene_item_id)

name = "weathernewslive"
client = TikTokLiveClient(unique_id=name)
print(name)
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
   global usagi_count
   if event.gift.streakable and not event.streaking or not event.gift.streakable:
        """ギフトイベントを処理してうさぎ召喚"""
        for z in range(event.repeat_count):
            usagi_count += 1
            print(z)
        # 累計カウント分うさぎ召喚

        for i in range(usagi_count):
            asyncio.create_task(spawn_usagi(config.obs_client, i))
            await asyncio.sleep(0.5)

# @config.tiktok_client.on(GiftEvent)
async def test_on_gift():
    while True:
        """ギフトイベントを処理してうさぎ召喚"""
        global usagi_count
        usagi_count += 1

        # 累計カウント分うさぎ召喚
        for i in range(usagi_count):
            asyncio.create_task(spawn_usagi(config.obs_client, i))
            await asyncio.sleep(0.5)
        await asyncio.sleep(30)

async def source_name_to_id(scene_name,source_name):
    resp = await asyncio.to_thread(config.obs_client.get_scene_item_id,scene_name,source_name)
    # print(resp)
    scene_item_id = resp.scene_item_id
    # print(scene_item_id)
    return scene_item_id

async def get_usagi_sources(obs_client, scene_name):
    """シーン内から'usagi'を含むソース名をリストで返す"""
    resp = obs_client.get_scene_item_list(scene_name)
    return [item['sourceName'] for item in resp['sceneItems'] if "usagi" in item['sourceName']]

# async def track_usagi(obs_client, scene_name):
#     # 1分後にAを取得
#     await asyncio.sleep(60)
#     A = await asyncio.to_thread(get_usagi_sources, obs_client, scene_name)
#     print("A:", A)

#     # さらに1分後にBを取得
#     await asyncio.sleep(60)
#     B = await asyncio.to_thread(get_usagi_sources, obs_client, scene_name)
#     print("B:", B)

#     # 共通部分をDに格納
#     D = list(set(A) & set(B))
#     print("D (共通):", D)

#     # A, B の情報削除
#     del A
#     del B

#     return D



async def fade_out_source(obs_client, scene_name, source_name,scene_item_id,duration=1.0):
    """
    指定ソースをフェードアウトして削除する
    duration: フェードにかける秒数
    """
    print("try now")
    filter_name = "透明化のための…"
    async with asyncio.Lock():

        # resp = await asyncio.to_thread(config.obs_client.get_scene_item_id,scene_name,source_name)
        # print(resp)
        # scene_item_id = resp.scene_item_id
        # print(scene_item_id)
        # print(f"関数名　source_name_to_id:{await source_name_to_id(scene_name,source_name)}")
        
        print(await asyncio.to_thread(obs_client.get_source_filter,source_name,filter_name))
        await asyncio.to_thread(obs_client.create_source_filter,source_name,filter_name,"color_filter")
        steps = 10
        for i in range(steps):
            alpha = (steps - i) / steps  # 1→0
            settings= {
            
                "opacity": int(alpha * 100)
            }
            await asyncio.to_thread(obs_client.set_source_filter_settings,
                source_name,
                filter_name,
                settings,
                True
            )
            await asyncio.sleep(duration / steps)

        await asyncio.sleep(1)
        print(source_name," success")

        # フェードアウト後に削除
        # await asyncio.to_thread(obs_client.remove_input, source_name)
        await asyncio.to_thread(obs_client.remove_scene_item,SCENE_NAME,scene_item_id)

def get_scene_item_names(obs_client, scene_name):
    """
    指定シーンのシーンアイテム名をリストで取得
    """
    resp = obs_client.get_scene_item_list(scene_name)
    print("333666999 " + resp)
    return [item.source_name for item in resp.scene_items]

async def get_usagi_sources(obs_client, scene_name):
    """シーン内から'usagi'を含むソース名をリストで返す"""
    async with asyncio.Lock():
        resp = None
        while resp is None:
            resp = await asyncio.to_thread(obs_client.get_scene_item_list,(scene_name))
            print("999666333 ",resp)
            # await asyncio.sleep(3)
        usagi_items = []

        for item in resp.scene_items:
            source_name = item['sourceName']
            source_id = item['sceneItemId']
            if "usagi" in source_name.lower():
                usagi_items.append((source_name,source_id))
        # await asyncio.sleep(5)
        print("get sources list")
        return usagi_items
    # return [item for item in resp.scene_items if "usagi" in item.sourceName.lower()]

async def fade_out_checker(obs_client, scene_name, interval=30):
    while True:


        await asyncio.sleep(interval)
        A = await get_usagi_sources(obs_client, scene_name)
        # print("A:", A)
        # A_name_only = [item["sourceName"] for item in await A]

        # さらに1分後にBを取得
        await asyncio.sleep(interval)
        B = await get_usagi_sources(obs_client, scene_name)
        # print("B:", B)
        # B_name_only = [item["sourceName"] for item in await B]

        A_names = {name for name, _ in A}
        B_names = {name for name, _ in B}
        common_names = list(A_names & B_names)

        name_to_id = {name: item_id for name, item_id in A}  # AのIDを優先
        D = [(name, name_to_id[name]) for name in common_names]
        # # 共通部分をDに格納
        # D = list(set(A) & set(B))
        # print("D (共通):", D)

        # A, B の情報削除
        del A
        # del A_name_only
        del B
        # del B_name_only
          # 2分待機
        print("check now...")
        # for source_name, scene_item_id in D:
        while D:
            source_name, scene_item_id = D[0]
            await asyncio.to_thread(obs_client.remove_scene_item,SCENE_NAME,scene_item_id)
            # await fade_out_source(obs_client,scene_name,source_name,scene_item_id)
            print("削除…削除削除削除削除削除削除削除削除ｫｫｫ!!!!!!")
            await asyncio.sleep(1)
            D.pop(0)


async def main():
    global name
    try:
        await setup.setup_scene_and_source(config.obs_client,config.SCENE_NAME,config.SOURCES_NAMES)
        await setup.setup_system()
        # tasks = [asyncio.create_task(performance_system(config.obs_client,s,i)) for i,s in enumerate(config.SOURCES_NAMES)]
        # await asyncio.gather(*tasks)
        rabbit_tasks = []
        # for i, source in enumerate(RABBIT_SOURCES):
        #     base_x = 200 + i * 100  # 横に並べる
        #     base_y = 600
        #     rabbit_tasks.append(asyncio.create_task(bounce(config.obs_client, source, (base_x, base_y), phase_shift=i*0.5)))

        for i, source in enumerate(RABBIT_SOURCES):
            x = 200 + i * X_SPACING
            rabbit_tasks.append(asyncio.create_task(jump(config.obs_client, source, x, BASE_Y, phase_shift=i*0.25)))

        asyncio.create_task(fade_out_checker(config.obs_client,SCENE_NAME))

        if config.is_test_now:

            asyncio.create_task(test_on_gift())
            await asyncio.gather(*rabbit_tasks)
        else:
            name = input("TikTokのユーザー名を入力してください（@は不要）空白なら、muzukiray963: ").strip() or "muzukiray963"

            await asyncio.gather(*rabbit_tasks,asyncio.create_task(client.connect()))

        # await config.tiktok_client.connecet()
    finally:
        print("system finish.")
        await asyncio.sleep(1)
        print("system finish..")
        await asyncio.sleep(1)
        print("system finish...")


if __name__ == "__main__":
    asyncio.run(main())