'use client'
import { useState } from 'react'

const SECTOR_COLORS: Record<string, string> = {
  DeFi: '#005ab4', PerpDEX: '#964400', Stablecoins: '#7d5800',
  RWA: '#006c51', 'AI×Crypto': '#535ec6', L1: '#5f5e5a',
  L2: '#185fa5', 'ZK·Privacy': '#8b3b5a', Restaking: '#0a6e56',
  DePIN: '#5a7a1a', Meme: '#8a4a9a', '기관·매크로': '#5a5a55', '인프라': '#3a5a6a',
}
const DEFAULT_COLOR = '#717785'
const RISING = '#0873df'
const COOLING = '#ba1a1a'

type Item = {
  name: string; sector: string; score: number; pct: number;
  status: string; summary: string; momentum: string;
}

function squarify(items: Item[], x: number, y: number, w: number, h: number) {
  if (!items.length) return []
  const sorted = [...items].sort((a, b) => b.pct - a.pct)
  const total = sorted.reduce((s, d) => s + d.pct, 0)
  const cells: (Item & { x: number; y: number; w: number; h: number })[] = []

  function row(rowItems: typeof sorted, rx: number, ry: number, rw: number, rh: number, horiz: boolean) {
    const rt = rowItems.reduce((s, d) => s + d.pct, 0)
    let pos = horiz ? rx : ry
    rowItems.forEach(item => {
      const ratio = item.pct / rt
      if (horiz) { const cw = rw * ratio; cells.push({ ...item, x: pos, y: ry, w: cw, h: rh }); pos += cw }
      else { const ch = rh * ratio; cells.push({ ...item, x: rx, y: pos, w: rw, h: ch }); pos += ch }
    })
  }

  const half = total / 2
  let acc = 0, split = 0
  for (let i = 0; i < sorted.length; i++) { acc += sorted[i].pct; if (acc >= half) { split = i + 1; break } }
  const a = sorted.slice(0, split), b = sorted.slice(split)
  const horiz = w >= h
  const aRatio = a.reduce((s, d) => s + d.pct, 0) / total
  if (horiz) { row(a, x, y, w * aRatio, h, false); row(b, x + w * aRatio, y, w * (1 - aRatio), h, false) }
  else { row(a, x, y, w, h * aRatio, true); row(b, x, y + h * aRatio, w, h * (1 - aRatio), true) }
  return cells
}

