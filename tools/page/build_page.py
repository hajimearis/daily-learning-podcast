import html, json, re, sys

OUT = sys.argv[1]

def esc(s):
    return html.escape(s, quote=True)

def plain(s):
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).replace("\n", " ").strip()

def attr_q(items):
    return esc(json.dumps(items, ensure_ascii=False))

# ------------------------------------------------------------------ domains
ECO_FIG = """<figure>
      <svg viewBox="0 0 360 210" role="img" aria-label="全球經濟成長率長條圖：2025 年 3.5%，2026 年 3.1%，2027 年 3.4%">
        <line class="axis" x1="40" y1="170" x2="350" y2="170"/>
        <line class="axis" x1="40" y1="20" x2="350" y2="20"/>
        <text x="34" y="24" text-anchor="end" font-size="11" class="mute">4%</text>
        <text x="34" y="97" text-anchor="end" font-size="11" class="mute">2%</text>
        <line class="axis" x1="40" y1="95" x2="350" y2="95" stroke-dasharray="3 4"/>
        <text x="34" y="174" text-anchor="end" font-size="11" class="mute">0</text>
        <rect class="bar dim" x="70" y="38.75" width="64" height="131.25" rx="2"/>
        <rect class="bar" x="170" y="53.75" width="64" height="116.25" rx="2"/>
        <rect class="bar dim" x="270" y="42.5" width="64" height="127.5" rx="2"/>
        <text x="102" y="32" text-anchor="middle" font-size="14" font-weight="700">3.5%</text>
        <text x="202" y="47" text-anchor="middle" font-size="14" font-weight="700">3.1%</text>
        <text x="302" y="37" text-anchor="middle" font-size="14" font-weight="700">3.4%</text>
        <text x="102" y="190" text-anchor="middle" font-size="13">2025</text>
        <text x="202" y="190" text-anchor="middle" font-size="13">2026 預測</text>
        <text x="302" y="190" text-anchor="middle" font-size="13">2027 預測</text>
      </svg>
      <figcaption>全球經濟成長率。資料：IMF 2026 年 10 月世界經濟展望（經 CGTN 報導）。</figcaption>
    </figure>"""

MKT_FIG = """<figure>
      <ul class="meters">
        <li class="meter"><div class="row"><span>表示公司已有明確的 AI 搜尋策略</span><b>91%</b></div><div class="track"><div class="fill" style="width:91%"></div></div></li>
        <li class="meter"><div class="row"><span>不確定目前做法是否正確</span><b>51%</b></div><div class="track"><div class="fill" style="width:51%"></div></div></li>
        <li class="meter"><div class="row"><span>分不清 GEO 與傳統 SEO 的差別</span><b>56%</b></div><div class="track"><div class="fill" style="width:56%"></div></div></li>
        <li class="meter"><div class="row"><span>覺得自家落後競爭對手</span><b>62%</b></div><div class="track"><div class="fill" style="width:62%"></div></div></li>
      </ul>
      <figcaption>長度依百分比等比例繪製。GEO 是生成式引擎優化，指讓內容更容易被 AI 理解和引用的做法。</figcaption>
    </figure>"""

BRAIN_FIG = """<figure>
      <svg id="dots" viewBox="0 0 360 150" role="img" aria-label="一群神經元中，約 20 個被刺激的神經元以綠色標示"></svg>
      <figcaption>示意圖：綠色代表被刺激的約 20 個「領頭」神經元，灰色代表其他神經元。圖形為概念示意，不是實際數據。</figcaption>
    </figure>"""

