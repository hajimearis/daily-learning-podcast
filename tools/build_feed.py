#!/usr/bin/env python3
"""Regenerate feed.xml and index.html from episodes.json, and prune old episodes.

Usage (from the repository root):
    python3 tools/build_feed.py

To add an episode, append an entry to episodes.json and put the mp3 in episodes/:
  {"id": "2026-10-22-knowledge", "title": "...", "description": "...",
   "file": "episodes/2026-10-22-knowledge.mp3", "duration": 480,
   "pub": "2026-10-22T06:55:00+08:00"}
Size in bytes is read from the file. Episodes older than KEEP_DAYS are dropped
from the feed and their mp3 files are deleted.
"""
import datetime as dt
import email.utils
import html
import json
import os
import sys

BASE = "https://hajimearis.github.io/daily-learning-podcast/"
TITLE = "每日跨領域學習"
AUTHOR = "陳俊源"
DESC = ("每天三個領域的最新訊息與跨領域思考，加上英文詞塊與跟讀練習。"
        "內容為學習用的資訊整理，不構成投資或其他專業建議。")
KEEP_DAYS = 30

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

episodes = json.load(open("episodes.json", encoding="utf-8"))
now = dt.datetime.now(dt.timezone.utc)
for e in episodes:
    e["_pub"] = dt.datetime.fromisoformat(e["pub"])

keep, drop = [], []
for e in episodes:
    (keep if (now - e["_pub"]).days <= KEEP_DAYS else drop).append(e)
for e in drop:
    try:
        os.remove(e["file"])
    except FileNotFoundError:
        pass
episodes = sorted(keep, key=lambda e: e["_pub"], reverse=True)
json.dump([{k: v for k, v in e.items() if k != "_pub"} for e in episodes],
          open("episodes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

x = html.escape


def hms(sec):
    sec = int(sec)
    return "%02d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)


items = []
for e in episodes:
    size = os.path.getsize(e["file"])
    url = BASE + e["file"]
    items.append(f"""    <item>
      <title>{x(e["title"])}</title>
      <description>{x(e["description"])}</description>
      <link>{BASE}</link>
      <guid isPermaLink="false">{x(e["id"])}</guid>
      <pubDate>{email.utils.format_datetime(e["_pub"])}</pubDate>
      <enclosure url="{x(url)}" length="{size}" type="audio/mpeg"/>
      <itunes:duration>{hms(e["duration"])}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{x(TITLE)}</title>
    <link>{BASE}</link>
    <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>
    <description>{x(DESC)}</description>
    <language>zh-TW</language>
    <lastBuildDate>{email.utils.format_datetime(now)}</lastBuildDate>
    <itunes:author>{x(AUTHOR)}</itunes:author>
    <itunes:summary>{x(DESC)}</itunes:summary>
    <itunes:image href="{BASE}cover.png"/>
    <itunes:category text="Education"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
  </channel>
</rss>
"""
open("feed.xml", "w", encoding="utf-8").write(feed)

rows = []
for e in episodes:
    local = e["_pub"].astimezone(dt.timezone(dt.timedelta(hours=8)))
    rows.append(f"""    <article>
      <h2>{x(e["title"])}</h2>
      <p class="meta">{local.strftime("%Y-%m-%d %H:%M")} · {int(e["duration"]) // 60} 分鐘</p>
      <p>{x(e["description"])}</p>
      <audio controls preload="none" src="{x(e["file"])}"></audio>
    </article>""")

page = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{x(TITLE)}</title>
<link rel="alternate" type="application/rss+xml" title="{x(TITLE)}" href="feed.xml">
<style>
:root {{ --bg:#f3f6f8; --surface:#fff; --fg:#14212b; --muted:#566774; --line:#d5dee4; --accent:#1d5c8a; color-scheme: light; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#0f171d; --surface:#17222a; --fg:#e6edf1; --muted:#9badb9; --line:#2b3a45; --accent:#7db7e3; color-scheme: dark; }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:17px/1.8 "Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;
  padding: 28px max(16px, env(safe-area-inset-right,0px)) 48px max(16px, env(safe-area-inset-left,0px)); }}
main {{ max-width: 680px; margin: 0 auto; }}
h1 {{ font-size: 28px; margin: 0 0 6px; line-height: 1.35; }}
h2 {{ font-size: 18px; margin: 0; line-height: 1.5; }}
p {{ margin: 0 0 .8em; }}
.lead {{ color: var(--muted); }}
.sub {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; margin: 20px 0; }}
.sub code {{ display: block; overflow-wrap: anywhere; font: 14px/1.6 ui-monospace,Menlo,Consolas,monospace; margin: 6px 0 10px; }}
button {{ font: inherit; font-size: 15px; min-height: 44px; padding: 8px 16px; background: var(--bg); color: var(--fg); border: 1px solid var(--line); border-radius: 8px; cursor: pointer; }}
article {{ border-top: 1px solid var(--line); padding: 18px 0 6px; }}
.meta {{ color: var(--muted); font-size: 14px; margin: 2px 0 8px; }}
audio {{ width: 100%; margin-bottom: 12px; }}
a {{ color: var(--accent); }}
.note {{ font-size: 13px; color: var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>{x(TITLE)}</h1>
  <p class="lead">{x(DESC)}</p>
  <div class="sub">
    <strong>Podcast 訂閱網址</strong>
    <code id="feed">{BASE}feed.xml</code>
    <button id="copy" type="button">複製網址</button>
  </div>
{chr(10).join(rows)}
  <p class="note">本頁只保留最近 {KEEP_DAYS} 天的集數。</p>
</main>
<script>
document.getElementById("copy").addEventListener("click", function () {{
  var t = document.getElementById("feed").textContent, b = this;
  function ok() {{ b.textContent = "已複製"; }}
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, function () {{ b.textContent = "請長按網址手動複製"; }});
  else b.textContent = "請長按網址手動複製";
}});
</script>
</body>
</html>
"""
open("index.html", "w", encoding="utf-8").write(page)
print("episodes:", len(episodes), "dropped:", len(drop))
