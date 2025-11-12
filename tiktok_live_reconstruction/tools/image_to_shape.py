# tools/image_to_shape.py
# ==============================================
# 白黒PNG画像 → 花火形状JSON変換ツール
# - 白地に黒(または暗い色)で形を描く
# - 輝度閾値で明るい部分を抽出
# - 中心(0,0)基準の -1～1 座標に正規化
# - assets/fireworks_shapes に JSON 出力
# ==============================================

import os
import json
import numpy as np
from PIL import Image

# === 入出力フォルダ設定 ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "assets", "fireworks_shapes", "converter", "input")
OUT_DIR = os.path.join(PROJECT_ROOT, "assets", "fireworks_shapes")
os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# === 設定値 ===
THRESHOLD = 200   # 0～255：明るさがこれ以上なら描画点と見なす
SCALE = 75     # 花火の全体スケール倍率
SAMPLE_STEP = 50   # ピクセル間引き間隔（小さいほど密）

# === 変換処理 ===
def convert_image_to_shape(img_path: str):
    name = os.path.splitext(os.path.basename(img_path))[0]
    img = Image.open(img_path).convert("L").resize((512, 512))  # グレースケール化
    arr = np.array(img)

    # 明るい部分を抽出（白色領域が花火形状になる）
    ys, xs = np.where(arr > THRESHOLD)

    # 点が多すぎる場合、サンプリングして軽量化
    xs = xs[::SAMPLE_STEP]
    ys = ys[::SAMPLE_STEP]

    h, w = arr.shape
    # -1～1の範囲に正規化し、中心を(0,0)に
    points = np.stack([
        (xs - w / 2) / (w / 2),
        - (ys - h / 2) / (h / 2)
    ], axis=1).tolist()

    data = {"name": name, "scale": SCALE, "points": points}
    out_path = os.path.join(OUT_DIR, f"{name}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] {name}: {len(points)} points → {out_path}")

# === メイン ===
def main():
    files = [f for f in os.listdir(SRC_DIR) if f.lower().endswith(".png")]
    if not files:
        print(f"[INFO] 入力フォルダにPNG画像がありません: {SRC_DIR}")
        print("白黒PNGを配置して再実行してください。")
        return

    for file in files:
        convert_image_to_shape(os.path.join(SRC_DIR, file))

if __name__ == "__main__":
    main()
