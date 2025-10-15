import sys
import os
# print("//sys.path")
# print(sys.path)
# print(os.path.basename(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import asyncio

# command_queue = asyncio.Queue()

coin_count_queue = asyncio.Queue()

# async def command_worker_mod():
#     try:
#         mcr.connect()

#         print("command worker boot now...")
#         while True:
#             cmd = await command_queue.get()
#             try:
#                 mcr.command(cmd)# 実際にコマンドを送信
#             except Exception as e:
#                 print (f"Error while executing {cmd}:{e}")
#             await asyncio.sleep(0.05) # レート制御（高頻度すぎ防止）

async def coin_total_count_worker():
    print("coin total worker boot now...")
    while True:
        total_coin = await coin_count_queue.get()
        total_coin += total_coin
