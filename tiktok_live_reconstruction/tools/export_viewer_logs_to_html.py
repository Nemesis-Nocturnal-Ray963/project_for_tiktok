# tools/export_viewer_logs_to_html.py
import os, csv, re, json, sys
from datetime import datetime
from collections import defaultdict
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from modules import config  # LOGS_DIR を利用

VIEWERS_DIR = os.path.join(config.LOGS_DIR, "viewers")
REPORT_DIR  = os.path.join(config.LOGS_DIR, "reports", "viewers")
os.makedirs(REPORT_DIR, exist_ok=True)

# 旧ロガーの「内容」文字列をゆるく解釈するための正規表現
GIFT_PAT = re.compile(r"^(?P<gift>.+?)\s*x(?P<count>\d+)\s*\((?P<coin>\d+)\s*coin[s]?\)$", re.I)

STYLE = """
<style>
:root{{--bg:#0b0f14;--panel:#111827;--muted:#9aa4b2;--accent:#38bdf8;--good:#22c55e;--warn:#f59e0b;--bad:#ef4444;}}
*{{box-sizing:border-box}}body{{margin:0;font:14px/1.6 system-ui,Segoe UI,Roboto,Helvetica,Arial;
background:linear-gradient(180deg,#0b0f14 0%,#0e1621 100%);color:#e5e7eb}}
.wrap{{max-width:1080px;margin:40px auto;padding:0 16px}}
.hdr{{display:flex;gap:16px;align-items:center;margin-bottom:24px}}
.badge{{padding:6px 10px;border:1px solid #1f2937;border-radius:999px;background:#0f172a;color:#94a3b8}}
.h1{{font-size:24px;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0 24px}}
@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
.card{{background:linear-gradient(180deg,#0f172a,#0b1220);border:1px solid #1f2937;border-radius:16px;padding:14px}}
.kv{{font-size:12px;color:#94a3b8}}.vl{{font-size:22px;font-weight:700}}
table{{width:100%;border-collapse:separate;border-spacing:0 8px}}
th{{font-size:12px;text-align:left;color:#9aa4b2;font-weight:600;padding:4px 8px}}
td{{padding:10px 12px;background:#0f172a;border:1px solid #1f2937;border-left:none;border-right:none}}
tr td:first-child{{border-left:1px solid #1f2937;border-top-left-radius:10px;border-bottom-left-radius:10px}}
tr td:last-child{{border-right:1px solid #1f2937;border-top-right-radius:10px;border-bottom-right-radius:10px}}
.section{{margin:28px 0}}
.h2{{font-size:16px;font-weight:700;margin:0 0 8px}}
.tag{{font-size:12px;color:#cbd5e1;background:#0b1220;border:1px solid #1f2937;border-radius:8px;padding:4px 8px}}
.muted{{color:#9aa4b2}}.accent{{color:#7dd3fc}}
hr{{border:0;height:1px;background:#1f2937;margin:24px 0}}
.footer{{color:#94a3b8;font-size:12px;margin:24px 0}}
.avatar{{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #1f2937;
    margin-right: 16px;
}}
</style>
"""