DOMAINS = [
    dict(
        id="eco", cls="eco", tag="經濟",
        title="3.1% 的底下，是兩股力量在拉扯",
        lead="IMF 把今年全球成長預測小幅調高到 3.1%，但真正的重點是成長被重新分配了。",
        pre=[
            "10 月 13 日，IMF 發布最新的世界經濟展望：2026 年全球成長預測從 7 月的 3.0% 調到 3.1%，2027 年預計是 3.4%。IMF 的說法是，全球經濟不是單純變慢，也不是變快，而是各國受到的影響不同。中東衝突帶來的能源衝擊拖累一部分經濟體，AI 相關投資熱潮則把成長往上拉。"
        ],
        note=None,
        fig=ECO_FIG,
        metaphor=("比喻：一艘一邊漏水、一邊換新引擎的船",
                  "船的一側在漏水，那是能源價格的壓力；另一側剛裝上新引擎，那是 AI 投資。從遠處看船速很穩，其實船上兩股力量一直在互相拉扯。"),
        link=("跨領域連結　平均數陷阱",
              "全班的平均心率剛好落在目標區間，看起來一切順利。走近一看，有人在輕鬆散步，有人已經喘到跟不上。平均數讓整體好看，卻藏住每個人真正的狀態。看到一個數字，多問一句：它底下的分布長什麼樣子？"),
        src='來源：<a href="https://news.cgtn.com/news/2026-10-13/IMF-raises-2026-global-growth-forecast-to-3-1--1RcEPm28WWI/share_amp.html" target="_blank" rel="noopener">CGTN：IMF raises 2026 global growth forecast to 3.1%</a>（2026-10-13）',
    ),
    dict(
        id="mkt", cls="mkt", tag="行銷",
        title="大家都說有策略，一半的人不確定做對沒",
        lead="當人們開始直接問 AI 問題，品牌有沒有出現在答案裡，成了新的曝光戰場。",
        pre=[],
        note="這是今年 7 月發布的調查，不是這幾天的新聞。調查由行銷代理商 Scribewise 與販售 AI 能見度產品的 Scrunch 共同發布，問卷細節未完整公開，數字請當作趨勢參考。",
        fig=MKT_FIG,
        pre_fig=["他們訪問了 602 位美國行銷與公關人員，問的是品牌在 AI 搜尋裡的能見度。"],
        metaphor=("比喻：招牌與答案",
                  "以前人們靠搜尋引擎找你，像在街上找店面招牌。現在越來越多人直接問 AI：「台灣哪裡有好的空間動力課程？」AI 給出一段答案。答案裡沒有你，對提問的人來說，你就不存在。"),
        link=("跨領域連結　被正確轉述，才算教出去",
              "老師真正教出去的，不是你講了什麼，而是學員回家後能對別人轉述什麼。沒有人完全知道 AI 怎麼挑內容，調查裡也有將近一半的人承認不了解。一個合理的推測是：內容越清楚、具體、一致，被別人提到越多，越容易被引用。把品牌名稱、課程名稱、核心概念每次都用同樣清楚的話講，就是在幫別人，也幫 AI，正確地轉述你。"),
        src='來源：<a href="https://martechseries.com/predictive-ai/ai-platforms-machine-learning/new-research-from-scribewise-and-scrunch-finds-91-of-marketers-claim-an-ai-search-strategy-but-most-are-only-scratching-the-surface/" target="_blank" rel="noopener">MarTech Series：Scribewise 與 Scrunch 的 AI 搜尋調查</a>（2026-07-17）',
    ),
    dict(
        id="brain", cls="brain", tag="腦神經",
        title="只刺激 20 個神經元，就能喚起一個學會的動作",
        lead="動作開始之前，總有一小群神經元先亮起來。這個研究把它們找出來，並直接點亮。",
        pre=[
            "10 月 14 日，加州大學聖地牙哥分校公布一項發表在《Nature》的研究。研究者讓小鼠學一個新動作，用顯微鏡一個一個追蹤運動皮質裡的神經元，發現有些神經元總是在動作開始前先活躍。接著他們用全息光遺傳學技術，只刺激其中約 20 個。這短短的刺激就帶動更大範圍的神經活動，多數情況下小鼠真的做出了學過的動作。"
        ],
        note="這是小鼠研究，不能直接推論到人類。成功與否取決於刺激前大腦的狀態，以及小鼠當時是否專注。對中風、癱瘓或加速學習的應用，目前都還只是未來展望。",
        fig=BRAIN_FIG,
        metaphor=("比喻：第一個音",
                  "一首你很熟的歌，不需要在腦中把每個音符排一遍。第一個音一響，手指就自己跟著走。那個起頭的音，就像這 20 個領頭的神經元。"),
        link=("跨領域連結　起動點與專注",
              "比起一長串動作修正，也許更重要的是給學員一個清楚的起動點，讓身體先帶頭，後面的細節由身體自己組織。另外，專注狀態會影響學習成不成功，所以課堂開頭如何讓大家安定下來，本身就是教學設計的一部分。這裡是借研究當比喻，並不是研究的結論。"),
        src='來源：<a href="https://www.news-medical.net/news/20261014/UC-San-Diego-study-achieves-mind-control-by-stimulating-neurons.aspx" target="_blank" rel="noopener">News-Medical：UC San Diego 刺激神經元的研究</a>（2026-10-14）。論文：Nature，DOI 10.1038/s41586-026-11174-3',
    ),
]

