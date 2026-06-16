from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
import time
import re
import feedparser
import anthropic
import requests
from notion_client import Client
from datetime import datetime, timedelta, timezone

# ── 환경 변수 ──────────────────────────────────────────
CLAUDE_API_KEY      = os.environ["CLAUDE_API_KEY"]
TELEGRAM_BOT_TOKEN  = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID    = os.environ["TELEGRAM_CHAT_ID"]
NOTION_API_KEY      = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID  = os.environ["NOTION_DATABASE_ID"]       # VC Intel DB
NARRATIVE_DB_ID     = os.environ.get("NARRATIVE_DATABASE_ID", "")  # Narrative Radar DB

# ── 블로그 소스 ───────────────────────────────────────
# ── 소스 기준: 메커니즘/이해관계 분석하는 것만. 미디어/마케팅 제외 ──
BLOG_SOURCES = [
    # VC/리서처 블로그 (RSS)
    {"name": "Dragonfly",         "url": "https://medium.com/feed/dragonfly-research",         "type": "rss"},
    {"name": "Arthur Hayes",      "url": "https://cryptohayes.substack.com/feed",              "type": "rss"},
    {"name": "Spartan Medium",    "url": "https://medium.com/feed/the-spartan-group",           "type": "rss"},
    {"name": "Delphi Digital",    "url": "https://members.delphidigital.io/feed",               "type": "rss"},
    {"name": "Blockworks Research","url": "https://blockworks.co/feed",                         "type": "rss"},
    # 프로토콜 공식 (메커니즘 직접 설명)
    {"name": "Uniswap Blog",      "url": "https://blog.uniswap.org/rss.xml",                   "type": "rss"},
    {"name": "Aave Blog",         "url": "https://medium.com/feed/aave",                       "type": "rss"},
    {"name": "Hyperliquid",       "url": "https://hyperliquid.substack.com/feed",              "type": "rss"},
    # VC 스크래핑 (RSS 없는 곳)
    {"name": "a16z Crypto",       "url": "https://a16zcrypto.com/posts/",                      "type": "scrape"},
    {"name": "Paradigm",          "url": "https://www.paradigm.xyz/writing",                   "type": "scrape"},
    {"name": "Multicoin Capital", "url": "https://multicoin.capital/writing/",                 "type": "scrape"},
    {"name": "Pantera Capital",   "url": "https://panteracapital.com/blockchain-letter/",      "type": "scrape"},
    {"name": "Galaxy Digital",    "url": "https://www.galaxy.com/insights/",                   "type": "scrape"},
]

URL_EXCLUDE_KEYWORDS = [
    "/team/", "/careers/", "/jobs/", "/about/", "/portfolio/",
    "/contact/", "/press/", "/events/", "/legal/", "/privacy/",
    "/login/", "/subscribe/", "/newsletter/", "/search/",
    "/leadership/", "/board/", "/newsroom/", "/shop/",
    "/our-team/", "/accelerator/", "/voices-onchain/", "/readwriteown/",
]

X_ACCOUNTS = [
    {"handle": "a16zcrypto",      "name": "a16z Crypto"},
    {"handle": "paradigm",        "name": "Paradigm"},
    {"handle": "dragonfly_xyz",   "name": "Dragonfly"},
    {"handle": "PanteraCapital",  "name": "Pantera Capital"},
    {"handle": "Polychain",       "name": "Polychain"},
    {"handle": "GalaxyDigital",   "name": "Galaxy Digital"},
    {"handle": "TheSpartanGroup", "name": "Spartan Group"},
    {"handle": "HashKey_Capital", "name": "HashKey Capital"},
    {"handle": "YZiLabs",         "name": "YZi Labs"},
    {"handle": "cdixon",          "name": "Chris Dixon"},
    {"handle": "hosseeb",         "name": "Haseeb Qureshi"},
    {"handle": "KyleSamani",      "name": "Kyle Samani"},
    {"handle": "pmarca",          "name": "Marc Andreessen"},
    {"handle": "CryptoHayes",     "name": "Arthur Hayes"},
    {"handle": "VitalikButerin",  "name": "Vitalik Buterin"},
    {"handle": "tushar_jain",     "name": "Tushar Jain"},
    {"handle": "balajis",         "name": "Balaji Srinivasan"},
    {"handle": "paultaylorvc",    "name": "Paul Taylor"},
    {"handle": "stacy_muur",      "name": "stacy_muur"},
    {"handle": "rajgokal",        "name": "Raj Gokal"},
    {"handle": "StaniKulechov",   "name": "Stani Kulechov"},
    {"handle": "Delphi_Digital",  "name": "Delphi Digital"},
    {"handle": "MessariCrypto",   "name": "Messari"},
    {"handle": "RyanSAdams",      "name": "Ryan Adams"},
    {"handle": "DefiIgnas",       "name": "DefiIgnas"},
    {"handle": "Defi_Warhol",     "name": "DeFi Warhol"},
    {"handle": "RyanWatkins_",    "name": "Ryan Watkins"},
]

VC_PORTFOLIO = {
    "a16z Crypto":       "Stablecoins, Payments, RWA, Agentic Commerce. Fund 5 ($2.2B).",
    "Paradigm":          "ZK, DeFi Infra, Prediction Markets. AI+Robotics로 확장 중 ($1.5B).",
    "Multicoin Capital": "Solana, DePIN, AI×Crypto. High-conviction contrarian 전략.",
    "Pantera Capital":   "RWA, Stablecoins, Prediction Markets, Perps.",
    "Galaxy Digital":    "Institutional, Trading, RWA 토큰화.",
    "Dragonfly":         "Stablecoin Infra, On-chain Payments, Trading Infra. Fund 4 ($650M).",
    "Polychain":         "L1/L2, ZK, DePIN, AI-driven protocols.",
    "Spartan Group":     "DeFi, L1 생태계. dYdX, Aave, Pendle.",
    "HashKey Capital":   "아시아 중심. $500M Digital Asset Treasury Fund.",
    "YZi Labs":          "구 Binance Labs 계열.",
    "Chris Dixon":       "a16z GP. Web3 철학 + 장기 비전.",
    "Haseeb Qureshi":    "Dragonfly 파트너. 논리적 분석.",
    "Kyle Samani":       "Multicoin 파트너. Thesis 끝판왕.",
    "Marc Andreessen":   "a16z. 매크로 + 빅픽처.",
    "Arthur Hayes":      "BitMEX 창업자. 매크로 에세이.",
    "Vitalik Buterin":   "Ethereum 창시자. 기술 + 철학.",
    "Tushar Jain":       "Multicoin 파트너. Thesis 공동 작성.",
    "Balaji Srinivasan": "극단적 Contrarian. Network State.",
    "Paul Taylor":       "현실적·비관적 분석.",
    "stacy_muur":        "RWA + 매크로. Contrarian.",
    "Raj Gokal":         "Solana 공동창업자.",
    "Stani Kulechov":    "Aave 창업자. DeFi 거버넌스.",
    "Delphi Digital":    "리서치+VC 겸업. DeFi, L1, GameFi.",
    "Messari":           "리서치 기관. DeFi, AI, DePIN.",
    "Ryan Adams":        "Bankless. Ethereum 비전.",
    "DefiIgnas":         "DeFi 리서치 스레드.",
    "DeFi Warhol":       "DeFi 메커니즘 설명.",
    "Ryan Watkins":      "Messari 리서처. 시장 구조.",
}

