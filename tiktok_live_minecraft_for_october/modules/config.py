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



obs_client_setting = None



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


current_multiplier = 1

time_measurement_running = False


data_file_default = "gifts.json"

player_name = "ray369_muzuki"
print(player_name)

minecraft_effects = [
    [f"/effect give {player_name} speed 60", "スピードが上昇した！", 5],
    [f"/effect give {player_name} slowness 60", "移動速度が低下した…", 2],
    [f"/effect give {player_name} haste 60", "採掘・攻撃速度上昇", 5],
    [f"/effect give {player_name} mining_fatigue 60", "採掘・攻撃速度が低下…", 2],
    [f"/effect give {player_name} strength 60", "力が増した！", 5],
    [f"/effect give {player_name} instant_health 3", "体力を即回復！", 5],
    [f"/effect give {player_name} instant_damage 1", "ダメージを受けた…", 2],
    [f"/effect give {player_name} jump_boost 60 3", "ジャンプ力が上昇！", 4],
    [f"/effect give {player_name} nausea 10", "画面がぐらぐら…", 1],
    [f"/effect give {player_name} regeneration 60", "体力が徐々に回復！", 5],
    [f"/effect give {player_name} resistance 60 1", "ダメージ軽減Lv2！", 4],
    [f"/effect give {player_name} fire_resistance 60", "火炎耐性が付いた！", 5],
    [f"/effect give {player_name} water_breathing 60", "水中でも息ができる！", 5],
    [f"/effect give {player_name} invisibility 60 255 true", "透明になった！", 4],
    [f"/effect give {player_name} blindness 60", "視界が真っ暗…", 1],
    [f"/effect give {player_name} night_vision 60", "この目は闇を見通す！", 5],
    [f"/effect give {player_name} hunger 60", "お腹が減りやすい…", 2],
    [f"/effect give {player_name} weakness 60", "攻撃力が下がった…", 2],
    [f"/effect give {player_name} poison 60", "毒状態になった…", 1],
    [f"/effect give {player_name} wither 60", "ウィザーの呪いだ…", 1],
    [f"/effect give {player_name} health_boost 60", "最大体力が増加！", 4],
    [f"/effect give {player_name} absorption 60", "拡張体力を付与！", 5],
    [f"/effect give {player_name} saturation 60", "お腹が満たされた！", 5],
    [f"/effect give {player_name} glowing 60", "白く光っているッ！！！", 3],
    [f"/effect give {player_name} levitation 60", "浮遊している…", 1],
    [f"/effect give {player_name} luck 60", "アイテム運が上昇！", 4],
    [f"/effect give {player_name} unluck 60", "アイテム運が低下…", 2],
    [f"/effect give {player_name} slow_falling 60", "落下速度が低下！", 4],
    [f"/effect give {player_name} conduit_power 60", "水神様の加護", 5],
    [f"/effect give {player_name} dolphins_grace 60", "泳ぐ速度が上昇！", 5],
    [f"/effect give {player_name} bad_omen 60", "襲撃の不吉な予兆…", 0],
    [f"/effect give {player_name} raid_omen 60", "襲撃が開始される…", 0],
    [f"/effect give {player_name} trial_omen 60", "不吉な試練が始まった…", 0],
    [f"/effect give {player_name} hero_of_the_village 60", "村人に好かれた！", 1],
    [f"/effect give {player_name} darkness 60", "視界が暗くなった…", 1],
    [f"/effect give {player_name} weaving 60", "敵にクモの加護…", 1],
    [f"/effect give {player_name} wind_charged 60", "敵が風の力を溜めた", 2],
    [f"/effect give {player_name} infested 60", "敵は石喰虫を呼ぶ気だ", 2],
    [f"/effect give {player_name} oozing 60", "スライムの気配がする", 2]
]