QUEUES = {}

def domain_html(d):
    q = [["zh", d["tag"] + "。"], ["zh", d["title"] + "。"], ["zh", d["lead"]]]
    body = []
    for p in d.get("pre", []):
        body.append(f'<p data-say>{p}</p>')
        q.append(["zh", p])
    if d.get("note"):
        body.append(f'<p class="note" data-say>{d["note"]}</p>')
        q.append(["zh", d["note"]])
    for p in d.get("pre_fig", []):
        body.append(f'<p data-say>{p}</p>')
        q.append(["zh", p])
    q.append(["pause", 600])
    mt, mb = d["metaphor"]
    lt, lb = d["link"]
    q += [["zh", mt], ["zh", mb], ["pause", 600], ["zh", lt], ["zh", lb]]
    QUEUES[d["id"]] = q
    return f'''
  <section class="domain {d["cls"]}" id="sec-{d["id"]}" data-q="{attr_q(q)}">
    <div class="sec-head"><span class="tag">{d["tag"]}</span><button class="btn read" type="button" data-read="#sec-{d["id"]}">▶ 台灣腔朗讀</button></div>
    <h2>{d["title"]}</h2>
    <p class="lead">{d["lead"]}</p>
    {''.join(body)}
    {d["fig"]}
    <h3>{mt}</h3>
    <p>{mb}</p>
    <div class="link-box">
      <h3>{lt}</h3>
      <p>{lb}</p>
    </div>
    <p class="src">{d["src"]}</p>
  </section>'''

# ------------------------------------------------------------------ English lesson
REVIEW = [
    dict(id="forecast", zh="預測", en="forecast", ex="The IMF raised its forecast for global growth.", exzh="IMF 上調了全球成長預測。", tag="eco"),
    dict(id="divergence", zh="分歧、分化", en="divergence", ex="There is a growing divergence between countries.", exzh="國家之間的分化正在擴大。", tag="eco"),
    dict(id="misrepresent", zh="誤述、扭曲", en="misrepresent", ex="Many brands worry that AI might misrepresent them.", exzh="許多品牌擔心 AI 會誤述他們。", tag="mkt"),
    dict(id="resilience", zh="韌性", en="resilience", ex="The economy shows resilience under pressure.", exzh="經濟在壓力下展現韌性。", tag="eco"),
]
CHUNKS = [
    dict(id="raise-a-forecast", zh="上調預測", en="raise a forecast", ex="The IMF raised its forecast for global growth to three point one percent.", exzh="IMF 把全球成長預測上調到百分之三點一。", tag="eco"),
    dict(id="offset-the-impact", zh="抵銷影響", en="offset the impact", ex="Strong AI investment helped offset the energy shock.", exzh="強勁的 AI 投資，幫忙抵銷了能源衝擊。", tag="eco"),
    dict(id="scratch-the-surface", zh="只做到皮毛", en="scratch the surface", ex="Most teams are only scratching the surface of AI search.", exzh="多數團隊對 AI 搜尋只做到皮毛。", tag="mkt"),
    dict(id="long-term-advantage", zh="取得長期優勢", en="gain a long-term advantage", ex="Early adopters may gain a long-term advantage.", exzh="早期採用者可能取得長期優勢。", tag="mkt"),
    dict(id="trigger-a-movement", zh="觸發學會的動作", en="trigger a learned movement", ex="A small signal can trigger a learned movement.", exzh="一個小小的訊號，就能觸發一個學會的動作。", tag="brain"),
]
PATTERN = dict(id="whether-depends-on", zh="A 行不行得通，取決於 B", en="Whether A works depends on B", ex="Whether the lesson succeeds depends on how ready the students are.", exzh="課程是否成功，取決於學生準備得如何。", tag="brain")
OUTPUT_EX = ("Whether the game works depends on how clear the rules are.", "這個遊戲行不行得通，取決於規則有多清楚。")
PASSAGE_EN = ("This week, the IMF raised its forecast for global growth to three point one percent. "
              "The boom in AI investment helped offset the energy shock caused by conflict in the Middle East. "
              "In marketing, a survey found that most teams are only scratching the surface of AI search. "
              "And in brain science, researchers showed that stimulating about twenty neurons can often trigger a learned movement in mice. "
              "Small things can have big effects.")