SEEN_FILE = "seen_entries.json"

# ── 소스 가중치 (클러스터링용) ─────────────────────────
SOURCE_WEIGHTS = {
    "blog":  3,
    "tweet": 1,
}

# ── seen 관리 ─────────────────────────────────────────
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# ── 블로그 스크래핑 ───────────────────────────────────
def scrape_blog_content_simple(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        from html.parser import HTMLParser
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self._skip = False
            def handle_starttag(self, tag, attrs):
                if tag in ('script', 'style', 'nav', 'footer'):
                    self._skip = True
            def handle_endtag(self, tag):
                if tag in ('script', 'style', 'nav', 'footer'):
                    self._skip = False
            def handle_data(self, data):
                if not self._skip:
                    self.text.append(data)
        p = TextExtractor()
        p.feed(r.text)
        return " ".join(p.text)[:6000]
    except:
        return ""

def fetch_rss_links(source):
    feed = feedparser.parse(source["url"])
    links = []
    for entry in feed.entries[:5]:
        link = entry.get("link", "")
        title = entry.get("title", "")
        published = entry.get("published", datetime.now().strftime("%Y-%m-%d"))
        if link and title:
            links.append({"title": title, "link": link, "published": published})
    return links

def fetch_new_blogs(seen):
    new_entries = []
    for source in BLOG_SOURCES:
        try:
            source_type = source.get("type", "scrape")
            if source_type == "rss":
                links = fetch_rss_links(source)
            else:
                links = []  # scrape 타입은 GitHub Actions에서 제외
            print(f"{source['name']} 블로그: {len(links)}개 링크")
            for item in links:
                if item["link"] not in seen:
                    content = scrape_blog_content_simple(item["link"])
                    if len(content) > 500:
                        new_entries.append({
                            "source": source["name"],
                            "title": item["title"],
                            "link": item["link"],
                            "content": content,
                            "published": item.get("published", datetime.now().strftime("%Y-%m-%d")),
                            "type": "blog",
                        })
                    seen.add(item["link"])
                    time.sleep(1)
        except Exception as e:
            print(f"블로그 오류 ({source['name']}): {e}")
    return new_entries

# ── X 트윗 스크래핑 (Nitter RSS 방식) ────────────────
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.net",
    "https://lightbrd.com",
]

_working_nitter = None

def get_working_nitter():
    global _working_nitter
    if _working_nitter:
        return _working_nitter
    for instance in NITTER_INSTANCES:
        try:
            r = requests.get(f"{instance}/a16zcrypto/rss", timeout=5)
            if r.status_code == 200:
                print(f"[Nitter] 사용 중: {instance}")
                _working_nitter = instance
                return instance
        except:
            continue
    return None

def fetch_tweets(account):
    instance = get_working_nitter()
    if not instance:
        return []
    tweets = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    try:
        feed = feedparser.parse(f"{instance}/{account['handle']}/rss")
        count = 0
        for entry in feed.entries:
            if count >= 3:
                break
            text = entry.get('summary', entry.get('title', ''))
            if text.startswith('RT @'):
                continue
            if len(text) < 100:
                continue
            try:
                pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                if pub < cutoff:
                    continue
            except:
                pass
            link = entry.get('link', '')
            tweets.append({"content": text[:500], "link": link, "date": entry.get('published', '')})
            count += 1
        time.sleep(0.3)
    except Exception as e:
        print(f"트윗 오류 (@{account['handle']}): {e}")
    return tweets

# ── 프롬프트 ──────────────────────────────────────────
# ══════════════════════════════════════════════════════
# 프롬프트 — 블로그/아티클 분석
# ══════════════════════════════════════════════════════
BLOG_ANALYSIS_PROMPT = """
당신은 크립토/DeFi 시장 시니어 애널리스트입니다.
독자는 DeFi를 깊이 이해하는 전문가입니다.

표면적 사실 요약 절대 금지.
반드시 뒤에서 무슨 일이 벌어지는지, 누가 이득/손해인지, 다음에 어떤 영향이 오는지까지 분석합니다.

[출처] {source}
[VC 컨텍스트] {portfolio}
[제목] {title}
[내용] {content}

중요도 판단 기준:
- high: 메커니즘/이해관계 분석 포함 + 새로운 프레임워크 + 내러티브 전환 신호
- medium: 관련 섹터 다루지만 현황 정리 수준
- low: 단순 공지/채용/이벤트/마케팅

JSON만 반환. 설명 없이 순수 JSON:
{{
  "importance": "high 또는 medium 또는 low",
  "background": "왜 지금 이 글이 나왔는지 맥락 (시장 상황, VC 포지션)",
  "what": "구체적으로 무슨 일/주장인지",
  "mechanism": "실제로 어떻게 작동하는지 — 기술/경제 메커니즘",
  "interests": "누가 이득이고 누가 손해인지 — 이해관계 구조",
  "impact": "다음에 어떤 영향이 오는지 — 단기/중기",
  "counter": "이 논지의 약점과 반대 포지션",
  "watch_next": "앞으로 뭘 봐야 하는지 — 다음 촉매나 리스크",
  "key_projects": "연관 핵심 프로젝트 2-3개",
  "sector_tags": ["DeFi","PerpDEX","Stablecoins","RWA","AI×Crypto","L1","L2","ZK·Privacy","Restaking","DePIN","Meme","기관·매크로","인프라"] 중 해당하는 것들,
  "narrative_signal": {{
    "narrative": "이 글이 강화/약화하는 내러티브 이름",
    "direction": "강화 또는 약화",
    "reason": "한 줄 근거"
  }}
}}
"""

