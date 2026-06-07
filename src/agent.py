import os
import json
import time
import re
import feedparser
import anthropic
import requests
from datetime import datetime
from notion_client import Client
import requests
from bs4 import BeautifulSoup

class SimpleFetcher:
    def get(self, url):
        import requests
        from bs4 import BeautifulSoup
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        return BeautifulSoup(r.text, "html.parser")



# ── 환경 변수 ──────────────────────────────────────────
CLAUDE_API_KEY     = os.environ["CLAUDE_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
NOTION_API_KEY     = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

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

# ── URL 필터 (공통 제외 키워드) ───────────────────────
URL_EXCLUDE_KEYWORDS = [
    "/team/", "/careers/", "/jobs/", "/about/", "/portfolio/",
    "/contact/", "/press/", "/events/", "/legal/", "/privacy/",
    "/login/", "/subscribe/", "/newsletter/", "/search/",
    "/leadership/", "/board/", "/newsroom/", "/shop/",
    "/our-team/", "/accelerator/", "/voices-onchain/", "/readwriteown/",
]

# ── X 계정 (Nitter) ───────────────────────────────────
X_ACCOUNTS = [
    # VC 공식
    {"handle": "a16zcrypto",      "name": "a16z Crypto"},
    {"handle": "paradigm",        "name": "Paradigm"},
    {"handle": "dragonfly_xyz",   "name": "Dragonfly"},
    {"handle": "PanteraCapital",  "name": "Pantera Capital"},
    {"handle": "Polychain",       "name": "Polychain"},
    {"handle": "GalaxyDigital",   "name": "Galaxy Digital"},
    {"handle": "TheSpartanGroup", "name": "Spartan Group"},
    {"handle": "HashKey_Capital", "name": "HashKey Capital"},
    {"handle": "YZiLabs",         "name": "YZi Labs"},
    # 개인 (Thesis + Contrarian)
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
    # 리서치/인플루언서
    {"handle": "Delphi_Digital",  "name": "Delphi Digital"},
    {"handle": "MessariCrypto",   "name": "Messari"},
    {"handle": "RyanSAdams",      "name": "Ryan Adams"},
    {"handle": "DefiIgnas",       "name": "DefiIgnas"},
    {"handle": "Defi_Warhol",     "name": "DeFi Warhol"},
    {"handle": "RyanWatkins_",    "name": "Ryan Watkins"},
]

# ── VC 포트폴리오 컨텍스트 ────────────────────────────
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

# ── 캘빈 관심 섹터 ────────────────────────────────────
CALVIN_SECTORS = [
    "DeFi", "Stablecoin", "RWA", "Payment", "Vault",
    "Tokenomics", "Market Making", "Backer", "Investment"
]

# ── seen 항목 관리 ────────────────────────────────────
SEEN_FILE = "seen_entries.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# ── 블로그 스크래핑 ───────────────────────────────────
def scrape_blog_links(source, fetcher):
    page = fetcher.get(source["url"])
    from urllib.parse import urlparse
    base = urlparse(source["url"])
    links = []
    seen_links = set()
    for a in page.css("a"):
        href = a.attrib.get("href", "")
        text = a.text_content().strip() if hasattr(a, 'text_content') else a.get_all_text().strip()
        if not href or not text or len(text) < 15:
            continue
        if href.startswith("/"):
            href = f"{base.scheme}://{base.netloc}{href}"
        if not href.startswith("http"):
            continue
        # URL 필터 적용
        if any(kw in href for kw in URL_EXCLUDE_KEYWORDS):
            continue
        # 소스 페이지 자체 URL 제외
        if href.rstrip("/") == source["url"].rstrip("/"):
            continue
        if href not in seen_links:
            seen_links.add(href)
            links.append({"title": text, "link": href})
    return links[:5]

def scrape_blog_content(url, fetcher):
    try:
        page = fetcher.get(url)
        return page.get_all_text()[:6000]
    except:
        return ""

def fetch_rss_links(source):
    """RSS 피드에서 최신 글 5개 가져오기"""
    feed = feedparser.parse(source["url"])
    links = []
    for entry in feed.entries[:5]:
        link = entry.get("link", "")
        title = entry.get("title", "")
        published = entry.get("published", datetime.now().strftime("%Y-%m-%d"))
        if link and title:
            links.append({"title": title, "link": link, "published": published})
    return links

def fetch_new_blogs(seen, fetcher):
    new_entries = []
    for source in BLOG_SOURCES:
        try:
            source_type = source.get("type", "scrape")
            if source_type == "rss":
                links = fetch_rss_links(source)
            else:
                links = scrape_blog_links(source, fetcher)
            print(f"{source['name']} 블로그: {len(links)}개 링크")
            for item in links:
                if item["link"] not in seen:
                    content = scrape_blog_content(item["link"], fetcher)
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

# ── X 트윗 스크래핑 ───────────────────────────────────
def is_recent(date_str):
    """24시간 이내 트윗인지 확인"""
    date_str = date_str.strip()
    if re.search(r'\d+[mh]$', date_str):  # 21h, 30m
        return True
    if date_str.lower() == 'just now':
        return True
    return False

def is_retweet(item):
    """RT 여부 확인"""
    retweet = item.css('.retweet-header')
    return len(retweet) > 0

def fetch_tweets(account, fetcher):
    """계정 트윗 수집 — 24시간 이내, 150자 이상, RT 제외"""
    tweets = []
    try:
        page = fetcher.get(f"https://nitter.net/{account['handle']}")
        items = page.css('.timeline-item')
        # 첫 번째는 핀 트윗이라 스킵
        for item in items[1:]:
            if is_retweet(item):
                continue
            date_els = item.css('.tweet-date a')
            content_els = item.css('.tweet-content')
            link_els = item.css('.tweet-link')
            if not date_els or not content_els:
                continue
            date_str = date_els[0].get_all_text().strip()
            if not is_recent(date_str):
                continue
            content = content_els[0].get_all_text().strip()
            if len(content) < 150:
                continue
            link = link_els[0].attrib.get('href', '') if link_els else ''
            if link.startswith('/'):
                link = f"https://x.com{link.replace('#m', '')}"
            tweets.append({
                "content": content,
                "link": link,
                "date": date_str,
            })
    except Exception as e:
        print(f"트윗 오류 (@{account['handle']}): {e}")
    return tweets

# ── 블로그 분석 프롬프트 ──────────────────────────────
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
  "sector_tags": ["Stablecoins","RWA","AI×Crypto","DePIN","Perps","ZK/Infra","L1·L2","기타"] 중 해당하는 것들
}}
"""

# ── 트윗 브리핑 프롬프트 ──────────────────────────────
TWEET_BRIEFING_PROMPT = """
당신은 글로벌 Crypto/Web3 시장 인텔리전스 에이전트입니다.
사용자의 목적: 나만의 시장 Thesis와 논리를 만드는 것.
관심 섹터: DeFi, Stablecoin, RWA, Payment, Vault, Tokenomics, Market Making, Backer/Investment

