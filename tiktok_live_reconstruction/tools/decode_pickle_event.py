# decode_pickle_event.py
# TikTokLive Event pickle → JSON 変換ツール（完全対応版）

import pickle
import json
import sys


def safe_repr(obj):
    """未知のオブジェクトでも落ちない repr"""
    try:
        return repr(obj)
    except:
        return f"<unserializable {type(obj).__name__}>"


def to_serializable(obj, depth=0):
    """あらゆるイベント構造を安全に JSON 化する"""
    # 再帰が深すぎる場合の保険
    if depth > 8:
        return safe_repr(obj)

    # --- プリミティブ型 ---
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    # --- dict ---
    if isinstance(obj, dict):
        return {str(k): to_serializable(v, depth+1) for k, v in obj.items()}

    # --- list / tuple / set ---
    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(v, depth+1) for v in obj]

    # --- Enum (GiftEvent.action など) ---
    if hasattr(obj, "name") and hasattr(obj, "value"):
        return {"enum": obj.name, "value": obj.value}

    # --- __dict__ を持つオブジェクト (Event, User, Gift, ImageModelなど) ---
    if hasattr(obj, "__dict__"):
        data = {}
        for k, v in obj.__dict__.items():
            data[str(k)] = to_serializable(v, depth+1)
        return data

    # --- __slots__ を持つオブジェクト (ImageModel) ---
    if hasattr(obj, "__slots__"):
        data = {}
        for slot in obj.__slots__:
            if hasattr(obj, slot):
                data[str(slot)] = to_serializable(getattr(obj, slot), depth+1)
        return data

    # --- 未知のオブジェクト ---
    # JSON化できない場合は文字列にする（確実に落ちない）
    return safe_repr(obj)


def decode_pickle(path):
    print(f"[INFO] Loading pickle: {path}")
    with open(path, "rb") as f:
        data = pickle.load(f)

    print("[INFO] Pickle decoded. Converting to JSON-safe structure...")
    return to_serializable(data)


def save_json(data, path):
    json_path = path.rsplit(".", 1)[0] + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] JSON saved → {json_path}")


def main():
    if len(sys.argv) < 2:
        print("使い方: python decode_pickle_event.py event.pkl")
        return

    path = sys.argv[1]
    data = decode_pickle(path)
    save_json(data, path)

    print("\n===== JSON Preview (Top Level) =====")
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
