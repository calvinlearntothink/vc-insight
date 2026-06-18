import { getNarratives } from '@/lib/notion'
import Timeline from '@/components/Timeline'
import SideNav from '@/components/SideNav'
import TopNav from '@/components/TopNav'

export const revalidate = 3600

export default async function TimelinePage() {
  let narratives: Awaited<ReturnType<typeof getNarratives>> = []
  try { narratives = await getNarratives() } catch (e) {}

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <SideNav active="timeline" />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopNav active="timeline" />

        <main style={{ flex: 1, overflowY: 'auto', background: 'var(--bg)' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2.5rem 2rem 5rem' }}>
            <div className="data" style={{ fontSize: 11, color: 'var(--primary)',
              letterSpacing: '.12em', textTransform: 'uppercase' }}>Historical Record</div>
            <h1 className="headline" style={{ fontSize: 28, fontWeight: 700, color: 'var(--on-surface)', marginTop: 6 }}>
              내러티브 타임라인
            </h1>
            <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginTop: 6, marginBottom: 32 }}>
              2019년부터 현재까지 크립토 주요 내러티브 · 바 높이 = 시그널 강도
            </p>
            <Timeline narratives={narratives} />
          </div>
        </main>
      </div>
    </div>
  )
}