아래는 오늘 수집한 Crypto/Web3 주요 인물들의 트윗 모음입니다.

{tweets_data}

다음을 수행하세요:

1. 관심 섹터 관련성, 새로운 시각, 시장 신호 여부 기준으로 상위 7-10개 트윗 선별
2. 선별된 것들을 아래 JSON 형식으로 반환

중요도 기준:
- high: 관심 섹터 직접 + Contrarian 시각 + 규제/정책 변화 + VC 포지션 변화 신호 + 데이터 기반
- medium: 관심 섹터 관련 + 알아두면 좋은 배경 지식
- 제외: 섹터 무관, 홍보성, 단순 반복, RT성 내용

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
      "sector_tags": ["해당 섹터들"]
    }}
  ]
}}
"""

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
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def analyze_tweets(all_tweets):
    """전체 트윗 모아서 한 번에 분석"""
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
        max_tokens=4000,
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
            print(f"JSON 파싱 실패: {e2}. raw: {raw[:300]}")
            return {"selected_tweets": []}

# ── 텔레그램 전송 ─────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # 텔레그램 4096자 제한 처리
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        })
        time.sleep(0.5)

def format_blog_message(entry, analysis):
    emoji = "🔴" if analysis["importance"] == "high" else "🟡"
    label = "머스트리드" if analysis["importance"] == "high" else "참고용"
    sectors = ", ".join(analysis.get("sector_tags", []))
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
{analysis['call_questions']}"""

