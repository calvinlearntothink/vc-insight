'use client'

const SECTOR_COLORS: Record<string, string> = {
  'DeFi':         '#1D9E75',
  'RWA':          '#0F6E56',
  'AI×Crypto':    '#185FA5',
  'L1·L2':        '#534AB7',
  'Stablecoin':   '#854F0B',
  'DePIN':        '#D85A30',
  'Perps':        '#1D9E75',
  'Privacy':      '#D4537E',
  'GameFi':       '#D4537E',
  'BTC Ecosystem':'#BA7517',
}

interface Props {
  sectors: { name: string; count: number; score: number }[]
}

export default function SectorBar({ sectors }: Props) {
  if (!sectors.length) return null

  return (
    <div style={{ marginBottom:'1.5rem' }}>
      <div style={{ fontSize:10, color:'#444', letterSpacing:'.06em',
        textTransform:'uppercase', marginBottom:8 }}>섹터별 7일 시그널 강도</div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:6 }}>
        {sectors.slice(0, 8).map(s => {
          const color = SECTOR_COLORS[s.name] ?? '#888'
          return (
            <div key={s.name} style={{ background:'#111', borderRadius:8,
              padding:'10px 12px', border:'0.5px solid #1e1e1e' }}>
              <div style={{ display:'flex', justifyContent:'space-between',
                alignItems:'center', marginBottom:6 }}>
                <span style={{ fontSize:11, fontWeight:500, color }}>{s.name}</span>
                <span style={{ fontSize:11, color:'#555' }}>{s.count}건</span>
              </div>
              <div style={{ height:3, background:'#1a1a1a', borderRadius:2, overflow:'hidden' }}>
                <div style={{ width:`${s.score * 10}%`, height:'100%',
                  background:color, borderRadius:2 }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