export default function MindshareTreemap({ data, timeframe, onTimeframeChange }: {
  data: Item[]; timeframe: '7d' | '30d'; onTimeframeChange: (t: '7d' | '30d') => void
}) {
  const [selected, setSelected] = useState<string | null>(null)
  const W = 900, H = 340
  const cells = squarify(data, 0, 0, W, H)
  const sel = data.find(d => d.sector === selected)
  const ranked = [...data].sort((a, b) => b.score - a.score).slice(0, 6)
  const maxScore = Math.max(...data.map(d => d.score), 1)

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginBottom: 12 }}>
        <div style={{ display: 'flex', background: 'var(--surface-container)', padding: 3,
          borderRadius: 4, gap: 2 }}>
          {(['7d', '30d'] as const).map(t => (
            <button key={t} onClick={() => onTimeframeChange(t)}
              className="data"
              style={{ fontSize: 11, padding: '6px 16px', borderRadius: 2, border: 'none',
                color: timeframe === t ? 'var(--on-primary)' : 'var(--on-surface-variant)',
                background: timeframe === t ? 'var(--primary)' : 'transparent', cursor: 'pointer',
                fontWeight: 600 }}>
              {t === '7d' ? '7D' : '30D'}
            </button>
          ))}
        </div>
      </div>

      {data.length === 0 ? (
        <div style={{ height: H, display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: '1px solid var(--outline-variant)', background: 'var(--surface-container-lowest)',
          color: 'var(--on-surface-variant)', fontSize: 13 }}>
          데이터 수집 중입니다 · 매일 09:00 KST 업데이트
        </div>
      ) : (
        <div style={{ position: 'relative', width: '100%', height: H,
          border: '1px solid var(--outline-variant)', background: 'var(--surface-container-lowest)',
          overflow: 'hidden' }}>
          {cells.map((c, i) => {
            const color = SECTOR_COLORS[c.sector] ?? DEFAULT_COLOR
            const isSel = selected === c.sector
            const show = c.w > 70 && c.h > 50
            const isRising = c.status === 'Rising'
            const isCooling = c.status === 'Cooling'
            return (
              <div key={i} onClick={() => setSelected(isSel ? null : c.sector)}
                title={`${c.sector} · ${c.pct}% · ${c.status}`}
                className="treemap-cell"
                style={{ position: 'absolute', left: c.x, top: c.y, width: c.w, height: c.h,
                  background: color + '14',
                  borderRight: '1px solid var(--outline-variant)',
                  borderBottom: '1px solid var(--outline-variant)',
                  outline: isSel ? `2px solid ${color}` : 'none',
                  cursor: 'pointer', overflow: 'hidden', padding: 14,
                  opacity: selected && !isSel ? 0.4 : 1 }}>
                {show && <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span className="headline" style={{ fontSize: Math.min(15, c.w / 13), fontWeight: 700,
                      color, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {c.sector}
                    </span>
                    {(isRising || isCooling) && (
                      <span className="data" style={{ fontSize: 11, fontWeight: 600,
                        color: isRising ? RISING : COOLING }}>
                        {isRising ? '+' : '-'}{c.pct}%
                      </span>
                    )}
                  </div>
                  <div style={{ position: 'absolute', bottom: 12, left: 14 }}>
                    <div className="data" style={{ fontSize: 9, color: 'var(--on-surface-variant)',
                      opacity: 0.7, textTransform: 'uppercase', letterSpacing: '.04em' }}>
                      MINDSHARE
                    </div>
                    <div className="headline" style={{ fontSize: Math.min(22, c.w / 9), fontWeight: 700,
                      color: 'var(--on-surface)' }}>
                      {c.pct}%
                    </div>
                  </div>
                </>}
              </div>
            )
          })}
        </div>
      )}

      {sel && (
        <div style={{ marginTop: 14, padding: 18, border: '1px solid var(--outline-variant)',
          borderLeft: `3px solid ${SECTOR_COLORS[sel.sector] ?? DEFAULT_COLOR}`,
          background: 'var(--surface-container)' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 10 }}>
            <span className="headline" style={{ fontSize: 16, fontWeight: 700, color: 'var(--on-surface)' }}>
              {sel.sector}
            </span>
            <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>{sel.pct}% 마인드쉐어</span>
            <span className="data" style={{ fontSize: 10, padding: '2px 8px', borderRadius: 2,
              background: sel.status === 'Rising' ? '#0873df18' : sel.status === 'Cooling' ? '#ba1a1a18' : 'var(--surface-container-high)',
              color: sel.status === 'Rising' ? RISING : sel.status === 'Cooling' ? COOLING : 'var(--on-surface-variant)',
              border: `1px solid ${sel.status === 'Rising' ? RISING : sel.status === 'Cooling' ? COOLING : 'var(--outline-variant)'}`,
              textTransform: 'uppercase', letterSpacing: '.04em' }}>
              {sel.status}
            </span>
            <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--on-surface-variant)' }}>
              {sel.momentum === '상승' ? '↑' : sel.momentum === '하락' ? '↓' : '→'} {sel.momentum}
            </span>
          </div>
          {sel.summary && (
            <div style={{ fontSize: 13, color: 'var(--on-surface)', lineHeight: 1.7 }}>
              {sel.summary.split('\n')[0]}
            </div>
          )}
          <a href={`/daily?sector=${encodeURIComponent(sel.sector)}`}
            style={{ display: 'inline-block', marginTop: 10, fontSize: 12, color: 'var(--primary)', fontWeight: 600 }}>
            관련 브리핑 보기 →
          </a>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 20 }}>
        <div style={{ border: '1px solid var(--outline-variant)', background: 'var(--surface-container)' }}>
          <div className="hairline-b" style={{ padding: '12px 16px', display: 'flex',
            justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="data" style={{ fontSize: 10, color: 'var(--on-surface-variant)',
              textTransform: 'uppercase', letterSpacing: '.08em', fontWeight: 600 }}>
              Mindshare Ranked List
            </span>
          </div>
          <div>
            {ranked.map((r, i) => (
              <div key={r.sector} style={{ padding: '12px 16px', display: 'flex', alignItems: 'center',
                gap: 12, borderBottom: i < ranked.length - 1 ? '1px solid var(--outline-variant)' : 'none' }}>
                <span className="data" style={{ width: 24, fontSize: 12, color: 'var(--on-surface-variant)' }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span style={{ flex: 1, fontSize: 13, color: 'var(--on-surface)' }}>{r.sector}</span>
                <span className="data" style={{ fontSize: 13, fontWeight: 600,
                  color: r.status === 'Rising' ? RISING : r.status === 'Cooling' ? COOLING : 'var(--on-surface)' }}>
                  {r.score.toFixed(1)}
                </span>
                <span style={{ fontSize: 13,
                  color: r.status === 'Rising' ? RISING : r.status === 'Cooling' ? COOLING : 'var(--on-surface-variant)' }}>
                  {r.status === 'Rising' ? '↗' : r.status === 'Cooling' ? '↘' : '→'}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ border: '1px solid var(--outline-variant)', background: 'var(--surface-container)' }}>
          <div className="hairline-b" style={{ padding: '12px 16px', display: 'flex',
            justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="data" style={{ fontSize: 10, color: 'var(--on-surface-variant)',
              textTransform: 'uppercase', letterSpacing: '.08em', fontWeight: 600 }}>
              Signal Strength Intensity
            </span>
            <span className="data" style={{ fontSize: 9, color: 'var(--on-surface-variant)', opacity: 0.6 }}>
              {timeframe === '7d' ? 'VOL: 7D' : 'VOL: 30D'}
            </span>
          </div>
          <div style={{ padding: '18px 16px', display: 'flex', flexDirection: 'column', gap: 16 }}>
            {ranked.slice(0, 4).map(r => (
              <div key={r.sector}>
                <div className="data" style={{ display: 'flex', justifyContent: 'space-between',
                  fontSize: 11, color: 'var(--on-surface-variant)', marginBottom: 5 }}>
                  <span>{r.sector.toUpperCase()}</span>
                  <span>{Math.round((r.score / maxScore) * 100)}%</span>
                </div>
                <div style={{ height: 6, background: 'var(--surface-container-highest)' }}>
                  <div style={{ height: '100%', width: `${Math.round((r.score / maxScore) * 100)}%`,
                    background: r.status === 'Rising' ? RISING : r.status === 'Cooling' ? COOLING : 'var(--outline)' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
