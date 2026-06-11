from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
import time
import re
import feedparser
import anthropic
import requests
from datetime import datetime, timedelta
from notion_client import Client
import datetime

# ── 환경 변수 ──────────────────────────────────────────
CLAUDE_API_KEY      = os.environ["CLAUDE_API_KEY"]
TELEGRAM_BOT_TOKEN  = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID    = os.environ["TELEGRAM_CHAT_ID"]
NOTION_API_KEY      = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID  = os.environ["NOTION_DATABASE_ID"]       # VC Intel DB
NARRATIVE_DB_ID     = os.environ.get("NARRATIVE_DATABASE_ID", "")  # Narrative Radar DB

# ── 블로그 소스 ───────────────────────────────────────
BLOG_SOURCES = [
    {"name": "a16z Crypto",       "url": "https://a16zcrypto.com/posts/",                 "type": "scrape"},
    {"name": "Paradigm",          "url": "https://www.paradigm.xyz/writing",              "type": "scrape"},
    {"name": "Multicoin Capital", "url": "https://multicoin.capital/writing/",            "type": "scrape"},
    {"name": "Pantera Capital",   "url": "https://panteracapital.com/blockchain-letter/", "type": "scrape"},
    {"name": "Galaxy Digital",    "url": "https://www.galaxy.com/insights/",              "type": "scrape"},
    {"name": "Spartan Group",     "url": "https://www.spartangroup.io/insights",          "type": "scrape"},
    {"name": "Dragonfly",         "url": "https://medium.com/feed/dragonfly-research",    "type": "rss"},
    {"name": "Arthur Hayes",      "url": "https://cryptohayes.substack.com/feed",         "type": "rss"},
    {"name": "Messari",           "url": "https://messari.io/rss/news",                   "type": "rss"},
    {"name": "The Block",         "url": "https://www.theblock.co/rss.xml",               "type": "rss"},
    {"name": "Spartan Medium",    "url": "https://medium.com/feed/the-spartan-group",     "type": "rss"},
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
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
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
                pub = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
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
BLOG_ANALYSIS_PROMPT = """
당신은 글로벌 Crypto/Web3 시장 인텔리전스 에이전트입니다.
사용자의 목적: 나만의 시장 Thesis와 논리를 만드는 것. DeFi, Stablecoin, RWA, Payment, Vault, Tokenomics, Market Making, Backer/Investment 섹터 집중.

아래 블로그 글을 분석하고 JSON으로만 반환하세요. 설명 없이 순수 JSON만.

[출처] {source}
[VC 컨텍스트] {portfolio}
[제목] {title}
[내용] {content}

중요도 판단 기준:
- high: 관심 섹터 직접 다룸 + 새로운 시각/프레임워크 + 내러티브 전환 신호 + VC thesis 직접 설명
- medium: 관심 섹터 관련이지만 현황 정리 수준 + 매크로 분석
- low: 관심 섹터 무관 + 단순 공지/채용/이벤트

반환할 JSON:
{{
  "importance": "high 또는 medium 또는 low",
  "summary": "핵심 논지 3줄 요약",
  "vc_intent": "왜 지금 이걸 썼는지, 포트폴리오 연결고리",
  "context": "관련 이전 사례와 시장 맥락",
  "must_know": "모르면 안 되는 용어/개념",
  "related_projects": "연관 프로젝트 리스트",
  "counter_argument": "이 논지의 약점과 반대 포지션",
  "data_check": "수치로 뒷받침되는 데이터 근거",
  "further_reading": "더 파볼 리포트/소스 + 왜 파봐야 하는지",
  "call_questions": "이 주제로 쓸 수 있는 질문 2-3개",
  "sector_tags": ["Stablecoins","RWA","AI×Crypto","DePIN","Perps","ZK/Infra","L1·L2","기타"] 중 해당하는 것들,
  "narrative_signal": {{
    "narrative": "이 글이 강화/약화하는 내러티브 이름",
    "direction": "강화 또는 약화",
    "reason": "한 줄 근거"
  }}
}}
"""

TWEET_BRIEFING_PROMPT = """
당신은 글로벌 Crypto/Web3 시장 인텔리전스 에이전트입니다.
사용자의 목적: 나만의 시장 Thesis와 논리를 만드는 것.
관심 섹터: DeFi, Stablecoin, RWA, Payment, Vault, Tokenomics, Market Making, Backer/Investment

아래는 오늘 수집한 Crypto/Web3 주요 인물들의 트윗 모음입니다.

{tweets_data}

다음을 수행하세요:
1. 관심 섹터 관련성, 새로운 시각, 시장 신호 여부 기준으로 상위 7-10개 트윗 선별
2. 선별된 것들을 아래 JSON 형식으로 반환

JSON만 반환. 설명 없이:
{{
  "selected_tweets": [
    {{
      "handle": "트위터 핸들",
      "name": "이름",
      "importance": "high 또는 medium",
      "content": "트윗 원문 (전체)",
      "link": "트윗 링크",
      "summary": "핵심 요약 2줄",
      "why_matters": "왜 지금 이 말을 하는가 (VC 포지션/포트폴리오 연결)",
      "counter": "반대 시각",
      "further_reading": "더 파볼 것 + 왜 파봐야 하는지",
      "sector_tags": ["해당 섹터들"],
      "narrative_signal": {{
        "narrative": "이 트윗이 강화/약화하는 내러티브 이름",
        "direction": "강화 또는 약화",
        "reason": "한 줄 근거"
      }}
    }}
  ]
}}
"""

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
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def analyze_tweets(all_tweets):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    tweets_data = ""
    for account_data in all_tweets:
        if not account_data["tweets"]:
            continue
        tweets_data += f"\n=== @{account_data['handle']} ({account_data['name']}) ===\n"
        tweets_data += f"컨텍스트: {VC_PORTFOLIO.get(account_data['name'], '정보 없음')}\n"
        for t in account_data["tweets"]:
            tweets_data += f"- [{t['date']}] {t['content']}\n  링크: {t['link']}\n"

    if not tweets_data.strip():
        return None

    prompt = TWEET_BRIEFING_PROMPT.format(tweets_data=tweets_data)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            if not raw.endswith("]}"):
                raw = raw + "]}"
            return json.loads(raw)
        except Exception as e2:
            print(f"JSON 파싱 실패: {e2}")
            return {"selected_tweets": []}

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

def save_tweet_briefing_to_notion(result, date_str):
    notion = Client(auth=NOTION_API_KEY)
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

    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "제목":      {"title": [{"text": {"content": f"X 브리핑 | {date_str}"}}]},
            "출처":      {"rich_text": [{"text": {"content": "X 브리핑"}}]},
            "중요도":    {"select": {"name": "🟡 참고용"}},
            "날짜":      {"date": {"start": date_str}},
            "핵심 논지": {"rich_text": [{"text": {"content": briefing_content}}]},
            "처리 여부": {"checkbox": False},
        },
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
      "next_catalyst": "다음에 확인해야 할 촉매 또는 리스크 한 줄"
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

                if narrative_part and direction_part:
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
        model="claude-sonnet-4-20250514",
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