HTML_TPL = """<!doctype html>
<html lang="ja">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viewer Report — {uid}</title>
""" + STYLE + """
<div class="wrap">
  <div class="hdr">
    <img src="{avatar_url}" class="avatar" onerror="this.src=https://chatgpt.com/s/m_69159de0b52081919f2d054308128241;">
    <div>
      <div class="h1">Viewer Report</div>
      <div class="badge">unique_id: <span class="accent">{uid}</span></div>
      <div class="badge">latest nickname: <span class="accent">{nickname}</span></div>
      <div class="badge">updated: {updated}</div>
    </div>
  </div>
  <div class="grid">
    <div class="card"><div class="kv">コメント数</div><div class="vl">{n_comments}</div></div>
    <div class="card"><div class="kv">ギフト回数</div><div class="vl">{n_gifts}</div></div>
    <div class="card"><div class="kv">推定コイン合計</div><div class="vl">{sum_coins}</div></div>
    <div class="card"><div class="kv">最終アクティブ</div><div class="vl">{last_ts}</div></div>
  </div>

  <div class="section">
    <div class="h2">タイムライン</div>
    <table>
      <thead><tr><th>日時</th><th>種別</th><th>内容</th></tr></thead>
      <tbody>
        {rows_timeline}
      </tbody>
    </table>
  </div>

  <div class="section">
    <div class="h2">ギフト詳細</div>
    <table>
      <thead><tr><th>日時</th><th>ギフト名</th><th>回数</th><th>コイン</th></tr></thead>
      <tbody>{rows_gifts}</tbody>
    </table>
  </div>

  <div class="section">
    <div class="h2">名前の変遷</div>
    <table>
      <thead><tr><th>日付</th><th>名前</th></tr></thead>
      <tbody>
        {rows_name_history}
      </tbody>
    </table>
  </div>

  <div class="section">
    <div class="h2">コメント一覧</div>
    <table>
      <thead><tr><th>日時</th><th>コメント</th></tr></thead>
      <tbody>{rows_comments}</tbody>
    </table>
  </div>

  <hr>
  <div class="footer">自動生成: {gen_ts}</div>
</div>
</html>
"""


INDEX_TPL = """<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viewer Reports</title>""" + STYLE + """<div class="wrap">
  <div class="hdr"><div class="h1">Viewer Reports Index</div><div class="badge">total viewers: {n}</div></div>
  <div class="section">
    <table><thead><tr><th>unique_id</th><th>latest nickname</th><th>コメント数</th><th>ギフト回数</th><th>コイン合計</th><th>リンク</th></tr></thead>
    <tbody>{rows}</tbody></table>
  </div>
  <div class="footer">自動生成: {gen_ts}</div>
</div>
</html>
"""


def _parse_old_content(s:str):
    """旧CSV(内容カラムにまとめ書き)対応。成功時 dict を返す。"""
    m = GIFT_PAT.match(s.strip())
    if not m: return None
    d = m.groupdict()
    return {
        "gift_name": d["gift"].strip(),
        "repeat": int(d["count"]),
        "coins": int(d["coin"])
    }

def _read_viewer_csv(path):
    # 2系統に対応:
    # 1) 旧: [日時, ユーザー名, イベント種別, 内容]
    # 2) 新(推奨): [日時, ユーザー名, 種別, コメント, ギフト名, 回数, コイン]
    data = []
    latest_nick = ""
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        hdr = [h.strip() for h in reader.fieldnames or []]
        for r in reader:
            ts = r.get("日時") or r.get("日付") or ""
            nick = r.get("ユーザー名") or r.get("ユーザー") or ""
            latest_nick = nick or latest_nick
            t = r.get("イベント種別") or r.get("種別") or ""
            base = {"ts": ts, "nickname": latest_nick, "type": t}

            if "内容" in hdr:
                content = r.get("内容","")
                if t.lower()=="comment":
                    base.update({"comment": content})
                elif t.lower()=="gift":
                    parsed = _parse_old_content(content) or {}
                    base.update({
                        "gift_name": parsed.get("gift_name",""),
                        "repeat": parsed.get("repeat", 1),
                        "coins": parsed.get("coins", 0),
                    })
                data.append(base)
            else:
                # 新ヘッダ想定
                base.update({
                    "comment": r.get("コメント","") or "",
                    "gift_name": r.get("ギフト名","") or "",
                    "repeat": int(r.get("回数","0") or 0),
                    "coins": int(r.get("コイン","0") or 0),
                })
                data.append(base)
    return data, latest_nick

