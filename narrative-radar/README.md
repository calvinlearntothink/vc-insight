# Narrative Radar

크립토 내러티브를 가장 빠르게 파악하는 곳.

## 로컬 실행

```bash
npm install
cp .env.local.example .env.local
# .env.local 파일에 실제 값 입력
npm run dev
```

## 환경변수

| 변수 | 설명 |
|------|------|
| `NOTION_API_KEY` | Notion Integration 토큰 |
| `NOTION_DATABASE_ID` | VC Intel DB ID |
| `NARRATIVE_DATABASE_ID` | Narrative Radar DB ID (`ec2a106b-4112-4d2c-97ff-d50b67bce847`) |

## Vercel 배포

1. GitHub repo 연결
2. 환경변수 설정 (위 표 참고)
3. Deploy