# ══════════════════════════════════════════════════════
# 프롬프트 — 데일리 브리핑 (트윗 + 블로그 통합)
# ══════════════════════════════════════════════════════
DAILY_BRIEFING_PROMPT = """
당신은 크립토/DeFi 시장 시니어 애널리스트입니다.
독자는 DeFi를 깊이 이해하는 전문가입니다.

역할:
- 오늘 크립토/DeFi에서 진짜 중요한 일을 판단하고 깊이 해석합니다
- 단순 요약 절대 금지. 표면 말고 뒤에서 무슨 일이 벌어지는지까지 분석합니다
- 메커니즘(어떻게 작동하는지), 이해관계(누가 이득/손해), 영향(다음에 뭐가 바뀌는지) 반드시 포함
- 노이즈는 마지막에 한 줄로만 처리합니다
- 한국어로 작성합니다

판단 기준:
- 여러 소스가 동시에 언급 → 중요 시그널
- 프로토콜 창립자/공식 업데이트 → 높은 우선순위
- 새로운 메커니즘/이해관계 구조 포함 → 높은 우선순위
- 단순 가격 예측, 마케팅성 → 제외

링크 규칙:
- 각 이슈 하단에 실제 URL만 2~3개 붙입니다
- 없는 URL 절대 만들지 않습니다

오늘 수집된 데이터:
{raw_data}

출력 형식 (반드시 이 형식):
---
📌 크립토 데일리 브리핑 | {{날짜}}

🔥 오늘의 핵심 이슈

① [이슈 제목]
배경: [왜 지금 이 이슈가 나왔는지]
내용: [구체적으로 무슨 일인지]
메커니즘: [실제로 어떻게 작동하는지]
이해관계: [누가 이득이고 누가 손해인지]
영향: [다음에 어떤 일이 생기는지]
🔍 더 보기: [URL]

(중요한 이슈 전부, 개수 제한 없음)

🧭 앞으로 뭘 봐야 하나
- [다음 관전 포인트]
- [확인해야 할 촉매/리스크]
- [과거 유사 사례 있으면 언제, 어떤 결과였는지]

⚖️ 규제 레이더 (규제 이슈 있을 때만)
• [어느 기관/국가, 무슨 움직임, 단기/장기 영향]

⚡ 빠르게 체크
• [알아두면 좋은 것 5개 이내]

🚫 오늘 무시해도 될 것
• [노이즈 + 이유 한 줄]
---
"""

TWEET_BRIEFING_PROMPT = DAILY_BRIEFING_PROMPT  # 하위 호환성 유지

# ── Claude 분석 ───────────────────────────────────────
def analyze_blog(entry):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    portfolio = VC_PORTFOLIO.get(entry["source"], "정보 없음")
    prompt = BLOG_ANALYSIS_PROMPT.format(
        source=entry["source"],
        portfolio=portfolio,
        title=entry["title"],
        content=entry["content"],
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def generate_daily_briefing(all_tweets, blog_analyses):
    """트윗 + 블로그 분석 결과를 통합해서 데일리 브리핑 생성"""
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    today = datetime.now().strftime("%Y.%m.%d")
    url_list = []

    raw_data = f"=== 블로그/아티클 분석 ({len(blog_analyses)}개) ===\n"
    for entry, analysis in blog_analyses:
        if analysis.get("importance") == "low":
            continue
        raw_data += f"\n[{entry['source']} | {entry['title']}]\n"
        raw_data += f"배경: {analysis.get('background', '')}\n"
        raw_data += f"메커니즘: {analysis.get('mechanism', '')}\n"
        raw_data += f"이해관계: {analysis.get('interests', '')}\n"
        raw_data += f"영향: {analysis.get('impact', '')}\n"
        raw_data += f"섹터: {', '.join(analysis.get('sector_tags', []))}\n"
        if entry.get("link"):
            url_list.append(f"[{entry['source']}] {entry['link']}")

    raw_data += f"\n=== 트윗 수집 ({sum(len(a['tweets']) for a in all_tweets)}개) ===\n"
    for account_data in all_tweets:
        if not account_data["tweets"]:
            continue
        ctx = VC_PORTFOLIO.get(account_data["name"], "")
        raw_data += f"\n[@{account_data['handle']} | {ctx}]\n"
        for t in account_data["tweets"]:
            raw_data += f"  - {t['content']}\n"
            if t.get("link"):
                url_list.append(f"[@{account_data['handle']}] {t['link']}")

    if url_list:
        raw_data += "\n=== 수집된 URL (이것만 사용) ===\n"
        raw_data += "\n".join(url_list)

    if not raw_data.strip():
        return None

    prompt = DAILY_BRIEFING_PROMPT.format(raw_data=raw_data, 날짜=today)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()

def analyze_tweets(all_tweets):
    """하위 호환성 유지 — 기존 코드에서 호출하는 경우"""
    return generate_daily_briefing(all_tweets, [])

# ── 텔레그램 ──────────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        })
        time.sleep(0.5)

# ── 포맷 함수 ─────────────────────────────────────────
def format_blog_message(entry, analysis):
    emoji = "🔴" if analysis["importance"] == "high" else "🟡"
    label = "머스트리드" if analysis["importance"] == "high" else "참고용"
    sectors = ", ".join(analysis.get("sector_tags", []))
    sig = analysis.get("narrative_signal", {})
    signal_line = ""
    if sig.get("narrative"):
        arrow = "📈" if sig.get("direction") == "강화" else "📉"
        signal_line = f"\n{arrow} *내러티브 시그널*: {sig['narrative']} {sig.get('direction','')} — {sig.get('reason','')}"

    return f"""{emoji} *{entry['source']}* | {label}

*{entry['title']}*
🔗 {entry['link']}
📂 {sectors}

📌 *핵심 논지*
{analysis['summary']}

🎯 *VC 의도*
{analysis['vc_intent']}

⚡ *반대 의견*
{analysis['counter_argument']}

📚 *모르면 안 되는 개념*
{analysis['must_know']}

🔗 *더 파볼 것*
{analysis['further_reading']}

❓ *질문*
{analysis['call_questions']}{signal_line}"""

def format_tweet_briefing(result):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    msg = f"📊 *오늘의 X 브리핑 | {today}*\n\n"
    high_tweets = [t for t in result["selected_tweets"] if t["importance"] == "high"]
    medium_tweets = [t for t in result["selected_tweets"] if t["importance"] == "medium"]

    if high_tweets:
        msg += "━━━━━━━━━━━━━━━\n🔴 *주목할 것*\n━━━━━━━━━━━━━━━\n\n"
        for t in high_tweets:
            sectors = ", ".join(t.get("sector_tags", []))
            sig = t.get("narrative_signal", {})
            signal_line = ""
            if sig.get("narrative"):
                arrow = "📈" if sig.get("direction") == "강화" else "📉"
                signal_line = f"\n{arrow} *내러티브*: {sig['narrative']} {sig.get('direction','')} — {sig.get('reason','')}\n"
            msg += f"*@{t['handle']}* ({t['name']})\n"
            msg += f"📂 {sectors}\n"
            msg += f"💬 _{t['content'][:200]}_\n"
            msg += f"🔗 {t['link']}\n\n"
            msg += f"📌 {t['summary']}\n\n"
            msg += f"🎯 *왜 지금*\n{t['why_matters']}\n\n"
            msg += f"⚡ *반대 시각*\n{t['counter']}\n\n"
            msg += f"🔗 *더 파볼 것*\n{t['further_reading']}\n"
            msg += signal_line
            msg += "━━━━━━━━━━━━━━━\n"

    if medium_tweets:
        msg += "\n🟡 *참고용*\n━━━━━━━━━━━━━━━\n\n"
        for t in medium_tweets:
            msg += f"*@{t['handle']}* — {t['summary']}\n"
            msg += f"🔗 {t['link']}\n\n"
    return msg

# ── Notion 저장 ───────────────────────────────────────
NOTION_IMPORTANCE = {
    "high":   "🔴 머스트리드",
    "medium": "🟡 참고용",
    "low":    "⚪ 아카이브",
}

def to_str(val):
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val) if val else ""

