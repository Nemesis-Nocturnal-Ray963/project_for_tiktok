
import sys
import os
print("//sys.path")
print(sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import setup,config,receive

from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, FollowEvent, LikeEvent
from TikTokLive.client.errors import UserOfflineError
from datetime import datetime
from mcrcon import MCRcon
import random
import asyncio
import time
import obsws_python as obs
import colorsys
from quart import Quart, request,jsonify
import os


async def command_worker():
    while True:
        cmd = await config.command_queue.get()
        try:
            config.mcr.command(cmd)# 実際にコマンドを送信
        except Exception as e:
            print (f"Error while executing {cmd}:{e}")
        await asyncio.sleep(0.05) # レート制御（高頻度すぎ防止）