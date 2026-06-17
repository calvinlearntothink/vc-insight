'use client'
import { useState } from 'react'

const SECTOR_COLORS: Record<string, string> = {
  DeFi: '#3C3489', PerpDEX: '#993C1D', Stablecoins: '#854F0B',
  RWA: '#0F6E56', 'AI×Crypto': '#534AB7', L1: '#5F5E5A',
  L2: '#185FA5', 'ZK·Privacy': '#72243E', Restaking: '#085041',
  DePIN: '#3B6D11', Meme: '#7A4A9A', '기관·매크로': '#444441', '인프라': '#2A4A5A',
}
const DEFAULT_COLOR = '#2A2A3A'

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
  const W = 660, H = 300
  const cells = squarify(data, 0, 0, W, H)
  const sel = data.find(d => d.sector === selected)

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 500, color: '#fff' }}>마인드쉐어</div>
          <div style={{ fontSize: 11, color: '#444', marginTop: 2 }}>VC 시그널 기반 섹터별 attention 분포</div>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {(['7d', '30d'] as const).map(t => (
            <button key={t} onClick={() => onTimeframeChange(t)}
              style={{ fontSize: 11, padding: '3px 10px', borderRadius: 99,
                border: '0.5px solid ' + (timeframe === t ? '#fff' : '#333'),
                color: timeframe === t ? '#000' : '#555',
                background: timeframe === t ? '#fff' : 'transparent', cursor: 'pointer' }}>
              {t === '7d' ? '7일' : '30일'}
            </button>
          ))}
        </div>
      </div>

      {data.length === 0 ? (
        <div style={{ height: H, display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: '0.5px solid #1a1a1a', borderRadius: 8, color: '#333', fontSize: 12 }}>
          데이터 수집 중입니다 · 매일 09:00 KST 업데이트
        </div>
      ) : (
        <div style={{ position: 'relative', width: '100%', height: H,
          border: '0.5px solid #1a1a1a', borderRadius: 8, overflow: 'hidden' }}>
          {cells.map((c, i) => {
            const color = SECTOR_COLORS[c.sector] ?? DEFAULT_COLOR
            const isSel = selected === c.sector
            const show = c.w > 60 && c.h > 40
            return (
              <div key={i} onClick={() => setSelected(isSel ? null : c.sector)}
                title={`${c.sector} · ${c.pct}% · ${c.status}`}
                style={{ position: 'absolute', left: c.x, top: c.y, width: c.w, height: c.h,
                  background: color + '22', border: '0.5px solid ' + color + (isSel ? '' : '44'),
                  outline: isSel ? `2px solid ${color}` : 'none',
                  cursor: 'pointer', overflow: 'hidden', transition: 'opacity .15s',
                  opacity: selected && !isSel ? 0.3 : 1 }}>
                {show && <>
                  <div style={{ position: 'absolute', bottom: 18, left: 8, right: 4,
                    fontSize: Math.min(12, c.w / 8), fontWeight: 500, color,
                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {c.sector}
                  </div>
                  <div style={{ position: 'absolute', bottom: 5, left: 8,
                    fontSize: 10, color: color + 'aa' }}>
                    {c.pct}%
                  </div>
                </>}
              </div>
            )
          })}
        </div>
      )}

      {/* 상세 패널 */}
      {sel && (
        <div style={{ marginTop: 10, padding: 14, border: '0.5px solid ' + (SECTOR_COLORS[sel.sector] ?? '#333') + '66',
          borderRadius: 8, background: (SECTOR_COLORS[sel.sector] ?? '#222') + '0A' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 10 }}>
            <span style={{ fontSize: 15, fontWeight: 500, color: '#fff' }}>{sel.sector}</span>
            <span style={{ fontSize: 12, color: '#555' }}>{sel.pct}% 마인드쉐어</span>
            <span style={{ fontSize: 11, padding: '1px 7px', borderRadius: 99,
              background: sel.status === 'Rising' ? '#1D9E7520' : sel.status === 'Cooling' ? '#D85A3020' : '#33333340',
              color: sel.status === 'Rising' ? '#1D9E75' : sel.status === 'Cooling' ? '#D85A30' : '#666',
              border: '0.5px solid ' + (sel.status === 'Rising' ? '#1D9E7550' : sel.status === 'Cooling' ? '#D85A3050' : '#333') }}>
              {sel.status}
            </span>
            <span style={{ marginLeft: 'auto', fontSize: 11, color: '#444' }}>
              {sel.momentum === '상승' ? '↑' : sel.momentum === '하락' ? '↓' : '→'} {sel.momentum}
            </span>
          </div>
          {sel.summary && (
            <div style={{ fontSize: 12, color: '#888', lineHeight: 1.6 }}>
              {sel.summary.split('\n')[0]}
            </div>
          )}
          <a href={`/daily?sector=${encodeURIComponent(sel.sector)}`}
            style={{ display: 'inline-block', marginTop: 8, fontSize: 11, color: '#1D9E75', textDecoration: 'none' }}>
            관련 브리핑 보기 →
          </a>
        </div>
      )}

      {/* 범례 */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8,
        paddingTop: 8, borderTop: '0.5px solid #1a1a1a', fontSize: 11, color: '#444' }}>
        {cells.slice(0, 8).map(c => (
          <div key={c.sector} style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}
            onClick={() => setSelected(selected === c.sector ? null : c.sector)}>
            <div style={{ width: 7, height: 7, borderRadius: 2,
              background: SECTOR_COLORS[c.sector] ?? DEFAULT_COLOR }} />
            <span style={{ color: selected === c.sector ? '#fff' : '#444' }}>{c.sector}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