def save_blog_to_notion(entry, analysis):
    notion = Client(auth=NOTION_API_KEY)
    importance = NOTION_IMPORTANCE.get(analysis["importance"], "⚪ 아카이브")
    try:
        pub_date = entry["published"][:10]
        datetime.strptime(pub_date, "%Y-%m-%d")
    except:
        pub_date = datetime.now().strftime("%Y-%m-%d")

    sig = analysis.get("narrative_signal", {})
    signal_text = ""
    if sig.get("narrative"):
        signal_text = f"내러티브: {sig['narrative']} | 방향: {sig.get('direction','')} | 근거: {sig.get('reason','')}"

    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "제목":               {"title": [{"text": {"content": entry["title"][:200]}}]},
            "출처":               {"rich_text": [{"text": {"content": to_str(entry["source"])}}]},
            "중요도":             {"select": {"name": importance}},
            "섹터":               {"multi_select": [{"name": s} for s in analysis.get("sector_tags", [])]},
            "날짜":               {"date": {"start": pub_date}},
            "핵심 논지":          {"rich_text": [{"text": {"content": (to_str(analysis.get("summary", "")) + "\n\n" + signal_text)[:2000]}}]},
            "VC 의도":            {"rich_text": [{"text": {"content": to_str(analysis.get("vc_intent", ""))[:2000]}}]},
            "맥락":               {"rich_text": [{"text": {"content": to_str(analysis.get("context", ""))[:2000]}}]},
            "반대 의견":          {"rich_text": [{"text": {"content": to_str(analysis.get("counter_argument", ""))[:2000]}}]},
            "모르면 안되는 개념": {"rich_text": [{"text": {"content": to_str(analysis.get("must_know", ""))[:2000]}}]},
            "연관 프로젝트":      {"rich_text": [{"text": {"content": to_str(analysis.get("related_projects", ""))[:2000]}}]},
            "데이터 근거":        {"rich_text": [{"text": {"content": to_str(analysis.get("data_check", ""))[:2000]}}]},
            "더 파볼 것":         {"rich_text": [{"text": {"content": to_str(analysis.get("further_reading", ""))[:2000]}}]},
            "콜 질문":            {"rich_text": [{"text": {"content": to_str(analysis.get("call_questions", ""))[:2000]}}]},
            "내 포지션":          {"rich_text": [{"text": {"content": ""}}]},
            "원문 링크":          {"url": entry["link"]},
            "처리 여부":          {"checkbox": False},
        },
    )

def save_daily_briefing_to_notion(briefing_text, date_str):
    """데일리 브리핑 텍스트를 Notion VC Intel DB에 저장"""
    notion = Client(auth=NOTION_API_KEY)
    title = f"데일리 브리핑 | {date_str}"

    # 같은 날짜 이미 있으면 갱신
    try:
        existing = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"property": "제목", "title": {"equals": title}},
            page_size=1,
        ).get("results", [])
    except Exception:
        existing = []

    props = {
        "제목":      {"title": [{"text": {"content": title}}]},
        "출처":      {"rich_text": [{"text": {"content": "데일리 브리핑"}}]},
        "중요도":    {"select": {"name": "🔴 머스트리드"}},
        "날짜":      {"date": {"start": date_str}},
        "핵심 논지": {"rich_text": [{"text": {"content": briefing_text[:1900]}}]},
        "처리 여부": {"checkbox": False},
    }
    if existing:
        notion.pages.update(page_id=existing[0]["id"], properties=props)
        print("데일리 브리핑 Notion 갱신 완료")
    else:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=props,
        )
        print("데일리 브리핑 Notion 저장 완료")

def save_tweet_briefing_to_notion(result, date_str):
    """하위 호환성 유지"""
    notion = Client(auth=NOTION_API_KEY)
    title = f"X 브리핑 | {date_str}"
    lines = []
    for t in result.get("selected_tweets", []):
        emoji = "🔴" if t.get("importance") == "high" else "🟡"
        lines.append(f"{emoji} @{t.get('handle')} ({t.get('name')})")
        lines.append(f"📂 {', '.join(t.get('sector_tags', []))}")
        lines.append(f"💬 {t.get('content', '')[:200]}")
        lines.append(f"🔗 {t.get('link', '')}")
        lines.append(f"📌 {t.get('summary', '')}")
        lines.append(f"🎯 {t.get('why_matters', '')}")
        lines.append(f"⚡ {t.get('counter', '')}")

        sig = t.get("narrative_signal", {})
        if sig.get("narrative"):
            lines.append(f"내러티브: {sig['narrative']} | 방향: {sig.get('direction','')} | 근거: {sig.get('reason','')}")

        lines.append("━━━━━━━━━━━━")
    briefing_content = "\n".join(lines)[:1900]

    # 같은 날짜 X 브리핑이 이미 있으면 갱신 (재실행 시 중복 방지)
    try:
        existing = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"property": "제목", "title": {"equals": title}},
            page_size=1,
        ).get("results", [])
    except Exception:
        existing = []

    props = {
        "제목":      {"title": [{"text": {"content": title}}]},
        "출처":      {"rich_text": [{"text": {"content": "X 브리핑"}}]},
        "중요도":    {"select": {"name": "🟡 참고용"}},
        "날짜":      {"date": {"start": date_str}},
        "핵심 논지": {"rich_text": [{"text": {"content": briefing_content}}]},
        "처리 여부": {"checkbox": False},
    }
    if existing:
        notion.pages.update(page_id=existing[0]["id"], properties=props)
        print("X 브리핑 Notion 갱신 완료 (기존 페이지)")
    else:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=props,
        )
        print("X 브리핑 Notion 저장 완료")

# ══════════════════════════════════════════════════════
# 내러티브 클러스터링 (narrative_clustering)
# ══════════════════════════════════════════════════════