def format_tweet_briefing(result):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    msg = f"📊 *오늘의 X 브리핑 | {today}*\n\n"

    high_tweets = [t for t in result["selected_tweets"] if t["importance"] == "high"]
    medium_tweets = [t for t in result["selected_tweets"] if t["importance"] == "medium"]

    if high_tweets:
        msg += "━━━━━━━━━━━━━━━\n🔴 *주목할 것*\n━━━━━━━━━━━━━━━\n\n"
        for t in high_tweets:
            sectors = ", ".join(t.get("sector_tags", []))
            msg += f"*@{t['handle']}* ({t['name']})\n"
            msg += f"📂 {sectors}\n"
            msg += f"💬 _{t['content'][:200]}_\n"
            msg += f"🔗 {t['link']}\n\n"
            msg += f"📌 {t['summary']}\n\n"
            msg += f"🎯 *왜 지금*\n{t['why_matters']}\n\n"
            msg += f"⚡ *반대 시각*\n{t['counter']}\n\n"
            msg += f"🔗 *더 파볼 것*\n{t['further_reading']}\n\n"
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
    """리스트나 다른 타입을 string으로 변환"""
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

    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "제목":               {"title": [{"text": {"content": entry["title"][:200]}}]},
            "출처":               {"rich_text": [{"text": {"content": to_str(entry["source"])}}]},
            "중요도":             {"select": {"name": importance}},
            "섹터":               {"multi_select": [{"name": s} for s in analysis.get("sector_tags", [])]},
            "날짜":               {"date": {"start": pub_date}},
            "핵심 논지":          {"rich_text": [{"text": {"content": to_str(analysis.get("summary", ""))[:2000]}}]},
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

    # 읽기 좋은 텍스트로 변환
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
        lines.append(f"🔍 더 파볼 것: {t.get('further_reading', '')}")
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

# ── 메인 ─────────────────────────────────────────────
def main():
    print(f"[{datetime.now()}] VC Intel Agent 시작")
    seen = load_seen()
    
    today = datetime.now().strftime("%Y-%m-%d")
    mode = os.environ.get("AGENT_MODE", "all")

    # 1. 블로그 수집 및 분석
    if mode in ("all", "blog"):
        send_telegram("📰 *블로그 수집 중...* (약 3-5분 소요)")
        print("\n--- 블로그 수집 시작 ---")
        new_blogs = fetch_new_blogs(seen, fetcher)
        print(f"새 블로그 {len(new_blogs)}개 발견")

        if new_blogs:
            send_telegram(f"🔍 새 블로그 *{len(new_blogs)}개* 발견. Claude 분석 시작...")

        for i, entry in enumerate(new_blogs):
            try:
                print(f"분석 중: {entry['source']} — {entry['title'][:50]}")
                analysis = analyze_blog(entry)
                if analysis["importance"] in ("high", "medium"):
                    msg = format_blog_message(entry, analysis)
                    send_telegram(msg)
                save_blog_to_notion(entry, analysis)
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
        for i, account in enumerate(X_ACCOUNTS):
            tweets = fetch_tweets(account, fetcher)
            print(f"@{account['handle']}: {len(tweets)}개 트윗")
            if tweets:
                all_tweets.append({
                    "handle": account["handle"],
                    "name": account["name"],
                    "tweets": tweets,
                })
            time.sleep(2)

        total_tweets = sum(len(a["tweets"]) for a in all_tweets)
        print(f"\n총 {total_tweets}개 트윗 수집. 분석 시작...")

        if total_tweets > 0:
            send_telegram(f"🤖 *Claude 분석 중...* 트윗 {total_tweets}개 → 상위 7-10개 선별")
            try:
                result = analyze_tweets(all_tweets)
                if result and result.get("selected_tweets"):
                    selected = result["selected_tweets"]
                    high = [t for t in selected if t.get("importance") == "high"]
                    medium = [t for t in selected if t.get("importance") == "medium"]
                    send_telegram(f"📊 분석 완료: 총 {len(selected)}개 선별 (🔴 {len(high)}개 / 🟡 {len(medium)}개)")
                    msg = format_tweet_briefing(result)
                    if msg.strip():
                        send_telegram(msg)
                    save_tweet_briefing_to_notion(result, today)
                    print(f"브리핑 완료: {len(selected)}개 선별")
                else:
                    send_telegram("⚠️ 오늘 선별된 트윗이 없어요.")
            except Exception as e:
                err = str(e)
                if "usage limits" in err or "credit" in err.lower():
                    send_telegram("❌ *Claude API 오류*: 크레딧 부족\nconsole.anthropic.com에서 충전해주세요.")
                elif "database" in err.lower() or "notion" in err.lower():
                    send_telegram(f"❌ *Notion 저장 오류*: {err[:200]}")
                else:
                    send_telegram(f"❌ *오류 발생*: {err[:200]}")
                print(f"트윗 브리핑 오류: {e}")
        else:
            send_telegram("🐦 오늘 새 트윗 없음")

    save_seen(seen)
    send_telegram("✅ *완료!*")
    print(f"\n[{datetime.now()}] 완료")

if __name__ == "__main__":
    main()
