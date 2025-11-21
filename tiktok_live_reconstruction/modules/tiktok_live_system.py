import asyncio
import csv
import os
import random
from datetime import date
from multiprocessing import Queue, Process
import pickle
from TikTokLive import TikTokLiveClient
from TikTokLive.events import *
from TikTokLive.client.errors import UserOfflineError
from modules import logger_viewer
from modules import config, receive
from datetime import datetime
from modules import receive
from TikTokLive.client.web.web_settings import WebDefaults
# from TikTokLive.events import GiftGalleryEvent

WebDefaults.tiktok_sign_api_key = "euler_MDE0NmVkYjE2M2FhOWYxNTliYTE4ODRhOTJiYTBlOTMzMzNlZjhhZjg0ODBhZjk5ZGZkOTc0"
def save_raw_event_auto(event_obj):
    """イベント名を自動抽出して、そのまま.pklとして保存"""
    os.makedirs(config.LOGS_DIR, exist_ok=True)

    event_name = event_obj.__class__.__name__
    now = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{event_name}_{now}.pkl"
    filepath = os.path.join(config.LOGS_DIR, filename)

    try:
        with open(filepath, "wb") as f:
            pickle.dump(event_obj, f)
        print(f"[EVENT-LOG] 保存 → {filepath}")
    except Exception as e:
        print(f"[ERROR] event保存失敗: {e}")

# ============================================================
# TikTokLive マネージャー
# ============================================================
class TikTokLiveManager:
	"""TikTokLive 接続 + イベント管理"""
	
	def __init__(self, tiktok_user_id, base_dir="logs"):
		self.client = TikTokLiveClient(unique_id=tiktok_user_id)

		# CSVログ準備
		self.base_dir = base_dir
		os.makedirs(base_dir, exist_ok=True)
		today = date.today()
		self.filename = os.path.join(base_dir, f"{tiktok_user_id}_{today.year}-{today.month:02d}.csv")
		self.data = []
		if os.path.exists(self.filename):
			with open(self.filename, "r", encoding="utf-8", newline="") as f:
				reader = csv.DictReader(f)
				self.data = list(reader)
		else:
			with open(self.filename, "w", encoding="utf-8", newline="") as f:
				writer = csv.DictWriter(f, fieldnames=["日付", "ユーザー", "ギフト名", "合計コイン数"])
				writer.writeheader()

		# ログ保存キュー
		self.queue = asyncio.Queue()
		asyncio.create_task(self._log_save_worker())
		self.register()

	async def _log_save_worker(self):
		"""CSVへ逐次保存"""
		while True:
			entry = await self.queue.get()
			with open(self.filename, "a", encoding="utf-8", newline="") as f:
				writer = csv.DictWriter(f, fieldnames=["日付", "ユーザー", "ギフト名", "合計コイン数"])
				writer.writerow(entry)

	def log(self, user_name, gift_name, total_coin):
		today = date.today()
		entry = ({"日付": str(today), "ユーザー": user_name, "ギフト名": gift_name, "合計コイン数": total_coin})
		self.data.append(entry)
		self.queue.put_nowait(entry)

	def register(self):
		"""TikTokイベント登録"""
		from TikTokLive.events import (
			LikeEvent, FollowEvent, CommentEvent, GiftEvent,
			LinkMicBattleEvent, LinkmicAnimationEvent, LinkMicAdEvent,
			LinkMicBattleVictoryLapEvent, LinkMicSignalingMethodEvent,
			LinkMicBattlePunishFinishEvent, LinkmicAudienceNoticeEvent,
			LinkMicBattleItemCardEvent, LinkmicBattleTaskEvent,
			LinkMicAnchorGuideEvent, LinkmicBattleNoticeEvent,
			LinkMicArmiesEvent, LinkMicFanTicketMethodEvent, LinkMicMethodEvent, GiftGalleryEvent,GiftUpdateEvent,BarrageEvent,
			FansEventEvent,GoodyBagEvent,JoinEvent,EnvelopeEvent,UnknownEvent
		)
		from TikTokLive.client.web.web_settings import WebDefaults
		# @self.client.on(LikeEvent)
		# async def on_like(event: LikeEvent):
		# 	await receive.on_like_mod(event, self.client.unique_id)

		@self.client.on(FollowEvent)
		async def on_follow(event: FollowEvent):
			await receive.on_follow_mod(event, self.client.unique_id)

		@self.client.on(CommentEvent)
		async def on_comment(event: CommentEvent):
			await receive.on_comment_mod(event, self.client.unique_id)

		@self.client.on(GiftEvent)
		async def on_gift(event: GiftEvent):
			for _ in range(config.current_multiplier):
				await receive.on_gift_mod(event, self.client.unique_id)
			if (event.gift.streakable and not event.streaking) or (not event.gift.streakable):
				total_coin = event.gift.diamond_count * int(event.repeat_count)
				self.log(event.user.nickname, event.gift.name, total_coin)

		@self.client.on(LinkMicBattleEvent)
		async def on_battle(event: LinkMicBattleEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)
			battle_action = event.action
			print(type(battle_action), battle_action)
			# enumオブジェクト は name や value 属性を持っている
			if event.action.name == "BATTLE_ACTION_OPEN":
				print("バトル開始ッ…！")
				await receive.on_battle_start()
			if event.action.name == "BATTLE_ACTION_FINISH":
				print("バトル終了…")
				await receive.on_battle_end()
			# for user_id, result in event.battle_result.items():
			#	 print("user_id:", user_id)
			#	 print("score:", result.score)
			#	 print("user_id:", user_id,"result ","score:", result.score)

		@self.client.on(GiftUpdateEvent)
		async def on_gift_updata(event:GiftUpdateEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)

		@self.client.on(GiftGalleryEvent)
		async def on_gift_gallery(event:GiftGalleryEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)
			# await receive.on_fireworks(event)

		@self.client.on(FansEventEvent)
		async def on_fans_event(event:FansEventEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)

		@self.client.on(GoodyBagEvent)
		async def on_fans_event(event:GoodyBagEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)

		@self.client.on(BarrageEvent)
		async def on_vip_join_event(evant:BarrageEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)
			# print(event.user.nickname)
		@self.client.on(JoinEvent)
		async def on_join_event(event:JoinEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)
			print(event.user.nickname)

		@self.client.on(EnvelopeEvent)
		async def on_fans_event(event:EnvelopeEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)
			# print(event.user.name)

		@self.client.on(UnknownEvent)
		async def on_fans_event(event:UnknownEvent):
			save_raw_event_auto(event)
			print(event.__class__.__name__)


	async def start_client_session(self):
		"""TikTokLive接続"""
		# self.WebDefaults.tiktok_sign_api_key = "euler_MDE0NmVkYjE2M2FhOWYxNTliYTE4ODRhOTJiYTBlOTMzMzNlZjhhZjg0ODBhZjk5ZGZkOTc0"
		try:
			await self.client.connect()
		except UserOfflineError:
			print(f"⚠️ {self.client.unique_id} はオフラインです。")
		finally:
			print(f"配信終了: {self.client.unique_id}")
			await logger_viewer.flush_all()
