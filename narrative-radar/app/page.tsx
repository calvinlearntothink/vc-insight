import { getNarratives, getSignalFeed, getMindshare } from '@/lib/notion'
import Timeline from '@/components/Timeline'
import SignalFeed from '@/components/SignalFeed'
import MindshareClient from '@/components/MindshareClient'
import SideNav from '@/components/SideNav'
import TopNav from '@/components/TopNav'

export const revalidate = 3600

export default async function Home() {
  let narratives: Awaited<ReturnType<typeof getNarratives>> = []
  let feed: Awaited<ReturnType<typeof getSignalFeed>> = []
  let mindshare7d: Awaited<ReturnType<typeof getMindshare>> = []
  let mindshare30d: Awaited<ReturnType<typeof getMindshare>> = []

  try {
    ;[narratives, feed, mindshare7d, mindshare30d] = await Promise.all([
      getNarratives(),
      getSignalFeed(),
      getMindshare('7d'),
      getMindshare('30d'),
    ])
  } catch (e) {
    console.error('Notion fetch 실패:', e)
  }

  const latest = feed[0]?.date ?? ''
  const todayISO = new Date().toISOString().slice(0, 10)
  const isToday = latest === todayISO
  const staleDays = latest ? Math.floor((Date.parse(todayISO) - Date.parse(latest)) / 86400000) : null

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <SideNav active="radar" />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopNav active="radar" />

        <main style={{ flex: 1, overflowY: 'auto', background: 'var(--bg)' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 2rem 4rem' }}>

            {/* 헤더 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
              marginBottom: '1.5rem', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div className="data" style={{ fontSize: 11, color: 'var(--primary)',
                  letterSpacing: '.12em', textTransform: 'uppercase' }}>Market Overview</div>
                <h1 className="headline" style={{ fontSize: 28, fontWeight: 700, color: 'var(--on-surface)',
                  marginTop: 6 }}>마인드쉐어</h1>
                <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginTop: 4 }}>
                  VC 시그널 기반 섹터별 attention 분포
                </p>
              </div>
            </div>

            {/* 마인드쉐어 트리맵 */}
            <div style={{ marginBottom: '2.5rem' }}>
              <MindshareClient data7d={mindshare7d} data30d={mindshare30d} />
            </div>

            {/* 시그널 티커 */}
            <div className="hairline" style={{ background: 'var(--surface-container)', overflow: 'hidden',
              height: 40, display: 'flex', alignItems: 'center', marginBottom: '2.5rem' }}>
              <div className="signal-ticker-scroll" style={{ display: 'flex', whiteSpace: 'nowrap' }}>
                {[0, 1].map(dup => (
                  <div key={dup} style={{ display: 'flex', gap: 32, padding: '0 16px', alignItems: 'center' }}>
                    {feed.slice(0, 6).map(f => (
                      <span key={f.id + dup} className="data" style={{ fontSize: 12,
                        color: f.direction === '약화' ? 'var(--error)' : 'var(--primary)' }}>
                        {f.source} · {(f.title || f.summary).slice(0, 40)}
                        {f.narrative && <span style={{ opacity: 0.5 }}> / {f.narrative}</span>}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            </div>

            {/* 시그널 피드 헤더 */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <span className="data" style={{ fontSize: 10, color: 'var(--on-surface-variant)',
                letterSpacing: '.1em', textTransform: 'uppercase' }}>
                {isToday ? '오늘 시그널' : '최근 시그널'}
              </span>
              {!isToday && latest && (
                <span className="data" style={{ fontSize: 10, padding: '1px 8px', borderRadius: 2,
                  background: '#ba1a1a14', color: 'var(--error)', border: '1px solid var(--error)' }}>
                  마지막 업데이트 {latest.slice(5)} · {staleDays}일 전
                </span>
              )}
              {isToday && <span style={{ width: 5, height: 5, borderRadius: '50%',
                background: 'var(--primary)', display: 'inline-block' }} />}
              <a href="/daily" style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--primary)' }}>
                데일리 브리핑 전체 보기 →
              </a>
            </div>

            <SignalFeed feed={feed} />

            {/* 타임라인 */}
            <div style={{ marginTop: '3rem' }}>
              <div className="data" style={{ fontSize: 10, color: 'var(--on-surface-variant)',
                letterSpacing: '.1em', textTransform: 'uppercase', marginBottom: 14 }}>
                내러티브 타임라인 · 2019 → 현재
              </div>
              <Timeline narratives={narratives} />
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}