PASSAGE_ZH = ("這個星期，IMF 把全球成長預測上調到百分之三點一。AI 投資的熱潮，幫忙抵銷了中東衝突造成的能源衝擊。"
              "在行銷領域，一項調查發現，多數團隊對 AI 搜尋只做到皮毛。"
              "在腦科學領域，研究者顯示，刺激大約二十個神經元，往往就能在小鼠身上觸發一個學過的動作。小事情，可以帶來大影響。")

TAGNAME = {"eco": "經濟", "mkt": "行銷", "brain": "腦神經"}

def lesson_queue():
    q = [["zh", "這裡是今天的英文練習。開車請專心，你只需要用耳朵聽，再開口跟著念。"], ["pause", 1000]]
    q += [["zh", "第一段，昨天的回顧。我先說中文，停四秒，請你說出英文，然後我再念答案。"]]
    for r in REVIEW:
        q += [["zh", r["zh"] + "。"], ["pause", 4000], ["en-slow", r["en"]], ["pause", 1200]]
    q += [["zh", "第二段，今天的短文。先聽一次，再聽中文意思，最後慢速再聽一次。"], ["en", PASSAGE_EN], ["pause", 1200],
          ["zh", "中文意思。" + PASSAGE_ZH], ["pause", 1200], ["zh", "再聽一次，慢速。"], ["en-slow", PASSAGE_EN], ["pause", 2000]]
    q += [["zh", "第三段，今天的五個詞塊。每一個，我會念詞塊，說中文，念例句，說例句的意思，再慢速念一次，然後停三秒，請你跟著念。"]]
    for i, c in enumerate(CHUNKS, 1):
        q += [["zh", f"第{'一二三四五'[i-1]}個詞塊。"], ["en", c["en"]], ["zh", "意思是，" + c["zh"] + "。"], ["pause", 600],
              ["en", c["ex"]], ["zh", "意思是，" + c["exzh"]], ["en-slow", c["ex"]], ["pause", 3500]]
    q += [["zh", "第四段，今天的句型。"], ["en", PATTERN["en"]], ["zh", "意思是，" + PATTERN["zh"] + "。"],
          ["en", PATTERN["ex"]], ["zh", "意思是，" + PATTERN["exzh"]], ["en-slow", PATTERN["ex"]], ["pause", 3500]]
    q += [["zh", "第五段，輪到你。請用這個句型，在心裡說一句關於你上一堂課的英文。停八秒。"], ["pause", 8000],
          ["zh", "我的示範是這樣。"], ["en", OUTPUT_EX[0]], ["zh", "意思是，" + OUTPUT_EX[1]], ["pause", 1000],
          ["zh", "今天的五個詞塊，會在明天、三天後、七天後，再出現一次。"]]
    return q

