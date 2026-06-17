'use client'
import { useState } from 'react'

interface Signal {
  id: string
  title: string
  source: string
  date: string
  sectors: string[]
  summary: string
  link: string
  importance: string
  narrative: string
  direction: string
}

export default function SignalFeed({ feed }: { feed: Signal[] }) {
  const [selected, setSelected] = useState<string | null>(null)
  const sel = selected ? feed.find(f => f.id === selected) : null

  return (
    <div>
      <div style={{ display:'flex', flexDirection:'column' }}>
        {feed.map(f => (
          <div
            key={f.id}
            onClick={() => setSelected(selected === f.id ? null : f.id)}
            style={{
              display:'grid', gridTemplateColumns:'52px 1fr 60px',
              gap:10, padding:'9px 0',
              borderBottom:'0.5px solid #1a1a1a',
              cursor:'pointer',
              opacity: selected && selected !== f.id ? 0.5 : 1,
              transition:'opacity .15s',
            }}
          >
            <div className="data" style={{ fontSize:11, color:'var(--text-faint)', paddingTop:1 }}>
              {f.date?.slice(5, 10) ?? ''}
            </div>
            <div>
              <div style={{ fontSize:11, color:'#666', marginBottom:2, fontWeight:500 }}>
                {f.source}
              </div>
              <div style={{ fontSize:12, color:'#bbb', lineHeight:1.5 }}>
                {f.title || f.summary.slice(0, 80)}
              </div>
              {f.title && f.summary && (
                <div style={{ fontSize:11, color:'#555', lineHeight:1.5, marginTop:3,
                  display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical',
                  overflow:'hidden' }}>
                  {f.summary}
                </div>
              )}
              {f.narrative && (
                <div style={{ fontSize:10, color:'#333', marginTop:3 }}>
                  → {f.narrative}
                </div>
              )}
            </div>
            <div style={{ paddingTop:2 }}>
              {f.direction && (
                <span className="data"
                style={{
                  fontSize:10, padding:'2px 7px', borderRadius:2,
                  background: f.direction === '강화' ? 'var(--accent-dim)' : 'var(--warn-dim)',
                  color: f.direction === '강화' ? 'var(--accent)' : 'var(--warn)',
                  border: `1px solid ${f.direction === '강화' ? 'var(--accent)' : 'var(--warn)'}`,
                  whiteSpace:'nowrap',
                }}>
                  {f.direction === '강화' ? '↑ 강화' : '↓ 약화'}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 상세 */}
      {sel && (
        <div style={{ background:'var(--bg-card)', border:'1px solid var(--hairline)', borderRadius:2,
          borderLeft: '3px solid var(--accent)', padding:'1.25rem', marginTop:'1rem' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
            <span style={{ fontSize:14, fontWeight:500 }}>{sel.narrative || sel.title}</span>
            <span style={{ fontSize:11, color:'#444', marginLeft:'auto' }}>
              {sel.date} · {sel.source}
            </span>
          </div>
          <div style={{ background:'#1a1a1a', borderRadius:8, padding:'9px 11px',
            marginBottom:10 }}>
            <div style={{ fontSize:10, color:'#444', textTransform:'uppercase',
              letterSpacing:'.04em', marginBottom:4 }}>요약</div>
            <div style={{ fontSize:12, color:'#999', lineHeight:1.6 }}>{sel.summary}</div>
          </div>
          {sel.link && (
            <a href={sel.link} target="_blank" rel="noopener noreferrer"
              style={{ fontSize:11, color:'#1D9E75' }}>
              원문 보기 →
            </a>
          )}
        </div>
      )}
    </div>
  )
}
