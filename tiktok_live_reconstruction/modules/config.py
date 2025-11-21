import sys
import os
# print("//sys.path")
# print(sys.path)
print(os.path.basename(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import obsws_python as obs
from mcrcon import MCRcon
import queue

# Arcade と TikTokLive が共有するキュー
arcade_queue = queue.Queue()

# tiktok ID
# TikTokのユーザー名

usernames = []


is_test_now = False
is_test = False

gift_counter = 0
combo_counter = 0

last_update_time = 0

attacks_queue = asyncio.Queue()

hp_lock = asyncio.Lock()
MASTER_HP = 10000

MASTER_HEAL_POINT = 100

PLAYER_ATTCK = 1
EVASION_PROBABILITY = 1

current_attacks = []

is_running_vrpg = False

master_hp_before = 0


is_combo_system_connect = False
is_minecraft_server_connect = False
		# --- クライアント作成 ---
# tiktokの接続
name = "muzukiray963"


# obs setting
HOST = "localhost"
PORT = 4455
PASSWORD = "MjKHwza9OEDkkAuD"



obs_client_setting = None



text_queue = asyncio.Queue()
# command_queue = asyncio.Queue()
minecraft_rcon_setup_info = MCRcon("127.0.0.1", "3699", port=25575)

tiktok_name = str()
tiktok_client = str()
SCENE_NAME = "tiktok　自由枠"#str(input("使用するシーンを入力してください。もしなければ作成されます"))tiktok　自由枠




wait_time = 0
max_battle_time = 15 * 60  # 15分間（秒刻み）900秒

# global is_running_vrpg
base_wait = 10
cooldown_time = 900
ramp_time = 30 * 60
last_battle_time = 0
current_probability = 0

current_multiplier = 1

time_measurement_running = False




async def re_mcid(tiktok_id):
	mc_id = tiktok_to_minecraft.get(tiktok_id,"@a")
	return mc_id


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 便利なパス変数を追加
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
FONT_TYPE_SOUKOU = os.path.join(ASSETS_DIR,"fonts","SoukouMincho.ttf")
FONT_TYPE_TOROMAN = os.path.join(ASSETS_DIR,"fonts","toroman.ttf")

# 例: 絶対パスで確認
print("[CONFIG] BASE_DIR:", BASE_DIR)
print("[CONFIG] ASSETS_DIR:", ASSETS_DIR)

tiktok_usernames = []

VIEWERS_DIR = os.path.join(LOGS_DIR, "viewers")
os.makedirs(VIEWERS_DIR, exist_ok=True)

AVATAR_CACHE_PATH = os.path.join(VIEWERS_DIR, "avatar_cache.json")

import json

# 起動時に読み込む
def load_avatar_cache():
    if os.path.exists(AVATAR_CACHE_PATH):
        try:
            with open(AVATAR_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# 保存用
def save_avatar_cache(cache: dict):
    with open(AVATAR_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# 初期化（アプリ起動時）
avatar_url_cache = load_avatar_cache()

NICKNAME_HISTORY_PATH = os.path.join(VIEWERS_DIR, "nickname_history.json")

def load_nickname_history():
    if os.path.exists(NICKNAME_HISTORY_PATH):
        try:
            with open(NICKNAME_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_nickname_history(db: dict):
    with open(NICKNAME_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

nickname_history = load_nickname_history()

POINT_TOTAL = 0