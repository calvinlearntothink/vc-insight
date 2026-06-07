import { getNarratives, getSignalFeed, getSectorStrength } from '@/lib/notion'
import Timeline from '@/components/Timeline'
import SignalFeed from '@/components/SignalFeed'
import SectorBar from '@/components/SectorBar'
import MarketHeader from '@/components/MarketHeader'

export const revalidate = 3600 // 1시간마다 재빌드

export default async function Home() {
  const [narratives, feed, sectors] = await Promise.all([
    getNarratives(),
    getSignalFeed(),
    getSectorStrength(),
  ])

  const today = new Date().toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  })

  const risingCount   = narratives.filter(n => n.status === 'Rising' || n.status === 'Hot').length
  const coolingCount  = narratives.filter(n => n.status === 'Cooling').length
  const totalSignals  = feed.length

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '1.25rem 1rem' }}>

      {/* 탑바 */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between',
        borderBottom:'0.5px solid #1e1e1e', paddingBottom:'1rem', marginBottom:'1.5rem' }}>
        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          <div style={{ width:7, height:7, borderRadius:'50%', background:'#1D9E75' }} />
          <span style={{ fontSize:13, fontWeight:500 }}>Narrative Radar</span>
          <span style={{ fontSize:11, color:'#444', marginLeft:2 }}>by Calvin</span>
        </div>
        <span style={{ fontSize:11, color:'#444' }}>{today}</span>
      </div>

      {/* 시장 현황 */}
      <MarketHeader
        risingCount={risingCount}
        coolingCount={coolingCount}
        totalSignals={totalSignals}
        topNarrative={feed.find(f => f.direction === '강화')?.narrative ?? ''}
        feed={feed}
      />

      {/* 섹터별 강도 */}
      <SectorBar sectors={sectors} />

      {/* 오늘 시그널 티커 */}
      <div style={{ marginBottom:'1.5rem' }}>
        <div style={{ fontSize:10, color:'#444', letterSpacing:'.06em', textTransform:'uppercase',
          marginBottom:8 }}>오늘 시그널</div>
        <div style={{ display:'flex', gap:6, overflowX:'auto', paddingBottom:4,
          scrollbarWidth:'none' }}>
          {feed.slice(0, 8).map(f => (
            <div key={f.id} style={{ background:'#111', border:'0.5px solid #1e1e1e',
              borderRadius:8, padding:'7px 11px', whiteSpace:'nowrap', flexShrink:0,
              minWidth:160, maxWidth:200 }}>
              <div style={{ fontSize:10, color:'#444', marginBottom:2 }}>{f.source}</div>
              <div style={{ fontSize:11, color:'#ccc', overflow:'hidden',
                textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{f.title}</div>
              {f.narrative && (
                <div style={{ fontSize:10, marginTop:3,
                  color: f.direction === '강화' ? '#1D9E75' : '#D85A30' }}>
                  {f.direction === '강화' ? '↑' : '↓'} {f.narrative}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 내러티브 타임라인 */}
      <div style={{ marginBottom:'1.5rem' }}>
        <div style={{ fontSize:10, color:'#444', letterSpacing:'.06em', textTransform:'uppercase',
          marginBottom:10 }}>narrative timeline · bar height = signal strength</div>
        <Timeline narratives={narratives} />
      </div>

      {/* 시그널 피드 */}
      <div>
        <div style={{ fontSize:10, color:'#444', letterSpacing:'.06em', textTransform:'uppercase',
          marginBottom:10 }}>시그널 피드</div>
        <SignalFeed feed={feed} />
      </div>

    </div>
  )
}
