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
            <div className="data" style={{ fontSize:11, color:'var(--on-surface-variant)', paddingTop:1 }}>
              {f.date?.slice(5, 10) ?? ''}
            </div>
            <div>
              <div style={{ fontSize:11, color:'var(--on-surface-variant)', marginBottom:2, fontWeight:500 }}>
                {f.source}
              </div>
              <div style={{ fontSize:12, color:'var(--on-surface)', lineHeight:1.5 }}>
                {f.title || f.summary.slice(0, 80)}
              </div>
              {f.title && f.summary && (
                <div style={{ fontSize:11, color:'var(--on-surface-variant)', lineHeight:1.5, marginTop:3,
                  display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical',
                  overflow:'hidden' }}>
                  {f.summary}
                </div>
              )}
              {f.narrative && (
                <div style={{ fontSize:10, color:'var(--outline-variant)', marginTop:3 }}>
                  → {f.narrative}
                </div>
              )}
            </div>
            <div style={{ paddingTop:2 }}>
              {f.direction && (
                <span className="data"
                style={{
                  fontSize:10, padding:'2px 7px', borderRadius:2,
                  background: f.direction === '강화' ? '#0873df14' : '#ba1a1a14',
                  color: f.direction === '강화' ? 'var(--primary)' : 'var(--error)',
                  border: `1px solid ${f.direction === '강화' ? 'var(--primary)' : 'var(--error)'}`,
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
        <div style={{ background:'var(--surface-container)', border:'1px solid var(--outline-variant)', borderRadius:2,
          borderLeft: '3px solid var(--primary)', padding:'1.25rem', marginTop:'1rem' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
            <span style={{ fontSize:14, fontWeight:500 }}>{sel.narrative || sel.title}</span>
            <span style={{ fontSize:11, color:'var(--on-surface-variant)', marginLeft:'auto' }}>
              {sel.date} · {sel.source}
            </span>
          </div>
          <div style={{ background:'#1a1a1a', borderRadius:8, padding:'9px 11px',
            marginBottom:10 }}>
            <div style={{ fontSize:10, color:'var(--on-surface-variant)', textTransform:'uppercase',
              letterSpacing:'.04em', marginBottom:4 }}>요약</div>
            <div style={{ fontSize:12, color:'var(--on-surface-variant)', lineHeight:1.6 }}>{sel.summary}</div>
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