CLUSTERING_PROMPT = """
당신은 크립토 내러티브 분석가입니다.

아래는 지난 7일간 VC 블로그와 X(트위터)에서 수집된 내러티브 시그널 집계입니다.
블로그/아티클 시그널은 가중치 3, 트윗 시그널은 가중치 1로 계산됐습니다.

{aggregated_data}

판단 기준:
- 가중치 합산 0~3: 노이즈 (제외)
- 4~6: Watchlist
- 7~10: 주목
- 11+: Rising (강화 우세) or Cooling (약화 우세)
- 복수 소스(블로그+트윗 혼합)일수록 신뢰도 높음

각 내러티브에 대해 JSON으로만 반환하세요. 설명 없이 순수 JSON만.

{{
  "date": "{date}",
  "narratives": [
    {{
      "narrative": "내러티브 이름",
      "status": "Rising / Cooling / Watchlist",
      "score": 가중치 합산 점수(숫자),
      "signal_count": 시그널 총 개수(숫자),
      "blog_count": 블로그 시그널 수(숫자),
      "tweet_count": 트윗 시그널 수(숫자),
      "direction": "강화 / 약화 / 혼재",
      "sources": ["출처 목록"],
      "calvin_signal": "이 내러티브가 왜 지금 강화/약화되는지 한 단락 분석. 기술·경제·시장 역학 관점.",
      "next_catalyst": "다음에 확인해야 할 촉매 또는 리스크 한 줄",
      "sector": "DeFi/PerpDEX/Stablecoins/RWA/AI×Crypto/L1/L2/ZK·Privacy/Restaking/DePIN/Meme/기관·매크로/인프라 중 하나",
      "key_projects": "이 내러티브 대표 프로젝트 2-3개"
    }}
  ],
  "week_summary": "이번 주 전체를 한 줄로 요약"
}}

score 3 이하 내러티브는 제외. score 높은 순으로 정렬.
"""

def fetch_recent_signals(days=7):
    """Notion VC Intel DB에서 지난 N일치 페이지 가져오기"""
    notion = Client(auth=NOTION_API_KEY)
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    results = []
    has_more = True
    next_cursor = None

    while has_more:
        kwargs = {
            "database_id": NOTION_DATABASE_ID,
            "filter": {
                "property": "날짜",
                "date": {"on_or_after": cutoff}
            },
            "page_size": 100,
        }
        if next_cursor:
            kwargs["start_cursor"] = next_cursor
        response = notion.databases.query(**kwargs)
        results.extend(response["results"])
        has_more = response.get("has_more", False)
        next_cursor = response.get("next_cursor")

    print(f"지난 {days}일 시그널 {len(results)}개 가져옴")
    return results

def parse_signals(pages):
    """각 페이지의 핵심 논지에서 narrative_signal 파싱 + 가중치 적용"""
    signals = []
    for page in pages:
        props = page.get("properties", {})

        # 출처 확인
        source = ""
        source_prop = props.get("출처", {})
        if source_prop.get("rich_text"):
            source = source_prop["rich_text"][0].get("plain_text", "")

        # 소스 타입 + 가중치
        if any(x in source.lower() for x in ["x 브리핑", "tweet", "트윗"]):
            weight = SOURCE_WEIGHTS["tweet"]
            source_type = "tweet"
        else:
            weight = SOURCE_WEIGHTS["blog"]
            source_type = "blog"

        # 핵심 논지에서 narrative_signal 파싱
        key_prop = props.get("핵심 논지", {})
        content = ""
        if key_prop.get("rich_text"):
            content = key_prop["rich_text"][0].get("plain_text", "")

        # "내러티브: XXX | 방향: 강화/약화 | 근거: YYY" 형식 파싱
        if "내러티브:" in content and "방향:" in content:
            try:
                narrative_part = content.split("내러티브:")[1].split("|")[0].strip()
                direction_part = content.split("방향:")[1].split("|")[0].strip()
                reason_part = content.split("근거:")[1].strip() if "근거:" in content else ""

                # 접근불가/분석불가 노이즈 제거
                NOISE_KEYWORDS = ["접근 불가", "분석 불가", "판단 불가", "확인 필요", "불가능", "알 수 없"]
                is_noise = any(kw in narrative_part for kw in NOISE_KEYWORDS)
                if narrative_part and direction_part and not is_noise:
                    signals.append({
                        "source": source,
                        "source_type": source_type,
                        "weight": weight,
                        "narrative": narrative_part,
                        "direction": direction_part,
                        "reason": reason_part,
                    })
            except Exception as e:
                print(f"시그널 파싱 오류: {e}")

    print(f"파싱된 시그널: {len(signals)}개")
    return signals

def aggregate_signals(signals):
    """내러티브별 집계 + 가중치 합산"""
    narrative_map = {}
    for sig in signals:
        name = sig["narrative"]
        if not name:
            continue
        if name not in narrative_map:
            narrative_map[name] = {
                "narrative": name,
                "total_score": 0,
                "signal_count": 0,
                "direction_counts": {"강화": 0, "약화": 0, "유지": 0},
                "sources": [],
                "reasons": [],
                "blog_count": 0,
                "tweet_count": 0,
            }
        entry = narrative_map[name]
        entry["total_score"] += sig["weight"]
        entry["signal_count"] += 1
        entry["sources"].append(sig["source"])
        entry["reasons"].append(sig["reason"])
        direction = sig["direction"]
        if direction in entry["direction_counts"]:
            entry["direction_counts"][direction] += sig["weight"]
        if sig["source_type"] == "blog":
            entry["blog_count"] += 1
        else:
            entry["tweet_count"] += 1
    return narrative_map

