import sys
import os
# print("//sys.path")
# print(sys.path)
print(os.path.basename(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import asyncio

command_queue = asyncio.Queue()
mcr = config.minecraft_rcon_setup_info
async def command_worker_mod():
    print("command worker boot now...")
    while True:
        cmd = await command_queue.get()
        try:
            mcr.command(cmd)# 実際にコマンドを送信
        except Exception as e:
            print (f"Error while executing {cmd}:{e}")
        await asyncio.sleep(0.05) # レート制御（高頻度すぎ防止）