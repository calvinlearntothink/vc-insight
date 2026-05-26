# VC Intel Agent

글로벌 Crypto/Web3 VC 리포트를 자동 수집·분석해서 텔레그램 알림 + Notion 저장하는 에이전트.

## 셋업

### 1. GitHub Secrets 등록
repo → Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 값 |
|-------------|-----|
| `CLAUDE_API_KEY` | Anthropic API 키 |
| `TELEGRAM_BOT_TOKEN` | BotFather에서 받은 토큰 |
| `TELEGRAM_CHAT_ID` | 텔레그램 채팅 ID (아래 참고) |
| `NOTION_API_KEY` | Notion Integration 토큰 |
| `NOTION_DATABASE_ID` | Notion DB ID (URL에서 추출) |

### 2. TELEGRAM_CHAT_ID 찾기
텔레그램에서 봇한테 아무 메시지 보내고
아래 URL 브라우저에서 열기:
```
https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getUpdates
```
결과에서 `"chat":{"id": 숫자}` 부분이 CHAT_ID

### 3. NOTION_DATABASE_ID 찾기
Notion DB URL:
```
https://www.notion.so/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...
```
`notion.so/` 뒤 32자리 문자열이 DATABASE_ID

### 4. Notion Integration 연결
Notion DB 페이지 우측 상단 `...` → `연결` → 만든 Integration 추가

## 실행 주기
매일 한국 시간 오전 9시 자동 실행.
GitHub Actions 탭에서 수동 실행도 가능.

## 파일 구조
```
vc-intel-agent/
├── .github/workflows/agent.yml   # GitHub Actions 스케줄
├── src/agent.py                  # 메인 에이전트 코드
├── requirements.txt              # 의존성
└── README.md
```