# ============================================================
# テストシステム
# ============================================================
class Tiktok_Client:
	"this is use TestSystem"
	def __init__(self, unique_id):
		self.unique_id = unique_id

class Gift:
	"this is use TestSystem"
	def __init__(self, name, diamond_count,streakable):
		self.name = name
		self.diamond_count = diamond_count
		self.streakable = streakable

class User:
	"this is use TestSystem"
	def __init__(self, unique_id ,nickname):
		self.unique_id = unique_id
		self.nickname = nickname

class GiftEvent:
	"this is use TestSystem"
	def __init__(self, client, user, gift, repeat_count, streaking):
		self.client = client
		self.user = user
		self.gift = gift
		self.repeat_count = repeat_count
		self.streaking = streaking
class RepeatCount:
	"this is use TestSystem"
	def __init__(self, times):
		self.repeat_count = times
	def __int__(self):
		return self.repeat_count
	def __str__(self):
		return str(self.repeat_count)

class CheckStraking:
	"this is use TestSystem"
	def __init__(self, streaking):
		self.streaking = streaking
	def __str__(self):
		return str(self.streaking)  # print したとき "True" か "False"

	def __bool__(self):
		return self.streaking

class TestSystem:
	"this is use TestSystem"
	def __init__(self):
		self.client = Tiktok_Client("muzukiray963")
		self.user = User("user1111111","test_user_3699")
		self.gift = Gift("test", 1337,True)
		self.repeat_count = RepeatCount(1000)
		self.streaking = CheckStraking(False)
		args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
		self.event = GiftEvent(*args)

	async def change_gift(self,gift_name,coin,streakings):
		self.gift = Gift(gift_name,coin,streakings)
		args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
		self.event = GiftEvent(*args)
		
	async def test_input_cord(self):
		while True:
			test_message = """
使用方法

# ギフトを変更
self.gift.name = "Diamond"
self.repeat_count = RepeatCount(1)
self.gift.streakable = True

# args に最新状態を反映させる
args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)

# GiftEvent を更新
self.event = GiftEvent(*args)

self.client = Tiktok_Client("muzukiray963")
self.user = User("test_user_3699")
self.gift = Gift("test", 9,True)
self.repeat_count = RepeatCount(1)
self.streaking = CheckStraking(False)
args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
self.event = GiftEvent(*args)

# 実行するとき
asyncio.create_task(receive.on_gift_mod(self.event, self.client.unique_id))


args = (self.client, self.user, self.gift, self.repeat_count, self.streaking)
self.event = GiftEvent(*args)
asyncio.create_task(receive.on_gift_mod(self.event, self.client.unique_id))
			"""
			print(test_message)
			for i in range(3):
				print("=== テストプログラム ===")

			test_code = await asyncio.to_thread(input,"I wait enter...>>>")
			if test_code.strip().lower() == "exit":
				print("テスト終了")
				break
			try:
				exec(test_code)
			except Exception as e:
				print("エラー:",e)


# ============================================================
# 同時起動エントリ
# ============================================================
async def start_tiktok_clients(user_ids: list[str]):
	managers = [TikTokLiveManager(uid) for uid in user_ids]
	if len(managers) == 1:
		await managers[0].start_client_session()
	else:
		await asyncio.gather(*(m.start_client_session() for m in managers))
