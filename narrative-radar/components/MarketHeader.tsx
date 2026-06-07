'use client'

interface Props {
  risingCount: number
  coolingCount: number
  totalSignals: number
  topNarrative: string
  feed: any[]
}

export default function MarketHeader({ risingCount, coolingCount, totalSignals, topNarrative, feed }: Props) {
  const topSource = feed[0]?.source ?? ''

  return (
    <div style={{ marginBottom:'1.25rem' }}>
      <div style={{ fontSize:10, color:'#444', letterSpacing:'.06em',
        textTransform:'uppercase', marginBottom:10 }}>지금 시장</div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:8, marginBottom:10 }}>
        {[
          { label:'7일 시그널', value: totalSignals, sub:'VC 블로그 + X', color:'#1D9E75' },
          { label:'Rising 내러티브', value: risingCount, sub:'활성 상태', color:'#e8e8e8' },
          { label:'가장 많이 언급', value: topNarrative || '-', sub: topSource, color:'#0F6E56', small: true },
          { label:'Cooling', value: coolingCount, sub:'냉각 중', color:'#D85A30' },
        ].map((c, i) => (
          <div key={i} style={{ background:'#111', borderRadius:8, padding:'12px',
            border:'0.5px solid #1e1e1e' }}>
            <div style={{ fontSize:10, color:'#444', letterSpacing:'.04em',
              textTransform:'uppercase', marginBottom:6 }}>{c.label}</div>
            <div style={{ fontSize: c.small ? 13 : 20, fontWeight:500, color: c.color,
              marginBottom:3, paddingTop: c.small ? 4 : 0 }}>{c.value}</div>
            <div style={{ fontSize:11, color:'#444' }}>{c.sub}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
