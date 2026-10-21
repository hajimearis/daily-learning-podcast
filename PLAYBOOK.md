# 每日學習 Podcast：每日作業手冊（給排程任務讀）

## 流程
1. 推 `scripts/YYYY-MM-DD-knowledge.json` 與 `scripts/YYYY-MM-DD-english.json`（日期為台北時間）。
2. GitHub Actions（make-audio）自動合成 mp3、更新 feed.xml；約 8–15 分鐘完成。若合成失敗（edge-tts 偶爾回 "No audio was received"），
   build.log 會留下原因；同一份 scripts 只需用 REST 重跑：
   `gh api -X POST repos/hajimearis/daily-learning-podcast/actions/workflows/make-audio.yml/dispatches -f ref=main`
   （不要用 `gh workflow run`，GraphQL 被擋）。不要為了重跑而改 scripts 內容；若要強制重建才把 `rev` 加 1。
3. 推送後確認 origin/main 出現 `episodes/YYYY-MM-DD-*.mp3`（最多等 20 分鐘，每 15 秒查一次），失敗就重跑一次。

## scripts JSON 格式
```
{"title": "...", "description": "...", "pub": "YYYY-MM-DDT07:00:00+08:00",
 "queue": [["zh","中文句子"],["en","English sentence"],["en-slow","slow English"],["pause",4000]],
 "voices": {"zh":"zh-TW-YunJheNeural","en":"en-US-ChristopherNeural"},
 "pitch": {"zh":"-13Hz","en":"-5Hz"},
 "rate": {"zh":"+5%","en":"+3%","en-slow":"-22%"},
 "fx": "warm", "rev": 1}
```
voices / pitch / rate / fx 請每天原樣照抄上面這組（Chen 已確認：台灣腔低沉男聲、美式英文）。
zh 片段每句不超過約 40 字，句末用全形標點；數字寫成口語（「百分之三點一」），縮寫如 IMF 可直接寫。

## 圖像頁
`tools/page/build_page.py` + `page_template.html`：複製到工作目錄，替換其中的內容資料
（DOMAINS、REVIEW、CHUNKS、PATTERN、PASSAGE_*、OUTPUT_EX、開場與共通思考的文字、scripts 的 title/description/pub），
執行 `python3 build_page.py out.html page_template.html scriptsdir/` 即可同時產出頁面與兩份 scripts JSON，
頁面與音檔使用同一份 queue。頁面發佈到既有 artifact（網址見排程提示，更新前先 read），capabilities 維持 `db`，
卡片進度存在 db 的 `cards` 集合（文件 id = 詞塊 slug；欄位 streak, n, last, due, status）。
