import sys
import os
print("//sys.path")
print(sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules import setup,config,receive,combo_system


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




async def text_queue_worker(interval: float = 0.1):
    """
    キューから文章を取り出し、一文字ずつ type_text で表示
    """
    while True:
        item = await config.text_queue.get()
        scene_name = item["scene_name"]
        source_name = item["source_name"]
        sentence = item["sentence"]

        current_text = ""
        for ch in sentence:
            current_text += ch
            update_text(scene_name, source_name, current_text)
            await asyncio.sleep(interval)







async def update_skill_source(scene_name: str, source_name: str, new_text: str):
    """ソースのテキストを更新（sceneItemId対応）"""
    try:
        # テキストを更新
        await config.obs_client.set_input_settings(source_name, {"text": new_text}, True)
    except Exception as e:
        print(f"エラー: {source_name} を更新できませんでした → {e}")







def update_text(scene_name: str, source_name: str, new_text: str):
    """ソースのテキストを更新（sceneItemId対応）"""
    try:
        # テキストを更新
        config.obs_client.set_input_settings(source_name, {"text": new_text}, True)
    except Exception as e:
        print(f"エラー: {source_name} を更新できませんでした → {e}")
        

async def master_attacks_kind():
    # """ランダムで1つの技を返す"""
    return random.choice(config.MASTER_ATTACKS)

async def attack_motion(attack):
    if attack["type"] == "attack":
        return attack["power"] * random.randint(1,3)
    elif attack["type"] == "heal":
        return attack["power"]
    else:  # status 技
        return 0

async def hp_changer():
    # global wait_time,config.master_hp_before,config.MASTER_HP
    config.master_hp_before = config.MASTER_HP
    while True:
        if config.wait_time >= config.max_battle_time or config.MASTER_HP <= 0 :
            break
        if config.master_hp_before != config.MASTER_HP:
            await config.text_queue.put({
                "scene_name": config.SCENE_NAME,
                "source_name":"HP-vrpg",
                "sentence":"HP:"+str(config.MASTER_HP)
                })
            HP_settings = {
                "text": "HP:"+str(config.MASTER_HP)
            }



            await asyncio.to_thread(config.obs_client.set_input_settings,"HP-vrpg", HP_settings, True)
            config.master_hp_before = config.MASTER_HP


async def set_input_settings_async(obs_client, source_name, settings):
    # 同期関数を別スレッドで実行
    await asyncio.to_thread(obs_client.set_input_settings, source_name, settings, True)
async def v_rpg_system():
    print("this is first cord")
    config.MASTER_HP = 10000
    # global is_running_vrpg,config.MASTER_HP, current_attacks,MASTER_HEAL_POINT, config.master_hp_before

    config.is_running_vrpg = True
    # PLAYER_ATTCK = 1
    # EVASION_PROBABILITY = 1
    # 選ばれた技（戦闘中に有効な4つ）
    current_attacks = random.sample(config.MASTER_ATTACKS,4)

    async def heal_motion():
            print("HPを回復します…")
            await asyncio.sleep(1)
            print("HPを回復します…")
            await asyncio.sleep(1)
            print("HPを回復します…")
            await asyncio.sleep(1)
            print("HPを回復します…")
            await asyncio.sleep(1)
            print("HPが回復した！")
            # 回復力に応じてHPの回復力が90％から110％の間で変動する
            heal_point = config.MASTER_HEAL_POINT * (float(random.randint(90,110))/100)
            return heal_point


    
    asyncio.create_task(hp_changer())

    print("=== 戦闘開始！")
    print("=== 戦闘開始！有効な技 ===")
    for atk in current_attacks:
        print(f"ID:{atk['id']} 技:{atk['attack_kind']} ギフト:{atk['gift']}")




    # バトル時間中のとき
    while config.wait_time < config.max_battle_time and config.MASTER_HP > 0 :
        config.wait_time += 1
        # HP_settings = {
        #             "text": "HP:" + str(config.MASTER_HP),
        #             "opacity": 100,
        #         }
        
        # 選ばれた技（戦闘中に有効な4つ）
        # current_attacks = []
        # for i in range(4):
        #     attack_choice = await master_attacks_kind()
        #     print(f"技{i}:{attack_choice}")


        # 攻撃情報
        # もし、待ち時間が10で割って0ならprintを出力する
        # もし、60で割って0なら、HPの回復
        TECH_SOURCES = ["1:技テキストゾーン-vrpg", "2:技テキストゾーン-vrpg", "3:技テキストゾーン-vrpg", "4:技テキストゾーン-vrpg"]
        if config.wait_time % 10 == 0:
            if config.wait_time % 60 == 0:
                current_attacks = random.sample(config.MASTER_ATTACKS, 4)
                print("=== 技を入れ替えました！ 新しい有効技 ===")
                for i,atk in enumerate(current_attacks,start=0):
                    source_name = TECH_SOURCES[i]
                    print(f"ID:{atk['id']} 技:{atk['attack_kind']} ギフト:{atk['gift']}")
                    await asyncio.to_thread(config.obs_client.set_input_settings, TECH_SOURCES[i], f"技:{atk['attack_kind']}", True)
                    # await config.text_queue.put({
                    #     "scene_name": config.SCENE_NAME,
                    #     "source_name":source_name,
                    #     "sentence":f"技:{atk['attack_kind']} "
                    #     })
                    await asyncio.sleep(1)

                async with config.hp_lock:
                    heal_point = await heal_motion()
                    config.MASTER_HP += heal_point
                    print(config.MASTER_HP)
            else:
                print(f"{config.wait_time}秒経過。マスターの攻撃を待っています…")

        if config.master_hp_before != config.MASTER_HP:
            await config.text_queue.put({
                "scene_name": config.SCENE_NAME,
                "source_name":"HP-vrpg",
                "sentence":"HP:"+str(config.MASTER_HP)
                })
            config.master_hp_before = config.MASTER_HP
        await asyncio.sleep(1)  # 1秒待機


    # while文から抜けた場合攻撃システムの停止

    config.wait_time = 0
    config.is_running_vrpg = False
    HP_settings = {
                "text": "HP:" + str(config.MASTER_HP),
                "opacity": 0,
                }


async def encount_system():
    # global is_running_vrpg
    # base_wait = 10
    # cooldown_time = 900
    # ramp_time = 30 * 60
    # last_battle_time = 0
    # current_probability = 0


    while True:
        now = time.time()
        if config.is_running_vrpg:
            await asyncio.sleep(config.base_wait)
            continue
        # クールタイム中
        elapsed_since_battle = now - config.last_battle_time
        if elapsed_since_battle < config.cooldown_time:
            current_probability = 0
        else:
            # クールタイム終了後、30分かけて0％→100％に増加
            ramp_elapsed = min(elapsed_since_battle - config.cooldown_time,config.ramp_time)
            # 曲線上昇(sin曲線を使った緩やかに始まり加速)
            fraction = ramp_elapsed / config.ramp_time # 0 ~ 1
            current_probability = math.sin(fraction * math.pi / 2)  * 100
            
            # current_probability = (ramp_elapsed / ramp_time) * 100
            
        roll = random.uniform(0,100)
        if roll <= current_probability:
            print(f"戦闘発生！確率: {current_probability:.1f}% / roll: {roll:.1f}")
            asyncio.create_task(v_rpg_system())
            last_battle_time = now
            current_probability = 0  # 戦闘発生したら確率リセット
        else:
            print(f"戦闘なし。確率: {current_probability:.1f}% / roll: {roll:.1f}")

        await asyncio.sleep(config.base_wait)
        # print("test")
        # await asyncio.sleep(15 * 60)
        # encount_probability = random.randint(1,100)
        # if encount_probability <= 50:  # 50%の確率で戦闘発生
        #     asyncio.create_task(v_rpg_system())
        # await asyncio.sleep(10)  # 10秒ごとに判定
        
# # --- 個別処理を関数化 ---
async def calculate_system(user,giftname,attack_time,attack_id):
    # global MASTER_HP

    # 投げられたギフトに対応する技を取得するもしなければ、None
    attack = next((a for a in config.current_attacks if a['id'] == attack_id), None)


    if not attack:
        print(f"{user} のギフト {giftname} は攻撃できません（ID {attack_id} は未選択）")
        return 0
    for i in range(attack_time):
        value = await attack_motion(attack)

        async with config.hp_lock:
            if attack["type"] == "attack":
                MASTER_HP -= value
                print(f"{user} の攻撃！{value} のダメージ！ 残りHP: {MASTER_HP}")
            elif attack["type"] == "heal":
                MASTER_HP += value
                print(f"{user} の回復！{value} 回復！ 現在HP: {MASTER_HP}")
            elif attack["type"] == "status":
                print(f"{user} が状態変化技 {attack['attack_kind']} を使用！")

    return value


async def get_attack_by_gift(giftname: str):
    """ギフト名から技を取得"""
    return next((a for a in config.MASTER_ATTACKS if a["gift"] == giftname), None)