def claude_cluster(narrative_map):
    """Claude로 내러티브 클러스터링 판단"""
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    today = datetime.now().strftime("%Y-%m-%d")

    aggregated_text = ""
    for name, data in sorted(
        narrative_map.items(),
        key=lambda x: x[1]["total_score"],
        reverse=True
    ):
        if data["total_score"] <= 3:
            continue
        aggregated_text += f"""
내러티브: {name}
가중치 합산: {data['total_score']} (블로그 {data['blog_count']}개×3 + 트윗 {data['tweet_count']}개×1)
시그널 수: {data['signal_count']}개
방향: 강화 {data['direction_counts']['강화']} / 약화 {data['direction_counts']['약화']} / 유지 {data['direction_counts'].get('유지', 0)}
출처: {', '.join(set(data['sources']))}
근거 요약: {' | '.join(data['reasons'][:3])}
---"""

    if not aggregated_text.strip():
        print("클러스터링할 시그널 없음 (모두 노이즈)")
        return None

    prompt = CLUSTERING_PROMPT.format(
        aggregated_data=aggregated_text,
        date=today,
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception as e:
        print(f"클러스터링 JSON 파싱 실패: {e}")
        return None

def format_narrative_signal_message(result):
    """텔레그램용 내러티브 시그널 메시지"""
    if not result:
        return None
    today = result.get("date", datetime.now().strftime("%Y-%m-%d"))
    msg = f"🧭 *내러티브 시그널 | {today}*\n\n"
    msg += f"_{result.get('week_summary', '')}_\n\n"
    msg += "━━━━━━━━━━━━━━━\n"

    for n in result.get("narratives", []):
        momentum_emoji = {"Rising": "📈", "Cooling": "📉", "Watchlist": "👁"}.get(n.get("status", ""), "•")
        msg += f"{momentum_emoji} *{n['narrative']}* (점수 {n.get('score', 0)} / 시그널 {n.get('signal_count', 0)}개)\n"
        msg += f"블로그 {n.get('blog_count', 0)}개 · 트윗 {n.get('tweet_count', 0)}개 · 방향: {n.get('direction', '')}\n\n"
        msg += f"📌 *Calvin's Signal*\n{n.get('calvin_signal', '')}\n\n"
        msg += f"⏭ *다음 촉매*\n{n.get('next_catalyst', '')}\n\n"
        msg += "━━━━━━━━━━━━━━━\n"
    return msg

def find_existing_narrative(notion, name):
    """봇 자동생성 내러티브 중 같은 이름의 기존 페이지 검색"""
    try:
        res = notion.databases.query(
            database_id=NARRATIVE_DB_ID,
            filter={"and": [
                {"property": "내러티브", "title": {"equals": name[:200]}},
                {"property": "출처 타입", "select": {"equals": "봇 자동생성"}},
            ]},
            page_size=1,
        )
        results = res.get("results", [])
        return results[0]["id"] if results else None
    except Exception as e:
        print(f"기존 내러티브 검색 오류 ({name}): {e}")
        return None

def save_narrative_signal_to_notion(result):
    """Narrative Radar DB에 클러스터링 결과 저장 (upsert: 있으면 갱신, 없으면 생성)"""
    if not result or not NARRATIVE_DB_ID:
        if not NARRATIVE_DB_ID:
            print("⚠️ NARRATIVE_DATABASE_ID 미설정 — Narrative Radar DB 저장 건너뜀")
        return
    notion = Client(auth=NOTION_API_KEY)
    today = result.get("date", datetime.now().strftime("%Y-%m-%d"))

    STATUS_MAP = {
        "Rising":   "Rising",
        "Cooling":  "Cooling",
        "Watchlist":"Watchlist",
    }
    MOMENTUM_MAP = {
        "강화": "상승",
        "약화": "하락",
        "혼재": "유지",
    }

    saved = 0
    for n in result.get("narratives", []):
        try:
            status   = STATUS_MAP.get(n.get("status", ""), "Watchlist")
            momentum = MOMENTUM_MAP.get(n.get("direction", ""), "유지")
            sources_text = ", ".join(n.get("sources", []))[:2000]
            content = (
                f"[{today} 자동 클러스터링]\n"
                f"주간 요약: {result.get('week_summary', '')}\n\n"
                f"시그널: {n.get('signal_count', 0)}개 "
                f"(블로그 {n.get('blog_count', 0)} / 트윗 {n.get('tweet_count', 0)})\n"
                f"가중치 합산: {n.get('score', 0)}\n\n"
                f"Calvin Signal: {n.get('calvin_signal', '')}\n\n"
                f"다음 촉매: {n.get('next_catalyst', '')}"
            )[:1900]

            # 공통 속성 (생성/갱신 양쪽에 사용)
            props = {
                "상태":      {"select": {"name": status}},
                "강도":      {"number": min(10.0, float(n.get("score", 0)))},  # 과거 DB와 동일한 1-10 스케일로 클램프
                "모멘텀":    {"select": {"name": momentum}},
                "한줄 요약": {"rich_text": [{"text": {"content": content}}]},
                "근거 소스": {"rich_text": [{"text": {"content": sources_text}}]},
                "섹터":      {"multi_select": [{"name": n.get("sector", "기타")[:100]}]},
                "핵심 프로젝트": {"rich_text": [{"text": {"content": n.get("key_projects", "")[:500]}}]},
                # Cooling이면 종료일 기록, 아니면 진행 중(빈 값)으로 유지
                "기간 종료": {"date": {"start": today} if status == "Cooling" else None},
            }

            existing_id = find_existing_narrative(notion, n["narrative"])
            if existing_id:
                notion.pages.update(page_id=existing_id, properties=props)
                print(f"갱신: {n['narrative']} [{status}] 점수:{n.get('score', 0)}")
            else:
                props.update({
                    "내러티브":  {"title": [{"text": {"content": n["narrative"][:200]}}]},
                    "타입":      {"select": {"name": "메가"}},
                    "기간 시작": {"date": {"start": today}},
                    "출처 타입": {"select": {"name": "봇 자동생성"}},
                    "검수 완료": {"checkbox": False},
                })
                notion.pages.create(
                    parent={"database_id": NARRATIVE_DB_ID},
                    properties=props,
                )
                print(f"생성: {n['narrative']} [{status}] 점수:{n.get('score', 0)}")
            saved += 1
        except Exception as e:
            print(f"Narrative Radar 저장 오류 ({n.get('narrative', '')}): {e}")

    print(f"Narrative Radar 업데이트 완료: {saved}개")


# ══════════════════════════════════════════════════════
# 위클리 브리핑
# ══════════════════════════════════════════════════════

WEEKLY_BRIEFING_PROMPT = """
당신은 크립토/DeFi 시장 시니어 애널리스트입니다.

아래는 이번 주(7일) 수집된 브리핑과 핵심 분석 내용입니다.
이번 주 크립토/DeFi 세계 전체 흐름을 분석하세요.

{weekly_data}

출력 형식:
---
📊 크립토 위클리 브리핑 | {week}

🌊 이번 주를 관통한 핵심 테마
[이번 주 시장을 지배한 1~3개 테마 — 왜 이게 중요했는지]

🔗 테마 간 연결 구조
[각 테마가 서로 어떻게 연결되고 영향을 주는지]

📈 이번 주 주목할 섹터 변화
[어떤 섹터가 강화/약화됐는지 + 이유]

🔄 지난주 대비 달라진 것
[지난주 예측과 실제 결과 비교]

🔭 다음 주 뭘 봐야 하나
[다음 주 주요 촉매, 리스크, 관전 포인트]
---
"""

def fetch_daily_snapshots(days=7):
    """Notion에서 지난 N일 데일리 브리핑 스냅샷 가져오기"""
    notion = Client(auth=NOTION_API_KEY)
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        res = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"and": [
                {"property": "날짜", "date": {"on_or_after": cutoff}},
                {"property": "출처", "rich_text": {"contains": "데일리 브리핑"}},
            ]},
            sorts=[{"property": "날짜", "direction": "descending"}],
            page_size=days,
        )
        snapshots = []
        for page in res.get("results", []):
            p = page["properties"]
            date = p.get("날짜", {}).get("date", {}).get("start", "")
            text = ""
            rt = p.get("핵심 논지", {}).get("rich_text", [])
            if rt:
                text = rt[0].get("plain_text", "")
            if date and text:
                snapshots.append({"date": date, "text": text})
        print(f"데일리 스냅샷 {len(snapshots)}개 가져옴")
        return snapshots
    except Exception as e:
        print(f"스냅샷 가져오기 오류: {e}")
        return []

