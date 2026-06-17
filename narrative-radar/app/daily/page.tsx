import { getDailyBriefings, getDailyBriefingContent } from '@/lib/notion'
import SideNav from '@/components/SideNav'
import TopNav from '@/components/TopNav'

export const revalidate = 3600

const TAG_COLORS: Record<string, string> = {
  '배경': 'var(--text-muted)',
  '내용': 'var(--text-muted)',
  '메커니즘': 'var(--accent)',
  '이해관계': '#D4A300',
  '영향': '#7B9EFF',
}

function renderBriefing(text: string) {
  if (!text) return null
  const lines = text.split('\n')
  const elements: React.ReactNode[] = []
  let key = 0
  let issueNum = 0

  for (const line of lines) {
    if (!line.trim()) { elements.push(<div key={key++} style={{ height: 10 }} />); continue }

    if (line.startsWith('## ')) {
      elements.push(
        <div key={key++} className="data" style={{ fontSize: 10, color: 'var(--text-faint)',
          letterSpacing: '.12em', textTransform: 'uppercase', marginTop: 32, marginBottom: 12 }}>
          {line.replace('## ', '').replace(/[🔥📡⚖️⚡🚫🧭]/g, '').trim()}
        </div>
      )
    } else if (line.startsWith('### ')) {
      issueNum++
      const title = line.replace(/^###\s+[①②③④⑤⑥⑦⑧⑨⑩]\s*/, '').trim()
      elements.push(
        <div key={key++} style={{ display: 'flex', alignItems: 'baseline', gap: 14,
          marginTop: 28, marginBottom: 14 }}>
          <span className="data" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)',
            opacity: 0.6 }}>
            {String(issueNum).padStart(2, '0')}
          </span>
          <span className="headline" style={{ fontSize: 16, fontWeight: 600, color: '#fff',
            lineHeight: 1.4 }}>
            {title}
          </span>
        </div>
      )
    } else if (/^\*\*(배경|내용|메커니즘|이해관계|영향):\*\*/.test(line)) {
      const tag = line.match(/\*\*(.+?):\*\*/)?.[1] ?? ''
      const rest = line.replace(/\*\*(.+?):\*\*/, '').trim()
      elements.push(
        <div key={key++} style={{ marginTop: 10 }}>
          <div className="data" style={{ fontSize: 10, fontWeight: 600, color: TAG_COLORS[tag] ?? 'var(--text-muted)',
            textTransform: 'uppercase', letterSpacing: '.1em', marginBottom: 4 }}>
            {tag}
          </div>
          <div style={{ fontSize: 13.5, color: '#cfcfcf', lineHeight: 1.75 }}>
            {rest}
          </div>
        </div>
      )
    } else if (line.startsWith('- **이득:**') || line.startsWith('- **손해:**')) {
      const isGain = line.includes('이득')
      const content = line.replace(/- \*\*(이득|손해):\*\*/, '').trim()
      elements.push(
        <div key={key++} style={{ display: 'flex', gap: 8, marginTop: 6, paddingLeft: 4 }}>
          <span className="data" style={{ color: isGain ? 'var(--accent)' : 'var(--warn)',
            fontSize: 11, fontWeight: 600, minWidth: 30 }}>
            {isGain ? '▲ UP' : '▼ DN'}
          </span>
          <span style={{ fontSize: 12.5, color: '#999', lineHeight: 1.6 }}>{content}</span>
        </div>
      )
    } else if (line.startsWith('- ')) {
      elements.push(
        <div key={key++} style={{ fontSize: 12.5, color: '#888', lineHeight: 1.7,
          paddingLeft: 4, marginTop: 3 }}>
          <span style={{ color: 'var(--text-faint)' }}>· </span>{line.slice(2)}
        </div>
      )
    } else if (line.startsWith('🔍')) {
      // skip
    } else if (line.startsWith('- https://') || line.startsWith('https://')) {
      const url = line.replace('- ', '').trim()
      const handle = url.match(/nitter\.net\/([^/]+)\//)?.[1]
      if (handle) {
        elements.push(
          <a key={key++} href={url.replace('nitter.net', 'twitter.com').replace('#m', '')}
            target="_blank" rel="noopener noreferrer" className="data"
            style={{ display: 'inline-block', fontSize: 11, color: 'var(--accent)',
              marginRight: 10, marginTop: 4, opacity: 0.8 }}>
            @{handle} ↗
          </a>
        )
      }
    } else if (line.startsWith('---')) {
      elements.push(<div key={key++} className="hairline-t" style={{ margin: '20px 0' }} />)
    } else if (line.trim()) {
      elements.push(
        <div key={key++} style={{ fontSize: 13, color: '#888', lineHeight: 1.7, marginTop: 6 }}>
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
    if (briefings[0]) latestContent = await getDailyBriefingContent(briefings[0].id)
  } catch (e) {
    console.error('브리핑 fetch 실패:', e)
  }

  const latest = briefings[0]

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <SideNav active="daily" />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopNav active="daily" />

        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

          <aside className="hairline" style={{
            width: 200, flexShrink: 0, borderRight: '1px solid var(--hairline)',
            borderTop: 'none', borderBottom: 'none', borderLeft: 'none',
            overflowY: 'auto', background: 'var(--bg-card)',
          }}>
            <div className="data hairline-b" style={{ padding: '14px 18px', fontSize: 10,
              color: 'var(--text-faint)', letterSpacing: '.1em', textTransform: 'uppercase' }}>
              Date Archive
            </div>
            <div style={{ padding: '6px' }}>
              {briefings.map((b, i) => (
                <a key={b.id} href={`/daily/${b.id}`} style={{
                  display: 'block', padding: '10px 12px', borderRadius: 2,
                  background: i === 0 ? 'var(--accent-dim)' : 'transparent',
                  borderRight: i === 0 ? '2px solid var(--accent)' : '2px solid transparent',
                }}>
                  <div className="data" style={{ fontSize: 11,
                    color: i === 0 ? 'var(--accent)' : 'var(--text-muted)' }}>
                    {b.date || b.title.replace('데일리 브리핑 | ', '')}
                  </div>
                </a>
              ))}
            </div>
          </aside>

          <main style={{ flex: 1, overflowY: 'auto' }}>
            <div style={{ maxWidth: 760, margin: '0 auto', padding: '2.5rem 2rem 5rem' }}>
              {latest ? (
                <>
                  <div style={{ marginBottom: 36 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                      <span className="data" style={{ fontSize: 10, padding: '3px 10px', borderRadius: 2,
                        background: 'var(--accent-dim)', color: 'var(--accent)',
                        border: '1px solid var(--accent)' }}>
                        DAILY BRIEFING
                      </span>
                      <span className="data" style={{ fontSize: 11, color: 'var(--text-faint)' }}>
                        {latest.date}
                      </span>
                    </div>
                    <h1 className="headline" style={{ fontSize: 30, fontWeight: 700, color: '#fff',
                      lineHeight: 1.2 }}>
                      오늘의 시장 종합
                    </h1>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 10, maxWidth: 540 }}>
                      VC 블로그, 프로토콜 공식, 핵심 인물 시그널 기반 — 메커니즘과 이해관계 중심 분석
                    </p>
                  </div>

                  {latestContent
                    ? renderBriefing(latestContent)
                    : <div style={{ fontSize: 13, color: 'var(--text-faint)' }}>본문을 불러오는 중...</div>
                  }
                </>
              ) : (
                <div style={{ fontSize: 13, color: 'var(--text-faint)', padding: '4rem 0' }}>
                  브리핑 데이터를 준비 중입니다. 매일 09:00 KST 업데이트됩니다.
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
