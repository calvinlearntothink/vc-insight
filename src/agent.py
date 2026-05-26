import os
import json
import feedparser
import anthropic
import requests
from datetime import datetime, timezone
from notion_client import Client

# ── 환경 변수 ──────────────────────────────────────────
CLAUDE_API_KEY      = os.environ["CLAUDE_API_KEY"]
TELEGRAM_BOT_TOKEN  = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID    = os.environ["TELEGRAM_CHAT_ID"]
NOTION_API_KEY      = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID  = os.environ["NOTION_DATABASE_ID"]

# ── 모니터링 RSS 소스 ──────────────────────────────────
RSS_SOURCES = [
    {"name": "a16z Crypto",     "url": "https://a16zcrypto.com/feed/"},
    {"name": "Paradigm",        "url": "https://www.paradigm.xyz/feed.xml"},
    {"name": "Dragonfly",       "url": "https://dragonfly.xyz/feed"},
    {"name": "Multicoin",       "url": "https://multicoin.capital/feed/"},
    {"name": "Pantera Capital", "url": "https://panteracapital.com/feed/"},
    {"name": "Delphi Digital",  "url": "https://members.delphidigital.io/feed"},
    {"name": "Messari",         "url": "https://messari.io/rss/research"},
    {"name": "Galaxy Digital",  "url": "https://www.galaxy.com/insights/feed/"},
]

# ── 이미 처리한 항목 추적 (중복 방지) ──────────────────
SEEN_FILE = "seen_entries.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# ── RSS 피드 파싱 ──────────────────────────────────────
def fetch_new_entries(seen):
    new_entries = []
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:5]:  # 최신 5개만
                entry_id = entry.get("link", entry.get("id", ""))
                if entry_id and entry_id not in seen:
                    new_entries.append({
                        "source": source["name"],
                        "title": entry.get("title", "제목 없음"),
                        "link": entry_id,
                        "summary": entry.get("summary", entry.get("description", ""))[:3000],
                        "published": entry.get("published", str(datetime.now(timezone.utc))),
                    })
                    seen.add(entry_id)
        except Exception as e:
            print(f"RSS 오류 ({source['name']}): {e}")
    return new_entries

# ── Claude API 분석 ────────────────────────────────────
VC_PORTFOLIO = {
    "a16z Crypto":     "Stablecoins, Payments, RWA, Agentic Commerce. Fund 5 ($2B) 모금 중.",
    "Paradigm":        "ZK, DeFi Infra, Prediction Markets. AI+Robotics로 확장 중 ($1.5B).",
    "Dragonfly":       "Stablecoin Infra, On-chain Payments, Trading Infra. Fund 4 ($650M).",
    "Multicoin":       "Solana, DePIN, AI×Crypto. High-conviction contrarian 전략.",
    "Pantera Capital": "RWA, Stablecoins, Prediction Markets, Perps.",
    "Delphi Digital":  "리서치+VC 겸업. DeFi, L1, GameFi.",
    "Messari":         "리서치 기관. DeFi, AI, DePIN, Consumer.",
    "Galaxy Digital":  "Institutional, Trading, RWA 토큰화.",
}

ANALYSIS_PROMPT = """
당신은 글로벌 Crypto/Web3 시장을 분석하는 개인 인텔리전스 에이전트입니다.
사용자가 레짓한 시장 플레이어로 성장하기 위해 VC/리서처들의 논지를 깊게 이해하고
본인만의 Thesis와 논리를 만드는 것을 돕습니다.

아래 콘텐츠를 분석하고 JSON으로만 반환하세요. 설명이나 마크다운 없이 순수 JSON만.

[출처] {source}
[VC 포트폴리오/방향] {portfolio}
[제목] {title}
[내용] {content}

반환할 JSON 구조:
{{
  "importance": "high 또는 medium 또는 low",
  "summary": "핵심 논지 3줄 요약",
  "vc_intent": "왜 지금 이걸 썼는지, 포트폴리오 연결고리 포함",
  "context": "관련 이전 사례와 시장 맥락",
  "must_know": "모르면 안 되는 용어/개념 (콜에서 튕겨나오지 않으려면)",
  "related_projects": "연관 프로젝트 리스트",
  "counter_argument": "이 논지의 약점과 반대 포지션",
  "data_check": "수치로 뒷받침되는 데이터 근거",
  "further_reading": "더 파볼 리포트/소스 추천",
  "call_questions": "콜에서 쓸 수 있는 질문 2-3개",
  "sector_tags": ["Stablecoins", "RWA", "AI×Crypto", "DePIN", "Perps", "ZK/Infra", "L1·L2", "기타"] 중 해당하는 것들
}}
"""

