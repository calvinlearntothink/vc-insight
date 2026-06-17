import { getNarratives, getSignalFeed, getMindshare } from '@/lib/notion'
import Timeline from '@/components/Timeline'
import SignalFeed from '@/components/SignalFeed'
import MindshareClient from '@/components/MindshareClient'

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

  const today = new Date().toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric'
  })

  const latest = feed[0]?.date ?? ''
  const todayISO = new Date().toISOString().slice(0, 10)
  const isToday = latest === todayISO
  const staleDays = latest ? Math.floor((Date.parse(todayISO) - Date.parse(latest)) / 86400000) : null

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '1.25rem 1rem' }}>

      {/* 탑바 */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        borderBottom: '0.5px solid #1e1e1e', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#1D9E75' }} />
          <span style={{ fontSize: 13, fontWeight: 500 }}>Narrative Radar</span>
          <span style={{ fontSize: 11, color: '#444', marginLeft: 2 }}>by Calvin</span>
        </div>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <a href="/daily" style={{ fontSize: 12, color: '#1D9E75', textDecoration: 'none' }}>데일리 브리핑</a>
          <a href="/timeline" style={{ fontSize: 12, color: '#444', textDecoration: 'none' }}>타임라인</a>
          <span style={{ fontSize: 11, color: '#444' }}>{today}</span>
        </div>
      </div>

      {/* 마인드쉐어 트리맵 */}
      <div style={{ marginBottom: '2rem' }}>
        <MindshareClient data7d={mindshare7d} data30d={mindshare30d} />
      </div>

      {/* 시그널 피드 */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <span style={{ fontSize: 10, color: '#444', letterSpacing: '.06em', textTransform: 'uppercase' }}>
            {isToday ? '오늘 시그널' : '최근 시그널'}
          </span>
          {!isToday && latest && (
            <span style={{ fontSize: 10, padding: '1px 7px', borderRadius: 99,
              background: '#D85A3015', color: '#D85A30', border: '0.5px solid #D85A3030' }}>
              마지막 업데이트 {latest.slice(5)} · {staleDays}일 전
            </span>
          )}
          {isToday && <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#1D9E75', display: 'inline-block' }} />}
          <a href="/daily" style={{ marginLeft: 'auto', fontSize: 11, color: '#1D9E75', textDecoration: 'none' }}>
            데일리 브리핑 전체 보기 →
          </a>
        </div>

        {/* 시그널 카드 티커 */}
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
          {feed.slice(0, 6).map(f => (
            <div key={f.id} style={{ flexShrink: 0, width: 200, padding: '10px 12px',
              border: '0.5px solid #1e1e1e', borderRadius: 8, background: '#0d0d0d' }}>
              <div style={{ fontSize: 10, color: '#444', marginBottom: 4 }}>{f.source}</div>
              <div style={{ fontSize: 12, color: '#bbb', lineHeight: 1.4,
                overflow: 'hidden', display: '-webkit-box',
                WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                {f.title || f.summary.slice(0, 60)}
              </div>
              {f.narrative && (
                <div style={{ fontSize: 10, color: '#1D9E75', marginTop: 4 }}>→ {f.narrative}</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 시그널 피드 리스트 */}
      <SignalFeed feed={feed} />

      {/* 타임라인 */}
      <div style={{ marginTop: '2.5rem' }}>
        <div style={{ fontSize: 10, color: '#444', letterSpacing: '.06em',
          textTransform: 'uppercase', marginBottom: 12 }}>
          내러티브 타임라인 · 2019 → 현재
        </div>
        <Timeline narratives={narratives} />
      </div>

    </div>
  )
}