def _safe_ts(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z","")).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts

def _row_td(*cells):
    tds = "".join(f"<td>{c}</td>" for c in cells)
    return f"<tr>{tds}</tr>"

def build_reports():
    index_rows = []
    gen_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name_db = config.nickname_history
    avatar_db = config.avatar_url_cache
    for fn in sorted(os.listdir(VIEWERS_DIR)):
        if not fn.endswith(".csv"): continue
        uid = os.path.splitext(fn)[0]
        path = os.path.join(VIEWERS_DIR, fn)

        # ★ avatar_url をここで取得する（uid が決まった直後）
        avatar_url = avatar_db.get(uid, "")
        if not avatar_url:
            avatar_url = "https://chatgpt.com/s/m_69159de0b52081919f2d054308128241"   # ← 2-1 の処理

        name_info = name_db.get(uid, {"history": [], "latest": ""})

        recs, latest_nick = _read_viewer_csv(path)

        # 集計
        n_comments = sum(1 for r in recs if r.get("type","").lower()=="comment")
        gift_recs = [r for r in recs if r.get("type","").lower()=="gift"]
        n_gifts   = len(gift_recs)
        sum_coins = sum(int(r.get("coins") or 0) for r in gift_recs)
        last_ts   = _safe_ts(max((r.get("ts","") for r in recs), default=""))

        # タイムライン行
        timeline = []
        # 日時でソート可能なら
        def _key(r):
            try: return datetime.fromisoformat(r.get("ts","").replace("Z",""))
            except: return datetime.min

        for r in sorted(recs, key=_key):
            kind = r.get("type","")
            if kind.lower()=="comment":
                timeline.append(_row_td(_safe_ts(r.get("ts","")), "コメント", r.get("comment","")))
            elif kind.lower()=="gift":
                g = r.get("gift_name","")
                c = r.get("coins",0)
                rp= r.get("repeat",1)
                timeline.append(_row_td(_safe_ts(r.get("ts","")), "ギフト", f"{g} x{rp} / {c} coin"))

        # ギフト詳細
        rows_gifts = []
        for r in sorted(gift_recs, key=_key, reverse=True):
            rows_gifts.append(_row_td(
                _safe_ts(r.get("ts","")),
                r.get("gift_name",""),
                r.get("repeat",1),
                r.get("coins",0),
            ))

        rows_name_history = ""   # ← 初期化を忘れない
        for entry in name_info.get("history", []):
            rows_name_history += f"""
              <tr>
                <td>{entry.get('first_seen', '')}</td>
                <td>{entry.get('name', '')}</td>
              </tr>
            """

        # コメント一覧
        rows_comments = []
        comments = [r for r in recs if r.get("type","").lower()=="comment"]
        for r in sorted(comments, key=_key, reverse=True):
            rows_comments.append(_row_td(_safe_ts(r.get("ts","")), r.get("comment","")))

        # 出力
        html = HTML_TPL.format(
            uid=uid,
            nickname=latest_nick or "unknown",
            updated=gen_ts,
            avatar_url=avatar_url,
            n_comments=n_comments,
            n_gifts=n_gifts,
            sum_coins=sum_coins,
            last_ts=last_ts or "-",
            rows_timeline="\n".join(timeline) or _row_td("—","—","—"),
            rows_gifts="\n".join(rows_gifts) or _row_td("—","—","—","—"),
            rows_comments="\n".join(rows_comments) or _row_td("—","—"),

            rows_name_history=rows_name_history,

            gen_ts=gen_ts,
        )
        out_path = os.path.join(REPORT_DIR, f"{uid}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        index_rows.append(_row_td(uid, latest_nick or "-", n_comments, n_gifts, sum_coins,f'<a class="tag" href="{uid}.html">open</a>'))

    index_html = INDEX_TPL.format(n=len(index_rows), rows="\n".join(index_rows) or _row_td("—","—","—","—","—","—"), gen_ts=gen_ts)
    with open(os.path.join(REPORT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    if not os.path.isdir(VIEWERS_DIR):
        raise SystemExit(f"not found: {VIEWERS_DIR}")
    build_reports()
    print("OK:", REPORT_DIR)
