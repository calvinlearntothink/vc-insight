'use client'
import { useState } from 'react'

const SECTOR_COLORS: Record<string, string> = {
  'DeFi':'#1D9E75','RWA':'#0F6E56','AI×Crypto':'#185FA5',
  'L1·L2':'#534AB7','Stablecoin':'#854F0B','DePIN':'#D85A30',
  'Perps':'#1D9E75','Privacy':'#D4537E','GameFi':'#D4537E',
  'BTC Ecosystem':'#BA7517',
}
const DEFAULT_COLOR = '#5F5E5A'

const START_YEAR = 2019.5
// 현재 시점 기반 동적 계산 — 연도가 지나도 차트가 자동 확장
const NOW = new Date()
const NOW_F = NOW.getFullYear() + NOW.getMonth() / 12
const END_YEAR = NOW_F + 0.5
const RANGE    = END_YEAR - START_YEAR
const MIN_H = 14
const MAX_H = 52
const ROW_GAP = 5

function yearToDate(ys: string): number {
  if (!ys) return 0
  const d = new Date(ys)
  return d.getFullYear() + d.getMonth() / 12
}

function barH(strength: number) {
  const s = Math.max(5, Math.min(10, strength))
  // 비선형(제곱) 스케일 — 9.5 vs 7.0 차이가 눈에 보이게
  const t = (s - 5) / 5
  return MIN_H + Math.pow(t, 1.6) * (MAX_H - MIN_H)
}

interface Narrative {
  id: string
  name: string
  sector: string[]
  strength: number
  summary: string
  what: string
  why: string
  macro: string
  mechanism: string
  trigger: string
  next: string
  calvinRead: string
  projects: string
  startDate: string
  endDate: string
  status: string
}

// 행 충돌 없이 row 배치
function assignRows(narrs: Narrative[]): (Narrative & { row: number; startF: number; endF: number; ongoing: boolean })[] {
  const rows: [number, number][] = []
  return narrs
    .filter(n => n.startDate)
    .map(n => {
      const sf = yearToDate(n.startDate)
      const ongoing = !n.endDate
      const ef = ongoing ? NOW_F + 0.08 : yearToDate(n.endDate)
      let row = 0
      while (true) {
        if (!rows[row] || rows[row][1] <= sf + 0.05) {
          rows[row] = [sf, ef]
          break
        }
        row++
      }
      return { ...n, row, startF: sf, endF: ef, ongoing }
    })
}

