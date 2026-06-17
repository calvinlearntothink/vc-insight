const NAV_ITEMS = [
  { key: 'radar', label: 'Radar', href: '/', icon: '◧' },
  { key: 'daily', label: 'Briefing', href: '/daily', icon: '▤' },
  { key: 'timeline', label: 'Timeline', href: '/timeline', icon: '▥' },
]

export default function SideNav({ active }: { active: string }) {
  return (
    <aside className="hairline" style={{
      display: 'none',
      flexDirection: 'column',
      width: 220,
      height: '100%',
      background: 'var(--bg-card)',
      borderRight: '1px solid var(--hairline)',
    }}>
      <style>{`
        @media (min-width: 1024px) {
          .sidenav-desktop { display: flex !important; }
        }
      `}</style>
      <div className="sidenav-desktop" style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        <div style={{ padding: '1.5rem 1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)' }} />
            <h1 className="headline" style={{ fontSize: 16, fontWeight: 700, color: 'var(--accent)' }}>
              Narrative Radar
            </h1>
          </div>
          <p className="data" style={{ fontSize: 10, color: 'var(--text-faint)', marginTop: 4 }}>
            Intelligence Unit · by Calvin
          </p>
        </div>

        <nav style={{ flex: 1, padding: '0 0.75rem', display: 'flex', flexDirection: 'column', gap: 2 }}>
          {NAV_ITEMS.map(item => {
            const isActive = item.key === active
            return (
              <a key={item.key} href={item.href} style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 14px', borderRadius: 4,
                color: isActive ? 'var(--accent)' : 'var(--text-muted)',
                background: isActive ? 'var(--accent-dim)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: 13,
                borderRight: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              }}>
                <span style={{ fontSize: 14, opacity: 0.85 }}>{item.icon}</span>
                {item.label}
              </a>
            )
          })}
        </nav>

        <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--hairline)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--accent)' }} />
            <span className="data" style={{ fontSize: 9, color: 'var(--accent)', textTransform: 'uppercase' }}>
              System Online
            </span>
          </div>
          <div className="data" style={{ fontSize: 9, color: 'var(--text-faint)' }}>
            매일 09:00 KST 업데이트
          </div>
        </div>
      </div>
    </aside>
  )
}
