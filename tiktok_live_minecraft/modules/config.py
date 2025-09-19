import sys
import os
# print("//sys.path")
# print(sys.path)
print(os.path.basename(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import obsws_python as obs
from mcrcon import MCRcon


is_test_now = False
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
obs_client = obs.ReqClient(host=HOST, port=PORT, password=PASSWORD)


text_queue = asyncio.Queue()
# command_queue = asyncio.Queue()
minecraft_rcon_setup_info = MCRcon("127.0.0.1", "3699", port=25575)

tiktok_name = str()
tiktok_client = str()
SCENE_NAME = "tiktok　自由枠"#str(input("使用するシーンを入力してください。もしなければ作成されます"))tiktok　自由枠
SOURCES_NAMES = {
"ギフトカウントテキスト-vrpg": {"text": "ギフト: 0"},
"コメントテキスト-vrpg": {"text": "コメントなし"},
"HP-vrpg": {"text": "通知なし"},
"1:技テキストゾーン-vrpg": {"text": "通知なし"},
"2:技テキストゾーン-vrpg": {"text": "通知なし"},
"3:技テキストゾーン-vrpg": {"text": "通知なし"},
"4:技テキストゾーン-vrpg": {"text": "通知なし"},
"通知テキスト-vrpg": {"text": "通知なし"},
"通知テキスト1-vrpg": {"text": "通知なし"},
"通知テキスト2-vrpg": {"text": "通知なし"},
"通知テキスト3-vrpg": {"text": "通知なし"},
}
#--

MASTER_ATTACKS = [
    {"id": 1, "attack_kind": "ライター", "power": 10, "type": "attack", "gift": "Rose"},
    {"id": 2, "attack_kind": "せいしんこうげき", "power": 15, "type": "attack", "gift": "TikTok"},
    {"id": 3, "attack_kind": "せいでんき", "power": 12, "type": "attack", "gift": "Popular Vote"},
    {"id": 4, "attack_kind": "ひっぱたく", "power": 25, "type": "attack", "gift": "Love you so much"},
    # {"id": 5, "attack_kind": "みずでっぽう", "power": 20, "type": "attack", "gift": "WaterGun"},
    # {"id": 6, "attack_kind": "でんきショック", "power": 22, "type": "attack", "gift": "Thunder"},
    # {"id": 7, "attack_kind": "つるのムチ", "power": 18, "type": "attack", "gift": "VineWhip"},
    # {"id": 8, "attack_kind": "いわなだれ", "power": 30, "type": "attack", "gift": "Rock"},
    # {"id": 9, "attack_kind": "どくづき", "power": 16, "type": "attack", "gift": "Poison"},
    # {"id": 10, "attack_kind": "ねむりごな", "power": 0, "type": "status", "gift": "SleepDust"},
    # {"id": 11, "attack_kind": "かいふく", "power": 50, "type": "heal", "gift": "HealPotion"}
]


wait_time = 0
max_battle_time = 15 * 60  # 15分間（秒刻み）900秒

# global is_running_vrpg
base_wait = 10
cooldown_time = 900
ramp_time = 30 * 60
last_battle_time = 0
current_probability = 0


# # 個別ユーザーごとのいいね数を保持
# user_like_count = {}
# # 配信全体の累計いいね数
# total_likes = 0

# # しきい値
# USER_LIKE_THRESHOLD = 300
# TOTAL_LIKE_THRESHOLD = 10000