def fetch_mustread_originals(days=7):
    """Notion에서 지난 N일 머스트리드 원문 가져오기 (RAG)"""
    notion = Client(auth=NOTION_API_KEY)
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        res = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"and": [
                {"property": "날짜", "date": {"on_or_after": cutoff}},
                {"property": "중요도", "select": {"equals": "🔴 머스트리드"}},
            ]},
            sorts=[{"property": "날짜", "direction": "descending"}],
            page_size=20,
        )
        originals = []
        for page in res.get("results", []):
            p = page["properties"]
            title = p.get("제목", {}).get("title", [{}])[0].get("plain_text", "")
            text = ""
            rt = p.get("핵심 논지", {}).get("rich_text", [])
            if rt:
                text = rt[0].get("plain_text", "")
            date = p.get("날짜", {}).get("date", {}).get("start", "")
            if title and text:
                originals.append({"title": title, "date": date, "text": text})
        print(f"머스트리드 원문 {len(originals)}개 가져옴")
        return originals
    except Exception as e:
        print(f"원문 가져오기 오류: {e}")
        return []

def run_weekly_briefing():
    """위클리 브리핑 생성 — 7일 스냅샷 + 머스트리드 원문"""
    print("\n--- 위클리 브리핑 시작 ---")
    from datetime import date
    week = date.today().strftime("%Y-W%W")
    today = datetime.now().strftime("%Y-%m-%d")

    snapshots = fetch_daily_snapshots(days=7)
    originals = fetch_mustread_originals(days=7)

    if not snapshots and not originals:
        print("위클리: 데이터 없음")
        return

    weekly_data = "=== 이번 주 데일리 스냅샷 ===\n"
    for s in snapshots:
        weekly_data += f"\n[{s['date']}]\n{s['text'][:500]}\n"

    weekly_data += "\n=== 이번 주 머스트리드 원문 ===\n"
    for o in originals:
        weekly_data += f"\n[{o['date']} | {o['title']}]\n{o['text'][:800]}\n"

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    prompt = WEEKLY_BRIEFING_PROMPT.format(weekly_data=weekly_data, week=week)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )
    briefing = message.content[0].text.strip()
    send_telegram(briefing)

    # Narrative Radar DB에 위클리 스냅샷 저장
    if NARRATIVE_DB_ID:
        notion = Client(auth=NOTION_API_KEY)
        try:
            notion.pages.create(
                parent={"database_id": NARRATIVE_DB_ID},
                properties={
                    "내러티브":  {"title": [{"text": {"content": f"위클리 | {week}"}}]},
                    "한줄 요약": {"rich_text": [{"text": {"content": briefing[:2000]}}]},
                    "출처 타입": {"select": {"name": "봇 자동생성"}},
                    "기간 시작": {"date": {"start": today}},
                },
            )
            print(f"위클리 스냅샷 저장 완료: {week}")
        except Exception as e:
            print(f"위클리 저장 오류: {e}")

    print("--- 위클리 브리핑 완료 ---\n")


# ══════════════════════════════════════════════════════
# 먼슬리 브리핑
# ══════════════════════════════════════════════════════

MONTHLY_BRIEFING_PROMPT = """
당신은 크립토/DeFi 시장 시니어 애널리스트입니다.

아래는 이번 달 수집된 위클리 스냅샷과 핵심 분석입니다.
이번 달 크립토/DeFi 세계의 큰 그림을 분석하세요.

{monthly_data}

출력 형식:
---
📅 크립토 먼슬리 브리핑 | {month}

🏔 이번 달 지배한 내러티브
[이번 달 가장 강하게 자리잡은 내러티브 + 왜]

🌱 새로 뜬 것
[이번 달 새롭게 부상한 테마/섹터]

🍂 식어가는 것
[이번 달 약화된 테마/섹터 + 왜]

🔄 지난달 대비 구조적 변화
[시장 구조가 어떻게 달라졌는지]

🔭 다음 달 주목할 것
[다음 달 주요 촉매, 이벤트, 리스크]
---
"""

def fetch_weekly_snapshots(weeks=4):
    """Notion Narrative Radar DB에서 위클리 스냅샷 가져오기"""
    notion = Client(auth=NOTION_API_KEY)
    cutoff = (datetime.now() - timedelta(days=weeks*7)).strftime("%Y-%m-%d")
    try:
        res = notion.databases.query(
            database_id=NARRATIVE_DB_ID,
            filter={"and": [
                {"property": "기간 시작", "date": {"on_or_after": cutoff}},
                {"property": "내러티브", "title": {"contains": "위클리"}},
            ]},
            sorts=[{"property": "기간 시작", "direction": "descending"}],
            page_size=weeks,
        )
        snapshots = []
        for page in res.get("results", []):
            p = page["properties"]
            title = p.get("내러티브", {}).get("title", [{}])[0].get("plain_text", "")
            text = ""
            rt = p.get("한줄 요약", {}).get("rich_text", [])
            if rt:
                text = rt[0].get("plain_text", "")
            if title and text:
                snapshots.append({"title": title, "text": text})
        print(f"위클리 스냅샷 {len(snapshots)}개 가져옴")
        return snapshots
    except Exception as e:
        print(f"위클리 스냅샷 가져오기 오류: {e}")
        return []

