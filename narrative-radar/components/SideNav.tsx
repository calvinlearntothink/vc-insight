const NAV_ITEMS = [
  { key: 'radar', label: 'Overview', href: '/', icon: '▦' },
  { key: 'daily', label: 'Briefing', href: '/daily', icon: '▤' },
  { key: 'timeline', label: 'Archive', href: '/timeline', icon: '▥' },
]

export default function SideNav({ active }: { active: string }) {
  return (
    <aside style={{
      display: 'none',
      flexDirection: 'column',
      width: 256,
      height: '100%',
      background: 'var(--surface-container)',
      borderRight: '1px solid var(--outline-variant)',
    }}>
      <style>{`
        @media (min-width: 1024px) {
          .sidenav-desktop { display: flex !important; }
        }
      `}</style>
      <div className="sidenav-desktop" style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        <div style={{ padding: '1.5rem' }}>
          <h1 className="headline" style={{ fontSize: 18, fontWeight: 700, color: 'var(--primary)',
            letterSpacing: '-0.02em' }}>
            Narrative Radar
          </h1>
          <p className="data" style={{ fontSize: 10, color: 'var(--on-surface-variant)',
            marginTop: 4, opacity: 0.7 }}>
            Intelligence Unit · by Calvin
          </p>
        </div>

        <nav style={{ flex: 1, padding: '0 1rem', display: 'flex', flexDirection: 'column', gap: 4, marginTop: 4 }}>
          {NAV_ITEMS.map(item => {
            const isActive = item.key === active
            return (
              <a key={item.key} href={item.href} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '12px 16px', borderRadius: 2,
                color: isActive ? 'var(--primary)' : 'var(--on-surface-variant)',
                background: isActive ? 'var(--surface-container-highest)' : 'transparent',
                fontWeight: isActive ? 700 : 400,
                fontSize: 13,
                borderRight: isActive ? '2px solid var(--primary)' : '2px solid transparent',
              }}>
                <span style={{ fontSize: 15, opacity: 0.8 }}>{item.icon}</span>
                {item.label}
              </a>
            )
          })}
        </nav>

        <div style={{ padding: '1rem' }}>
          <button style={{
            width: '100%', background: 'var(--primary)', color: 'var(--on-primary)',
            padding: '11px 16px', borderRadius: 2, border: 'none', cursor: 'pointer',
            fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em',
          }}>
            Upgrade to Pro
          </button>
          <div style={{ display: 'flex', gap: 16, marginTop: 14 }}>
            <span style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>Help</span>
            <span style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>Status</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
