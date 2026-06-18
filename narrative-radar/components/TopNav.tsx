const NAV_ITEMS = [
  { key: 'radar', label: 'Radar', href: '/' },
  { key: 'daily', label: 'Briefing', href: '/daily' },
  { key: 'timeline', label: 'Timeline', href: '/timeline' },
]

export default function TopNav({ active }: { active: string }) {
  return (
    <header style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      height: 64, padding: '0 2rem', background: 'var(--bg)',
      borderBottom: '1px solid var(--outline-variant)',
      position: 'sticky', top: 0, zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
        <span className="headline" style={{ fontSize: 15, fontWeight: 700, color: 'var(--primary)',
          letterSpacing: '-0.02em' }}>
          Narrative Radar
        </span>
        <nav style={{ display: 'flex', gap: 24 }}>
          {NAV_ITEMS.map(item => {
            const isActive = item.key === active
            return (
              <a key={item.key} href={item.href} style={{
                fontSize: 14, height: 64, display: 'flex', alignItems: 'center',
                color: isActive ? 'var(--primary)' : 'var(--on-surface-variant)',
                fontWeight: isActive ? 700 : 400,
                borderBottom: isActive ? '2px solid var(--primary)' : '2px solid transparent',
              }}>
                {item.label}
              </a>
            )
          })}
        </nav>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', background: 'var(--surface-container-low)',
          border: '1px solid var(--outline-variant)', borderRadius: 4, padding: '6px 12px', width: 220 }}>
          <span className="data" style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>
            Search signals...
          </span>
        </div>
        <span className="data" style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>
          {new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
        </span>
      </div>
    </header>
  )
}
