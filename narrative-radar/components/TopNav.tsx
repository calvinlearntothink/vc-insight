const NAV_ITEMS = [
  { key: 'radar', label: 'Radar', href: '/' },
  { key: 'daily', label: 'Briefing', href: '/daily' },
  { key: 'timeline', label: 'Timeline', href: '/timeline' },
]

export default function TopNav({ active }: { active: string }) {
  return (
    <header className="hairline-b" style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      height: 56, padding: '0 1.5rem', background: 'var(--bg)',
      position: 'sticky', top: 0, zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        <span className="headline" style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent)' }}>
          Narrative Radar
        </span>
        <nav style={{ display: 'flex', gap: 20 }}>
          {NAV_ITEMS.map(item => {
            const isActive = item.key === active
            return (
              <a key={item.key} href={item.href} style={{
                fontSize: 13, height: 56, display: 'flex', alignItems: 'center',
                color: isActive ? 'var(--accent)' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 400,
                borderBottom: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              }}>
                {item.label}
              </a>
            )
          })}
        </nav>
      </div>
      <span className="data" style={{ fontSize: 11, color: 'var(--text-faint)' }}>
        {new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
      </span>
    </header>
  )
}