def analyze_with_claude(entry):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    portfolio = VC_PORTFOLIO.get(entry["source"], "정보 없음")
    prompt = ANALYSIS_PROMPT.format(
        source=entry["source"],
        portfolio=portfolio,
        title=entry["title"],
        content=entry["summary"],
    )
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # JSON 펜스 제거
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

# ── 텔레그램 알림 ──────────────────────────────────────
IMPORTANCE_EMOJI = {"high": "🔴", "medium": "🟡", "low": "⚪"}
IMPORTANCE_LABEL = {"high": "머스트리드", "medium": "참고용", "low": "아카이브"}

def send_telegram(entry, analysis):
    emoji = IMPORTANCE_EMOJI.get(analysis["importance"], "⚪")
    label = IMPORTANCE_LABEL.get(analysis["importance"], "아카이브")
    sectors = ", ".join(analysis.get("sector_tags", []))

    msg = f"""{emoji} *{entry['source']}* | {label}

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

❓ *콜 질문*
{analysis['call_questions']}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    })

# ── Notion 저장 ────────────────────────────────────────
NOTION_IMPORTANCE = {
    "high":   "🔴 머스트리드",
    "medium": "🟡 참고용",
    "low":    "⚪ 아카이브",
}

def save_to_notion(entry, analysis):
    notion = Client(auth=NOTION_API_KEY)
    importance = NOTION_IMPORTANCE.get(analysis["importance"], "⚪ 아카이브")

    # 날짜 파싱
    try:
        pub_date = datetime.strptime(entry["published"][:10], "%Y-%m-%d").date().isoformat()
    except Exception:
        pub_date = datetime.now().date().isoformat()

    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "제목":           {"title": [{"text": {"content": entry["title"]}}]},
            "출처":           {"rich_text": [{"text": {"content": entry["source"]}}]},
            "중요도":         {"select": {"name": importance}},
            "섹터":           {"multi_select": [{"name": s} for s in analysis.get("sector_tags", [])]},
            "날짜":           {"date": {"start": pub_date}},
            "핵심 논지":      {"rich_text": [{"text": {"content": analysis["summary"]}}]},
            "VC 의도":        {"rich_text": [{"text": {"content": analysis["vc_intent"]}}]},
            "맥락":           {"rich_text": [{"text": {"content": analysis["context"]}}]},
            "반대 의견":      {"rich_text": [{"text": {"content": analysis["counter_argument"]}}]},
            "모르면 안되는 개념": {"rich_text": [{"text": {"content": analysis["must_know"]}}]},
            "연관 프로젝트":  {"rich_text": [{"text": {"content": analysis["related_projects"]}}]},
            "데이터 근거":    {"rich_text": [{"text": {"content": analysis["data_check"]}}]},
            "더 파볼 것":     {"rich_text": [{"text": {"content": analysis["further_reading"]}}]},
            "콜 질문":        {"rich_text": [{"text": {"content": analysis["call_questions"]}}]},
            "내 포지션":      {"rich_text": [{"text": {"content": ""}}]},
            "원문 링크":      {"url": entry["link"]},
            "처리 여부":      {"checkbox": False},
        },
    )

# ── 메인 실행 ──────────────────────────────────────────
def main():
    print(f"[{datetime.now()}] VC Intel Agent 시작")
    seen = load_seen()
    new_entries = fetch_new_entries(seen)
    print(f"새 항목 {len(new_entries)}개 발견")

    for entry in new_entries:
        try:
            print(f"분석 중: {entry['source']} — {entry['title']}")
            analysis = analyze_with_claude(entry)

            # 중요도 low면 Notion에만 저장, 텔레그램 스킵
            if analysis["importance"] in ("high", "medium"):
                send_telegram(entry, analysis)

            save_to_notion(entry, analysis)
            print(f"완료: {entry['title']}")
        except Exception as e:
            print(f"오류 ({entry['title']}): {e}")

    save_seen(seen)
    print(f"[{datetime.now()}] 완료. 처리: {len(new_entries)}개")

if __name__ == "__main__":
    main()