def review_li(r):
    return (f'<li class="rv"><span class="rv-zh">{r["zh"]}</span><span class="rv-en">{r["en"]}</span></li>')

def chunk_li(c):
    return f'''<li class="chunk">
        <div class="c-top"><span class="c-en">{c["en"]}</span><span class="c-tag t-{c["tag"]}">{TAGNAME[c["tag"]]}</span></div>
        <div class="c-zh">{c["zh"]}</div>
        <div class="c-ex">{c["ex"]}</div>
        <div class="c-exzh">{c["exzh"]}</div>
      </li>'''

def card_div(c, kind):
    k = {"review": "昨日回顧", "chunk": "今日詞塊", "pattern": "今日句型"}[kind]
    return f'''<div class="card" data-id="{c["id"]}">
        <div class="card-top"><span class="card-kind">{k}</span><span class="chip" data-chip>未練習</span></div>
        <div class="card-front">{c["zh"]}</div>
        <button class="btn" type="button" data-reveal>看答案</button>
        <div class="card-back" hidden>
          <div class="cb-en">{c["en"]}</div>
          <div class="cb-ex">{c["ex"]}</div>
          <div class="cb-exzh">{c["exzh"]}</div>
          <div class="grade">
            <button class="btn ok" type="button" data-grade="ok">記得</button>
            <button class="btn again" type="button" data-grade="again">不熟</button>
          </div>
        </div>
      </div>'''

english_html = f'''
  <section class="english" id="english" data-q="{attr_q(lesson_queue())}">
    <div class="sec-head"><span class="tag tag-en">英文</span><button class="btn read" type="button" data-read="#english">▶ 台灣腔朗讀英文軌</button></div>
    <h2>今日英文練習</h2>
    <p class="lead">5 個詞塊加 1 個句型，外加昨天的回顧。每個例句都有中文意思，可以先看一遍，再用音檔跟讀。</p>

    <h3>1　昨日回顧　先想，再看答案</h3>
    <ul class="review">{''.join(review_li(r) for r in REVIEW)}</ul>

    <h3>2　今日短文</h3>
    <div class="passage">
      <p class="p-en">{PASSAGE_EN}</p>
      <p class="p-zh">{PASSAGE_ZH}</p>
    </div>

    <h3>3　今日 5 個詞塊</h3>
    <ul class="chunks">{''.join(chunk_li(c) for c in CHUNKS)}</ul>

    <h3>4　今日句型</h3>
    <div class="pattern">
      <div class="p-en">{PATTERN["en"]}</div>
      <p class="p-zh">{PATTERN["zh"]}</p>
      <div class="c-ex">{PATTERN["ex"]}</div>
      <div class="c-exzh">{PATTERN["exzh"]}</div>
    </div>

    <h3>5　輪到你　一句輸出</h3>
    <p>用這個句型，說一句關於你上一堂課的英文。想完再看示範。</p>
    <details class="peek"><summary>看示範</summary>
      <div class="c-ex">{OUTPUT_EX[0]}</div>
      <div class="c-exzh">{OUTPUT_EX[1]}</div>
    </details>
  </section>'''

all_cards = [card_div(r, "review") for r in REVIEW] + [card_div(c, "chunk") for c in CHUNKS] + [card_div(PATTERN, "pattern")]

cards_html = f'''
  <section class="cardsec" id="cards">
    <div class="sec-head"><span class="tag tag-en">複習</span></div>
    <h2>閃卡與進度</h2>
    <p>停車後再用。看到中文，先在心裡說出英文，再按「看答案」，最後誠實選「記得」或「不熟」。記得的卡片會依 1、3、7、14 天的間隔再出現，連續 4 次記得就畢業。</p>
    <div class="progress" id="progress" aria-live="polite">
      <div><b data-p="due">0</b><span>今天到期</span></div>
      <div><b data-p="learn">0</b><span>學習中</span></div>
      <div><b data-p="grad">0</b><span>已畢業</span></div>
      <div><b data-p="new">{len(REVIEW)+len(CHUNKS)+1}</b><span>未練習</span></div>
    </div>
    <p class="note" id="save-note"></p>
    <div class="cards">{''.join(all_cards)}</div>
  </section>'''

