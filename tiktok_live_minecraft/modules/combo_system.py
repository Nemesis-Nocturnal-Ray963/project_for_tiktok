# コンボシステム
import sys
import os
# print("//sys.path")
# print(sys.path)
print(os.path.basename(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import setup,config,receive

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

async def combo_system_mod():
    config.fade_started = False


    # ソースのIDを取得　よくシーンと間違えるけど、ソースのIDを取得するんだからね
    # scene_list = cl.get_scene_list().scenes
    # scene_names = [s["sceneName"] for s in scene_list]
    combo_text_source = config.SOURCES_NAMES.get("コンボカウントテキスト")
    resp = config.obs_client.get_scene_item_id(config.SCENE_NAME,combo_text_source)

    scene_item_id = resp.scene_item_id
    # resp = cl.get_scene_item_id(SCENE_NAME,USE_NAME)

    # scene_item_id = resp.scene_item_id

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
        if config.gift_counter > config.combo_counter:
            opacity = 100
            config.combo_counter += 1
            config.last_update_time = now
            config.fade_started = False

            for i in range(10):
                
                combosettings = {
                    "text": str(config.combo_counter)+"combo!",
                    "color": int(color_value),
                    "opacity": int(opacity),
                }
                config.obs_client.set_input_settings(combo_text_source, combosettings, overlay=True)
                config.obs_client.set_scene_item_transform(config.SCENE_NAME,scene_item_id,{
                        # "positionX": 50 * (10 - i),
                        # "positionY": 30 * (10 - i),
                        "scaleX":1.0 -(float(i)/20),
                        "scaleY":1.0 -(float(i)/20)
                    })
                await asyncio.sleep(0.015)
            
        if now - config.last_update_time > 30: #30秒間のコンボ受付時間
            config.combo_counter = 0
            config.gift_counter = 0
            config.fade_started = False
        

        if now - config.last_update_time > 20:  # 20秒経過したらフェード開始
            config.fade_started = True
            elapsed = now - (config.last_update_time + 20)
            opacity = max(0, 100 - (elapsed / 10) * 100)  # 10秒で0に
        
        
        combosettings = {
            "text": str(config.combo_counter)+"combo!",
            "color": int(color_value),
            "opacity": int(opacity),
            "outline_opacity": int(opacity),
            # color など他の設定はそのまま
        }
        h = (h + step) % 1.0
        
        config.obs_client.set_input_settings(config.SOURCES_NAMES, combosettings, overlay=True)

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