export default function Timeline({ narratives }: { narratives: Narrative[] }) {
  const [selected, setSelected] = useState<string | null>(null)
  const [dimAll, setDimAll] = useState(false)

  const placed = assignRows(narratives)
  const maxRow = placed.reduce((m, n) => Math.max(m, n.row), 0)

  // 각 row의 top offset
  const rowTops: number[] = []
  for (let r = 0; r <= maxRow; r++) {
    const prev = r === 0 ? 0 : rowTops[r - 1]
    const prevH = r === 0 ? 0 : Math.max(...placed.filter(n => n.row === r - 1).map(n => barH(n.strength)))
    rowTops.push(prev + prevH + ROW_GAP)
  }
  const lastH = Math.max(...placed.filter(n => n.row === maxRow).map(n => barH(n.strength)), MIN_H)
  const totalH = rowTops[maxRow] + lastH

  const CURRENT_YEAR = NOW.getFullYear()
  const YEARS = Array.from({ length: CURRENT_YEAR - 2019 }, (_, i) => 2020 + i)
  const nowPct = ((NOW_F - START_YEAR) / RANGE) * 100

  const sel = selected ? placed.find(n => n.id === selected) : null

  return (
    <div>
      <div style={{ overflowX:'auto' }}>
        <div style={{ position:'relative', minWidth:660, height: 22 + 6 + totalH }}>

          {/* 연도 축 */}
          <div style={{ position:'relative', height:22, borderBottom:'0.5px solid #1e1e1e',
            marginBottom:6 }}>
            {YEARS.map(y => {
              const pct = ((y - START_YEAR) / RANGE) * 100
              const isNow = y === CURRENT_YEAR
              return (
                <div key={y} style={{ position:'absolute', left:`${pct}%`,
                  top:4, transform:'translateX(-50%)',
                  display:'flex', flexDirection:'column', alignItems:'center', gap:2 }}>
                  <div style={{ width:'0.5px', height:5, background:'var(--outline-variant)' }} />
                  <span style={{ fontSize:10, color: isNow ? 'var(--primary)' : 'var(--on-surface-variant)',
                    fontWeight: isNow ? 500 : 400, whiteSpace:'nowrap' }}>
                    {isNow ? `${y} ▶` : y}
                  </span>
                </div>
              )
            })}
            {/* Now line */}
            <div style={{ position:'absolute', left:`${nowPct}%`, top:0,
              height: 22 + 6 + totalH, width:'0.5px',
              background:'var(--primary)', opacity:.12, pointerEvents:'none' }} />
          </div>

          {/* 바 */}
          <div style={{ position:'relative', height:totalH }}>
            {placed.map(n => {
              const color = SECTOR_COLORS[n.sector?.[0]] ?? DEFAULT_COLOR
              const left  = ((n.startF - START_YEAR) / RANGE) * 100
              const width = ((n.endF - n.startF) / RANGE) * 100
              const h     = barH(n.strength)
              const top   = rowTops[n.row]
              const isSelected = selected === n.id
              const dim = dimAll && !isSelected

              return (
                <div
                  key={n.id}
                  title={`${n.name} · 강도 ${n.strength}/10 · ${n.startDate}${n.ongoing ? ' ~ 진행 중' : ` ~ ${n.endDate}`}`}
                  onClick={() => {
                    setSelected(isSelected ? null : n.id)
                    setDimAll(!isSelected)
                  }}
                  onMouseEnter={() => setDimAll(true)}
                  onMouseLeave={() => { if (!selected) setDimAll(false) }}
                  style={{
                    position:'absolute', left:`${left}%`, width:`${width}%`,
                    top, height:h, background:color, borderRadius:4,
                    cursor:'pointer', overflow:'hidden',
                    display:'flex', alignItems:'center', gap:6, padding:'0 8px',
                    opacity: dim ? 0.15 : 1,
                    filter: isSelected ? 'brightness(1.2)' : 'none',
                    transition:'opacity .15s, filter .15s',
                    border: isSelected ? `1.5px solid ${color}` : 'none',
                    boxShadow: n.ongoing ? `0 0 12px ${color}66, 0 0 3px ${color}` : 'none',
                  }}
                >
                  <span style={{ fontSize:10, fontWeight:500, color:'#ffffff',
                    whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis',
                    flex:1, minWidth:0 }}>
                    {n.name}
                  </span>
                  {width > 7 && (
                    <span style={{ fontSize:9, fontWeight:600, color:'#ffffffcc',
                      flexShrink:0, fontVariantNumeric:'tabular-nums' }}>
                      {n.strength}
                    </span>
                  )}
                </div>
              )
            })}
          </div>

        </div>
      </div>

      {/* 상세 패널 */}
      {sel && (
        <div style={{ background:'var(--surface-container)', border:'1px solid var(--outline-variant)', borderRadius:12,
          padding:'1.25rem', marginTop:'1rem' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
            <div style={{ width:8, height:8, borderRadius:'50%',
              background: SECTOR_COLORS[sel.sector?.[0]] ?? DEFAULT_COLOR }} />
            <span style={{ fontSize:15, fontWeight:500 }}>{sel.name}</span>
            <span style={{ fontSize:11, color:'var(--on-surface-variant)', marginLeft:'auto' }}>
              {sel.startDate} ~ {sel.endDate || '현재'} · strength {sel.strength}/10
            </span>
          </div>

          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:10 }}>
            {[
              { label:'무슨 일이 있었나', value: sel.what || sel.summary },
              { label:'왜 지금인가',     value: sel.why },
              { label:'매크로 맥락',     value: sel.macro },
              { label:'메커니즘',        value: sel.mechanism },
            ].map(b => b.value ? (
              <div key={b.label} style={{ background:'var(--surface-container-high)', padding:'9px 11px' }}>
                <div style={{ fontSize:10, color:'var(--on-surface-variant)', fontWeight:600,
                  letterSpacing:'.04em', textTransform:'uppercase', marginBottom:4 }}>{b.label}</div>
                <div style={{ fontSize:12, color:'#999', lineHeight:1.6 }}>{b.value}</div>
              </div>
            ) : null)}
          </div>

          {sel.calvinRead && (
            <div style={{ borderLeft:'2px solid #1D9E75', padding:'9px 12px',
              marginBottom:10, background:'var(--surface-container-high)',
              borderRadius:'0 8px 8px 0' }}>
              <div style={{ fontSize:10, color:'var(--primary)', fontWeight:600,
                letterSpacing:'.04em', textTransform:'uppercase', marginBottom:3 }}>
                Calvin's Read
              </div>
              <div style={{ fontSize:12, color:'#999', lineHeight:1.65 }}>{sel.calvinRead}</div>
            </div>
          )}

          {sel.projects && (
            <div style={{ display:'flex', flexWrap:'wrap', gap:4, marginBottom:8 }}>
              {sel.projects.split(/[,·]/).map(p => p.trim()).filter(Boolean).map(p => (
                <span key={p} style={{ fontSize:11, color:'var(--on-surface-variant)', background:'var(--surface-container-high)',
                  padding:'3px 8px', borderRadius:6, border:'0.5px solid #222' }}>{p}</span>
              ))}
            </div>
          )}

          {sel.next && (
            <div style={{ fontSize:11, color:'var(--on-surface-variant)', paddingTop:8,
              borderTop:'0.5px solid #1e1e1e' }}>
              → 다음 내러티브: {sel.next}
            </div>
          )}
        </div>
      )}

      {/* 범례 — 실제 데이터에 있는 섹터만 */}
      <div style={{ display:'flex', flexWrap:'wrap', gap:10, marginTop:8,
        paddingTop:10, borderTop:'1px solid var(--outline-variant)', fontSize:11, color:'var(--on-surface-variant)' }}>
        {Array.from(new Set(placed.map(n => n.sector?.[0]).filter(Boolean)))
          .map(name => (
          <div key={name} style={{ display:'flex', alignItems:'center', gap:5 }}>
            <div style={{ width:8, height:8, borderRadius:2,
              background: SECTOR_COLORS[name] ?? DEFAULT_COLOR }} />
            {name}
          </div>
        ))}
        <span style={{ marginLeft:'auto', fontSize:10, color:'var(--on-surface-variant)' }}>
          bar height = strength · glow = 진행 중
        </span>
      </div>
    </div>
  )
}
