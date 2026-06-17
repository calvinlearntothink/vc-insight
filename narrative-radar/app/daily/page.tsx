import { getDailyBriefings, getDailyBriefingContent } from '@/lib/notion'

export const revalidate = 3600

const SECTOR_COLORS: Record<string, string> = {
  DeFi: '#3C3489', PerpDEX: '#993C1D', Stablecoins: '#854F0B',
  RWA: '#0F6E56', 'AI×Crypto': '#534AB7', L1: '#5F5E5A',
  L2: '#185FA5', 'ZK·Privacy': '#72243E', Restaking: '#085041',
  DePIN: '#3B6D11', Meme: '#7A4A9A', '기관·매크로': '#444441',
  '인프라': '#2A4A5A',
}

function renderBriefing(text: string) {
  if (!text) return null
  const lines = text.split('\n')
  const elements: React.ReactNode[] = []
  let key = 0

  for (const line of lines) {
    if (!line.trim()) { elements.push(<div key={key++} style={{ height: 8 }} />); continue }

    if (line.startsWith('## ')) {
      elements.push(
        <div key={key++} style={{ fontSize: 11, color: '#555', letterSpacing: '.06em',
          textTransform: 'uppercase', marginTop: 24, marginBottom: 8 }}>
          {line.replace('## ', '').replace(/[🔥📡⚖️⚡🚫🧭]/g, '').trim()}
        </div>
      )
    } else if (line.startsWith('### ')) {
      const title = line.replace(/^###\s+[①②③④⑤⑥⑦⑧⑨⑩]\s*/, '').trim()
      elements.push(
        <div key={key++} style={{ fontSize: 14, fontWeight: 600, color: '#fff',
          marginTop: 20, marginBottom: 6, lineHeight: 1.4 }}>
          {title}
        </div>
      )
    } else if (line.startsWith('**배경:**') || line.startsWith('**내용:**') ||
               line.startsWith('**메커니즘:**') || line.startsWith('**이해관계:**') ||
               line.startsWith('**영향:**')) {
      const tag = line.match(/\*\*(.+?):\*\*/)?.[1] ?? ''
      const rest = line.replace(/\*\*(.+?):\*\*/, '').trim()
      const tagColors: Record<string, string> = {
        '배경': '#555', '내용': '#666', '메커니즘': '#1D9E75',
        '이해관계': '#D85A30', '영향': '#7B61FF',
      }
      elements.push(
        <div key={key++} style={{ display: 'flex', gap: 8, marginTop: 6 }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: tagColors[tag] ?? '#555',
            minWidth: 52, paddingTop: 2, textTransform: 'uppercase', letterSpacing: '.04em' }}>
            {tag}
          </span>
          <span style={{ fontSize: 13, color: '#bbb', lineHeight: 1.6, flex: 1 }}>
            {rest}
          </span>
        </div>
      )
    } else if (line.startsWith('- **이득:**') || line.startsWith('- **손해:**')) {
      const isGain = line.includes('이득')
      const content = line.replace(/- \*\*(이득|손해):\*\*/, '').trim()
      elements.push(
        <div key={key++} style={{ display: 'flex', gap: 6, marginTop: 4, marginLeft: 60 }}>
          <span style={{ color: isGain ? '#1D9E75' : '#D85A30', fontSize: 11, paddingTop: 2 }}>
            {isGain ? '↑' : '↓'}
          </span>
          <span style={{ fontSize: 12, color: '#888', lineHeight: 1.5 }}>{content}</span>
        </div>
      )
    } else if (line.startsWith('- ')) {
      elements.push(
        <div key={key++} style={{ fontSize: 12, color: '#777', lineHeight: 1.6,
          marginLeft: 60, marginTop: 2 }}>
          · {line.slice(2)}
        </div>
      )
    } else if (line.startsWith('🔍')) {
      // URL 라인 스킵 (링크는 별도)
    } else if (line.startsWith('- https://') || line.startsWith('https://')) {
      const url = line.replace('- ', '').trim()
      const handle = url.match(/nitter\.net\/([^/]+)\//)?.[1]
      if (handle) {
        elements.push(
          <a key={key++} href={url.replace('nitter.net', 'twitter.com').replace('#m', '')}
            target="_blank" rel="noopener noreferrer"
            style={{ display: 'inline-block', fontSize: 11, color: '#1D9E75',
              marginLeft: 60, marginTop: 2, textDecoration: 'none' }}>
            @{handle} →
          </a>
        )
      }
    } else if (line.startsWith('---')) {
      elements.push(<div key={key++} style={{ borderTop: '0.5px solid #1a1a1a', margin: '12px 0' }} />)
    } else if (line.trim()) {
      elements.push(
        <div key={key++} style={{ fontSize: 13, color: '#888', lineHeight: 1.6, marginTop: 4 }}>
          {line.replace(/\*\*(.*?)\*\*/g, '$1')}
        </div>
      )
    }
  }
  return elements
}

export default async function DailyPage() {
  let briefings: Awaited<ReturnType<typeof getDailyBriefings>> = []
  let latestContent = ''

  try {
    briefings = await getDailyBriefings(14)
    if (briefings[0]) {
      latestContent = await getDailyBriefingContent(briefings[0].id)
    }
  } catch (e) {
    console.error('브리핑 fetch 실패:', e)
  }

  const latest = briefings[0]
  const archive = briefings.slice(1)

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '1.25rem 1rem' }}>

      {/* 탑바 */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        borderBottom: '0.5px solid #1e1e1e', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <a href="/" style={{ fontSize: 13, color: '#444', textDecoration: 'none' }}>← 홈</a>
          <span style={{ color: '#222' }}>|</span>
          <span style={{ fontSize: 13, fontWeight: 500, color: '#fff' }}>데일리 브리핑</span>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <a href="/daily" style={{ fontSize: 12, color: '#1D9E75', textDecoration: 'none' }}>데일리</a>
          <a href="/timeline" style={{ fontSize: 12, color: '#444', textDecoration: 'none' }}>타임라인</a>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '1.5rem', alignItems: 'start' }}>

        {/* 왼쪽: 아카이브 */}
        <div style={{ position: 'sticky', top: '1rem' }}>
          <div style={{ fontSize: 10, color: '#444', letterSpacing: '.06em',
            textTransform: 'uppercase', marginBottom: 8 }}>아카이브</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {briefings.map((b, i) => (
              <a key={b.id} href={`/daily/${b.id}`}
                style={{ fontSize: 12, color: i === 0 ? '#1D9E75' : '#555',
                  textDecoration: 'none', padding: '4px 8px', borderRadius: 4,
                  background: i === 0 ? '#1D9E7510' : 'transparent',
                  fontWeight: i === 0 ? 500 : 400 }}>
                {b.date ? b.date.slice(5) : b.title.replace('데일리 브리핑 | ', '')}
              </a>
            ))}
          </div>
        </div>

        {/* 오른쪽: 브리핑 본문 */}
        <div>
          {latest ? (
            <>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#fff', marginBottom: 4 }}>
                {latest.title}
              </div>
              <div style={{ fontSize: 11, color: '#444', marginBottom: 20 }}>
                VC 블로그 + X 시그널 기반 · 매일 09:00 KST 업데이트
              </div>
              {latestContent
                ? renderBriefing(latestContent)
                : <div style={{ fontSize: 13, color: '#555' }}>본문을 불러오는 중...</div>
              }
            </>
          ) : (
            <div style={{ fontSize: 13, color: '#555', padding: '2rem 0' }}>
              브리핑 데이터를 준비 중입니다. 매일 09:00 KST 업데이트됩니다.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