def run_monthly_briefing():
    """먼슬리 브리핑 생성 — 4주 스냅샷 + 머스트리드 원문"""
    print("\n--- 먼슬리 브리핑 시작 ---")
    month = datetime.now().strftime("%Y-%m")
    today = datetime.now().strftime("%Y-%m-%d")

    weekly_snaps = fetch_weekly_snapshots(weeks=4)
    originals = fetch_mustread_originals(days=30)

    if not weekly_snaps and not originals:
        print("먼슬리: 데이터 없음")
        return

    monthly_data = "=== 이번 달 위클리 스냅샷 ===\n"
    for s in weekly_snaps:
        monthly_data += f"\n[{s['title']}]\n{s['text'][:600]}\n"

    monthly_data += "\n=== 이번 달 머스트리드 원문 (핵심만) ===\n"
    for o in originals[:10]:
        monthly_data += f"\n[{o['date']} | {o['title']}]\n{o['text'][:600]}\n"

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    prompt = MONTHLY_BRIEFING_PROMPT.format(monthly_data=monthly_data, month=month)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )
    briefing = message.content[0].text.strip()
    send_telegram(briefing)

    if NARRATIVE_DB_ID:
        notion = Client(auth=NOTION_API_KEY)
        try:
            notion.pages.create(
                parent={"database_id": NARRATIVE_DB_ID},
                properties={
                    "내러티브":  {"title": [{"text": {"content": f"먼슬리 | {month}"}}]},
                    "한줄 요약": {"rich_text": [{"text": {"content": briefing[:2000]}}]},
                    "출처 타입": {"select": {"name": "봇 자동생성"}},
                    "기간 시작": {"date": {"start": today}},
                },
            )
            print(f"먼슬리 스냅샷 저장 완료: {month}")
        except Exception as e:
            print(f"먼슬리 저장 오류: {e}")

    print("--- 먼슬리 브리핑 완료 ---\n")

def run_narrative_clustering():
    """내러티브 클러스터링 전체 실행"""
    print("\n--- 내러티브 클러스터링 시작 ---")
    pages   = fetch_recent_signals(days=7)
    if not pages:
        print("시그널 없음")
        return
    signals = parse_signals(pages)
    if not signals:
        print("파싱된 시그널 없음")
        return
    narrative_map = aggregate_signals(signals)
    print(f"집계된 내러티브: {len(narrative_map)}개")
    for name, data in sorted(narrative_map.items(), key=lambda x: x[1]["total_score"], reverse=True):
        print(f"  {name}: 점수 {data['total_score']} (시그널 {data['signal_count']}개)")
    cluster_result = claude_cluster(narrative_map)
    if not cluster_result:
        print("클러스터링 실패")
        return
    msg = format_narrative_signal_message(cluster_result)
    if msg:
        send_telegram(msg)
    save_narrative_signal_to_notion(cluster_result)
    print("--- 내러티브 클러스터링 완료 ---\n")

# ══════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════
def main():
    print(f"[{datetime.now()}] VC Intel Agent 시작")
    seen    = load_seen()
    today   = datetime.now().strftime("%Y-%m-%d")
    mode    = os.environ.get("AGENT_MODE", "all")

    blog_analyses = []
    tweet_result  = None

    # 1. 블로그 수집 및 분석
    if mode in ("all", "blog"):
        send_telegram("📰 *블로그 수집 중...* (약 3-5분 소요)")
        print("\n--- 블로그 수집 시작 ---")
        new_blogs = fetch_new_blogs(seen)
        print(f"새 블로그 {len(new_blogs)}개 발견")

        if new_blogs:
            send_telegram(f"🔍 새 블로그 *{len(new_blogs)}개* 발견. Claude 분석 시작...")

        for entry in new_blogs:
            try:
                print(f"분석 중: {entry['source']} — {entry['title'][:50]}")
                analysis = analyze_blog(entry)
                if analysis["importance"] in ("high", "medium"):
                    send_telegram(format_blog_message(entry, analysis))
                save_blog_to_notion(entry, analysis)
                blog_analyses.append((entry, analysis))
                print(f"완료: {entry['title'][:50]} [{analysis['importance']}]")
                time.sleep(2)
            except Exception as e:
                print(f"블로그 오류 ({entry['title'][:30]}): {e}")

        if not new_blogs:
            send_telegram("📰 새 블로그 없음")

        # 트윗/클러스터링에서 크래시 나도 재분석 방지되도록 여기서 즉시 저장
        save_seen(seen)

    # 2. 트윗 수집
    if mode in ("all", "tweets"):
        send_telegram(f"🐦 *트윗 수집 중...* ({len(X_ACCOUNTS)}개 계정)")
        print("\n--- 트윗 수집 시작 ---")
        all_tweets = []
        for account in X_ACCOUNTS:
            try:
                tweets = fetch_tweets(account)
            except Exception as e:
                print(f"트윗 수집 실패 (@{account['handle']}): {e}")
                tweets = []
            print(f"@{account['handle']}: {len(tweets)}개 트윗")
            if tweets:
                all_tweets.append({
                    "handle": account["handle"],
                    "name":   account["name"],
                    "tweets": tweets,
                })
            time.sleep(2)

        total_tweets = sum(len(a["tweets"]) for a in all_tweets)
        print(f"\n총 {total_tweets}개 트윗 수집")

        # 트윗 + 블로그 통합 데일리 브리핑
        if total_tweets > 0 or blog_analyses:
            send_telegram(f"🤖 *Claude 데일리 브리핑 생성 중...* (트윗 {total_tweets}개 + 블로그 {len(blog_analyses)}개)")
            try:
                briefing = generate_daily_briefing(all_tweets, blog_analyses)
                if briefing:
                    send_telegram(briefing)
                    save_daily_briefing_to_notion(briefing, today)
                else:
                    send_telegram("⚠️ 오늘 브리핑 생성 실패")
            except Exception as e:
                err = str(e)
                if "usage limits" in err or "credit" in err.lower():
                    send_telegram("❌ *Claude API 오류*: 크레딧 부족")
                else:
                    send_telegram(f"❌ *오류 발생*: {err[:200]}")
                print(f"데일리 브리핑 오류: {e}")
        else:
            send_telegram("🐦 오늘 새 데이터 없음")

    # 3. 내러티브 클러스터링 (데일리 실행 시)
    if mode in ("all", "daily"):
        try:
            send_telegram("🧭 *내러티브 클러스터링 중...*")
            run_narrative_clustering()
        except Exception as e:
            print(f"클러스터링 오류: {e}")

    save_seen(seen)
    send_telegram("✅ *완료!*")
    print(f"\n[{datetime.now()}] 완료")

def run_weekly():
    """위클리 브리핑 실행 (매주 월요일)"""
    print(f"[{datetime.now()}] 위클리 브리핑 시작")
    send_telegram("📊 *위클리 브리핑 생성 중...*")
    try:
        run_weekly_briefing()
        send_telegram("✅ *위클리 완료!*")
    except Exception as e:
        send_telegram(f"❌ 위클리 오류: {e}")
        print(f"위클리 오류: {e}")

def run_monthly():
    """먼슬리 브리핑 실행 (매월 1일)"""
    print(f"[{datetime.now()}] 먼슬리 브리핑 시작")
    send_telegram("📅 *먼슬리 브리핑 생성 중...*")
    try:
        run_monthly_briefing()
        send_telegram("✅ *먼슬리 완료!*")
    except Exception as e:
        send_telegram(f"❌ 먼슬리 오류: {e}")
        print(f"먼슬리 오류: {e}")


if __name__ == "__main__":
    main()
