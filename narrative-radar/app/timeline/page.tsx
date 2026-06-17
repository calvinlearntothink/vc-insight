import { getNarratives } from '@/lib/notion'
import Timeline from '@/components/Timeline'

export const revalidate = 3600

export default async function TimelinePage() {
  let narratives: Awaited<ReturnType<typeof getNarratives>> = []
  try { narratives = await getNarratives() } catch (e) {}

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '1.25rem 1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        borderBottom: '0.5px solid #1e1e1e', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <a href="/" style={{ fontSize: 13, color: '#444', textDecoration: 'none' }}>← 홈</a>
          <span style={{ color: '#222' }}>|</span>
          <span style={{ fontSize: 13, fontWeight: 500, color: '#fff' }}>내러티브 타임라인</span>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <a href="/daily" style={{ fontSize: 12, color: '#444', textDecoration: 'none' }}>데일리</a>
          <a href="/timeline" style={{ fontSize: 12, color: '#1D9E75', textDecoration: 'none' }}>타임라인</a>
        </div>
      </div>
      <div style={{ fontSize: 12, color: '#444', marginBottom: 16 }}>
        2019년부터 현재까지 크립토 주요 내러티브 · 바 높이 = 시그널 강도
      </div>
      <Timeline narratives={narratives} />
    </div>
  )
}
