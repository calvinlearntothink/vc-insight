import { Client } from '@notionhq/client'

const notion = new Client({ auth: process.env.NOTION_API_KEY })
const NARRATIVE_DB = process.env.NARRATIVE_DATABASE_ID!
const VC_INTEL_DB  = process.env.NOTION_DATABASE_ID!

export async function getNarratives() {
  const res = await notion.databases.query({
    database_id: NARRATIVE_DB,
    sorts: [{ property: '기간 시작', direction: 'ascending' }],
    page_size: 100,
  })
  return res.results.map((page: any) => {
    const p = page.properties
    return {
      id: page.id,
      name:       p['내러티브']?.title?.[0]?.plain_text ?? '',
      status:     p['상태']?.select?.name ?? '',
      sector:     p['섹터']?.multi_select?.map((s: any) => s.name) ?? [],
      strength:   p['강도']?.number ?? 0,
      momentum:   p['모멘텀']?.select?.name ?? '',
      type:       p['타입']?.select?.name ?? '',
      summary:    p['한줄 요약']?.rich_text?.[0]?.plain_text ?? '',
      what:       p['무슨 일이 있었나']?.rich_text?.[0]?.plain_text ?? '',
      why:        p['왜 지금인가']?.rich_text?.[0]?.plain_text ?? '',
      macro:      p['매크로 맥락']?.rich_text?.[0]?.plain_text ?? '',
      mechanism:  p['메커니즘']?.rich_text?.[0]?.plain_text ?? '',
      projects:   p['핵심 프로젝트']?.rich_text?.[0]?.plain_text ?? '',
      trigger:    p['트리거 이벤트']?.rich_text?.[0]?.plain_text ?? '',
      endSignal:  p['종료 신호']?.rich_text?.[0]?.plain_text ?? '',
      next:       p['다음 내러티브']?.rich_text?.[0]?.plain_text ?? '',
      calvinRead: p['Calvin의 Read']?.rich_text?.[0]?.plain_text ?? '',
      data:       p['데이터 수치']?.rich_text?.[0]?.plain_text ?? '',
      sources:    p['근거 소스']?.rich_text?.[0]?.plain_text ?? '',
      startDate:  p['기간 시작']?.date?.start ?? '',
      endDate:    p['기간 종료']?.date?.start ?? '',
      sourceType: p['출처 타입']?.select?.name ?? '',
    }
  })
}

export async function getSignalFeed() {
  const res = await notion.databases.query({
    database_id: VC_INTEL_DB,
    sorts: [{ property: '날짜', direction: 'descending' }],
    page_size: 20,
  })
  return res.results.map((page: any) => {
    const p = page.properties
    const keyText = p['핵심 논지']?.rich_text?.[0]?.plain_text ?? ''
    let narrative = '', direction = ''
    if (keyText.includes('내러티브:') && keyText.includes('방향:')) {
      try {
        narrative = keyText.split('내러티브:')[1].split('|')[0].trim()
        direction = keyText.split('방향:')[1].split('|')[0].trim()
      } catch {}
    }
    return {
      id: page.id,
      title:     p['제목']?.title?.[0]?.plain_text ?? '',
      source:    p['출처']?.rich_text?.[0]?.plain_text ?? '',
      date:      p['날짜']?.date?.start ?? '',
      sectors:   p['섹터']?.multi_select?.map((s: any) => s.name) ?? [],
      summary:   keyText.slice(0, 200),
      link:      p['원문 링크']?.url ?? '',
      importance:p['중요도']?.select?.name ?? '',
      narrative, direction,
    }
  })
}

export async function getSectorStrength() {
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - 7)
  const res = await notion.databases.query({
    database_id: VC_INTEL_DB,
    filter: { property: '날짜', date: { on_or_after: cutoff.toISOString().slice(0,10) } },
    page_size: 100,
  })
  const sectorCount: Record<string, number> = {}
  res.results.forEach((page: any) => {
    const sectors = page.properties['섹터']?.multi_select ?? []
    sectors.forEach((s: any) => { sectorCount[s.name] = (sectorCount[s.name] ?? 0) + 1 })
  })
  const total = res.results.length || 1
  return Object.entries(sectorCount)
    .map(([name, count]) => ({ name, count, score: Math.min(10, Math.round((count/total)*40)) }))
    .sort((a, b) => b.count - a.count)
}