def save_narrative_signal_to_notion(result):
    """Narrative Radar DB에 클러스터링 결과 저장"""
    if not result or not NARRATIVE_DB_ID:
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

            notion.pages.create(
                parent={"database_id": NARRATIVE_DB_ID},
                properties={
                    "내러티브":  {"title": [{"text": {"content": n["narrative"][:200]}}]},
                    "타입":      {"select": {"name": "메가"}},
                    "상태":      {"select": {"name": status}},
                    "강도":      {"number": float(n.get("score", 0))},
                    "모멘텀":    {"select": {"name": momentum}},
                    "기간 시작": {"date": {"start": today}},
                    "한줄 요약": {"rich_text": [{"text": {"content": content}}]},
                    "근거 소스": {"rich_text": [{"text": {"content": sources_text}}]},
                    "출처 타입": {"select": {"name": "봇 자동생성"}},
                    "검수 완료": {"checkbox": False},
                },
            )
            saved += 1
            print(f"저장: {n['narrative']} [{status}] 점수:{n.get('score', 0)}")
        except Exception as e:
            print(f"Narrative Radar 저장 오류 ({n.get('narrative', '')}): {e}")

    print(f"Narrative Radar 업데이트 완료: {saved}개")

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

    # 2. 트윗 수집
    if mode in ("all", "tweets"):
        send_telegram(f"🐦 *트윗 수집 중...* ({len(X_ACCOUNTS)}개 계정)")
        print("\n--- 트윗 수집 시작 ---")
        all_tweets = []
        for account in X_ACCOUNTS:
            tweets = fetch_tweets(account)
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

        if total_tweets > 0:
            send_telegram(f"🤖 *Claude 분석 중...* 트윗 {total_tweets}개 → 상위 7-10개 선별")
            try:
                tweet_result = analyze_tweets(all_tweets)
                if tweet_result and tweet_result.get("selected_tweets"):
                    selected = tweet_result["selected_tweets"]
                    high   = [t for t in selected if t.get("importance") == "high"]
                    medium = [t for t in selected if t.get("importance") == "medium"]
                    send_telegram(f"📊 분석 완료: {len(selected)}개 선별 (🔴 {len(high)}개 / 🟡 {len(medium)}개)")
                    msg = format_tweet_briefing(tweet_result)
                    if msg.strip():
                        send_telegram(msg)
                    save_tweet_briefing_to_notion(tweet_result, today)
                else:
                    send_telegram("⚠️ 오늘 선별된 트윗이 없어요.")
            except Exception as e:
                err = str(e)
                if "usage limits" in err or "credit" in err.lower():
                    send_telegram("❌ *Claude API 오류*: 크레딧 부족")
                else:
                    send_telegram(f"❌ *오류 발생*: {err[:200]}")
                print(f"트윗 브리핑 오류: {e}")
        else:
            send_telegram("🐦 오늘 새 트윗 없음")

    # 3. 내러티브 클러스터링 (매일 전체 실행 시에만)
    if mode == "all":
        try:
            send_telegram("🧭 *내러티브 클러스터링 중...*")
            run_narrative_clustering()
        except Exception as e:
            print(f"클러스터링 오류: {e}")

    save_seen(seen)
    send_telegram("✅ *완료!*")
    print(f"\n[{datetime.now()}] 완료")


if __name__ == "__main__":
    main()