check_html = '''
  <section class="check" id="check">
    <div class="sec-head"><span class="tag tag-en">檢核</span></div>
    <h2>怎麼知道有沒有學會</h2>
    <ul class="checklist">
      <li><b>每天</b><span>停車後花 3 分鐘做閃卡，只回答「記得」或「不熟」。</span></li>
      <li><b>每週日</b><span>10 題小測：聽力辨義、中翻英、填空。正確率低於 80% 的項目回到複習表，連續兩次達 90% 才算學會。</span></li>
      <li><b>每週五</b><span>用手機語音輸入說約 60 秒英文，主題是「這週學到的一件事」，把轉出來的文字貼給 Claude，會得到一個最優先修正點和詞彙文法回饋。Claude 只能看文字，聽不到音檔。</span></li>
      <li><b>每月</b><span>重測當月全部詞塊，再做一次英文能力自評，看 7 天後的回憶率有沒有維持在 70% 到 80%。</span></li>
    </ul>
  </section>'''

# ------------------------------------------------------------------ template
TEMPLATE = open(sys.argv[2], encoding="utf-8").read()
page = (TEMPLATE
        .replace("{{DOMAINS}}", "".join(domain_html(d) for d in DOMAINS))
        .replace("{{ENGLISH}}", english_html)
        .replace("{{CARDS}}", cards_html)
        .replace("{{CHECK}}", check_html))
open(OUT, "w", encoding="utf-8").write(page)
print("ok", len(page))


# ---- audio scripts (same queue format the page uses) ----
if len(sys.argv) > 3:
    import os
    outdir = sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    ords = ["第一個領域，", "第二個領域，", "第三個領域，"]
    kq = [["zh", "早安，陳老師。今天是十月二十一日，這是你的跨領域學習時間。今天我們走過三個地方：全球經濟、品牌行銷，還有大腦怎麼學動作。"], ["pause", 1000]]
    for i, d in enumerate(DOMAINS):
        q = QUEUES[d["id"]]
        kq.append(["zh", ords[i] + d["tag"] + "。"])
        kq += q[1:]
        kq.append(["pause", 1500])
    kq += [["zh", "好，我們把三件事串起來。"],
           ["zh", "IMF 的百分之三點一，底下是被拉扯的分化。行銷調查裡的百分之九十一，底下有一半的人其實不確定。大腦裡那個漂亮的動作，底下是一小群領頭的神經元，加上整個大腦當下的狀態。三個故事講同一件事：表面的數字或結果，底下都有結構。"],
           ["pause", 800],
           ["zh", "留一個問題給你，在路上慢慢想。今天，我最常看的那個平均數，底下藏著什麼？是誰被平均掉了？又是哪個起頭的小動作，決定了後面的一切？"],
           ["pause", 800], ["zh", "謝謝你的收聽。祝你今天教學順利，路上平安。"]]
    scripts = {
        "2026-10-21-knowledge": dict(
            title="2026-10-21 知識軌：IMF 預測、AI 搜尋、動作學習（樣品）",
            description="經濟：IMF 把 2026 年全球成長預測上調到 3.1%。行銷：AI 搜尋能見度調查。腦神經：只刺激約 20 個神經元就能喚起學會的動作（小鼠研究）。",
            pub="2026-10-21T12:50:00+08:00", queue=kq),
        "2026-10-21-english": dict(
            title="2026-10-21 英文軌：詞塊與跟讀（樣品）",
            description="昨日回顧、短文、5 個詞塊（例句附中文意思並停頓跟讀）、1 個句型與一句輸出練習。英文為美式發音。",
            pub="2026-10-21T12:51:00+08:00", queue=lesson_queue()),
    }
    for k, v in scripts.items():
        json.dump(v, open(os.path.join(outdir, k + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("scripts written")
