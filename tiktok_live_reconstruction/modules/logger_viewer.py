import csv, os
from datetime import datetime
from modules import config

VIEWER_LOG_DIR = os.path.join(config.LOGS_DIR, "viewers")
os.makedirs(VIEWER_LOG_DIR, exist_ok=True)

def log_viewer_event(unique_id: str, nickname: str, event_type: str, content: str):
    """
    unique_idごとにCSVへ追記
    event_type: "comment" or "gift"
    content: コメント内容またはギフト詳細
    """
    filename = os.path.join(VIEWER_LOG_DIR, f"{unique_id}.csv")
    is_new = not os.path.exists(filename)
    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["日時", "ユーザー名", "イベント種別", "内容"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([now, nickname, event_type, content])
