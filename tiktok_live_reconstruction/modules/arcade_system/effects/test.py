# modules/arcade_system/effects/test.py
# ==============================================
# Arcade テスト用モジュール
# 目的：
#   - arcade.draw_text の実演
#   - システム全体の管理／運用ガイドをコード内に明示
# ==============================================

import arcade
import os

class FloatingText:
	
	"""一時的に画面に文字を表示する軽量エフェクト"""
	def __init__(self, text: str, x: float, y: float, color=arcade.color.CYAN, size=32, lifetime=180,font_name="装甲明朝"):
		self.timer = 0
		self.lifetime = lifetime  # フレーム数（60fpsなら約3秒）
		self.base_color = color

		project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
		abs_path = os.path.join(project_root, self.RELATIVE_FONT_PATH)
		abs_path = os.path.abspath(abs_path).replace("\\", "/")


		# === フォントを1度だけ登録 ===
		if not hasattr(FloatingText, "_font_loaded"):
			if os.path.exists(abs_path):
				arcade.load_font(abs_path)
				FloatingText._font_loaded = True
				print(f"[ARC-FONT] Loaded custom font: {abs_path}")
			else:
				print(f"[ARC-FONT] Warning: font not found → {abs_path}")

		font_name = os.path.splitext(os.path.basename(abs_path))[0]


		self.text_obj = arcade.Text(text, x, y, color, size, font_name=font_name,anchor_x="center", anchor_y="center")

	def update(self, dt: float):
		"""フェードアウト処理"""
		self.timer += 1
		fade_ratio = max(0, 1 - self.timer / self.lifetime)
		self.text_obj.color = (
			int(arcade.color.CYAN[0] * fade_ratio),
			int(arcade.color.CYAN[1] * fade_ratio),
			int(arcade.color.CYAN[2] * fade_ratio),
		)

	def draw(self):
		self.text_obj.draw()

	def is_dead(self):
		return self.timer >= self.lifetime

def test_print(args, window):
	"""
	例: asyncio.create_task(arcade_send_queue(("test_test", ["Hello Arcade!"])))
	"""
	if not args or not isinstance(args[0], str):
		message = "テスト呼び出し: 引数がありません"
	else:
		message = args[0]

	x = window.width / 2
	y = window.height / 2
	text_effect = FloatingText(message, x, y)
	window.layers["overlay"].append(text_effect)
	print("[ARC-TEST] Floating text added:", message)

# ==============================================
# システム運用ガイド（実務向け）
# ==============================================
"""
■ 運用構造
-----------------------------------------------
main.py
 ┣ backend_async()	 … OBS・Minecraft・TikTokLive起動
 ┣ arcade_system.run() … メインスレッドでArcadeウィンドウ実行
 ┗ Queue(shared_queue) … 各モジュールと命令を共有

■ Arcade構造
-----------------------------------------------
modules/arcade_system/
 ┣ core.py	   … Arcadeウィンドウ本体 (GiftWindow)
 ┣ controller.py … コマンド受付・関数呼び出し
 ┗ effects/
	 ┣ sprite.py … ギフト画像の描画
	 ┣ frame.py  … 配信フレームの表示／削除
	 ┣ beams.py  … 光ビームなどのGPUエフェクト
	 ┗ test.py   … テキスト描画や動作確認

■ 動作フロー
-----------------------------------------------
1. TikTokイベント受信 → minecraft_interactive_command.on_gift_mod()
2. on_gift_mod() 内で arcade_send_queue(("spawn_gift", ["path"])) 等を発行
3. core.GiftWindow.update_queue() が受信し controller.handle_command() に渡す
4. controllerが該当モジュール（effects/*.py）の関数を実行
5. Window内で描画・更新処理を行う

■ 拡張方法
-----------------------------------------------
1. 新しい演出を追加する場合：
   - effects/ に新しいファイル (例: fireworks.py) を作成
   - 関数を定義して controller.EFFECT_REGISTRY に登録する
	 例:  "spawn_fireworks": fireworks.spawn_fireworks

2. TikTok連携に組み込む場合：
   - minecraft_interactive_command.py 内で arcade_send_queue() を呼ぶ
   - 例: asyncio.create_task(arcade_send_queue(("spawn_fireworks", ["start"])))

3. 表示確認：
   - TestSystem() の test_input_cord() コンソールから
	 asyncio.create_task(m_intr_c.arcade_send_queue(("test_test", ["Hello"])))
	 で確認可能

■ 注意点
-----------------------------------------------
- Arcadeはメインスレッド専用。asyncioで同時に動かすときはqueue経由。
- 画像・音声・文字は相対パスより絶対パス推奨。
- 大量のエフェクトを使うときは更新負荷に注意。
"""
