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
    page_size: 30,
  })
  const items = res.results.map((page: any) => {
    const p = page.properties
    const keyText = p['핵심 논지']?.rich_text?.map((t: any) => t.plain_text).join('') ?? ''
    let narrative = '', direction = ''
    if (keyText.includes('내러티브:') && keyText.includes('방향:')) {
      try {
        narrative = keyText.split('내러티브:')[1].split('|')[0].trim()
        direction = keyText.split('방향:')[1].split('|')[0].trim()
      } catch {}
    }
    // 요약에서 "내러티브: ... | 방향: ..." 시그널 라인 제거 → 순수 논지만
    const cleanSummary = keyText.split(/\n+내러티브:/)[0].trim()
    return {
      id: page.id,
      title:     p['제목']?.title?.[0]?.plain_text ?? '',
      source:    p['출처']?.rich_text?.[0]?.plain_text ?? '',
      date:      p['날짜']?.date?.start ?? '',
      sectors:   p['섹터']?.multi_select?.map((s: any) => s.name) ?? [],
      summary:   cleanSummary.slice(0, 300),
      link:      p['원문 링크']?.url ?? '',
      importance:p['중요도']?.select?.name ?? '',
      narrative, direction,
    }
  })
  // 같은 제목 중복 제거 (재실행으로 생긴 X 브리핑 중복 등) — 최신만 유지
  const seen = new Set<string>()
  return items.filter(f => {
    const key = f.title || f.id
    if (seen.has(key)) return false
    seen.add(key)
    return true
  }).slice(0, 20)
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

export async function getDailyBriefings(limit = 10) {
  const res = await notion.databases.query({
    database_id: VC_INTEL_DB,
    filter: { property: '출처', rich_text: { contains: '데일리 브리핑' } },
    sorts: [{ property: '날짜', direction: 'descending' }],
    page_size: limit,
  })
  return res.results.map((page: any) => {
    const p = page.properties
    const id = page.id
    const title = p['제목']?.title?.[0]?.plain_text ?? ''
    const date  = p['날짜']?.date?.start ?? ''
    const preview = p['핵심 논지']?.rich_text?.map((t: any) => t.plain_text).join('') ?? ''
    return { id, title, date, preview }
  })
}

export async function getDailyBriefingContent(pageId: string) {
  // 페이지 본문 블록 전체 가져오기
  const res = await notion.blocks.children.list({ block_id: pageId, page_size: 100 })
  const texts = res.results.map((block: any) => {
    const rt = block?.[block.type]?.rich_text ?? []
    return rt.map((t: any) => t.plain_text).join('')
  })
  return texts.join('\n')
}

export async function getMindshare(timeframe: '7d' | '30d' = '7d') {
  const days = timeframe === '7d' ? 7 : 30
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - days)

  // Narrative Radar DB에서 봇 자동생성 스냅샷 가져오기
  const res = await notion.databases.query({
    database_id: NARRATIVE_DB,
    filter: {
      and: [
        { property: '출처 타입', select: { equals: '봇 자동생성' } },
        { property: '기간 시작', date: { on_or_after: cutoff.toISOString().slice(0, 10) } },
      ]
    },
    sorts: [{ property: '기간 시작', direction: 'descending' }],
    page_size: 50,
  })

  // 섹터별 최신 스냅샷만 유지 (중복 제거)
  const sectorMap = new Map<string, any>()
  res.results.forEach((page: any) => {
    const p = page.properties
    const name    = p['내러티브']?.title?.[0]?.plain_text ?? ''
    const sector  = p['섹터']?.multi_select?.[0]?.name ?? name
    const score   = p['강도']?.number ?? 0
    const status  = p['상태']?.select?.name ?? 'Watchlist'
    const summary = p['한줄 요약']?.rich_text?.[0]?.plain_text ?? ''
    const momentum= p['모멘텀']?.select?.name ?? ''
    const date    = p['기간 시작']?.date?.start ?? ''
    const key     = sector || name
    if (!sectorMap.has(key) || date > sectorMap.get(key).date) {
      sectorMap.set(key, { name, sector: key, score, status, summary, momentum, date })
    }
  })

  const items = Array.from(sectorMap.values())
    .sort((a, b) => b.score - a.score)
    .slice(0, 13)

  // 전체 합산으로 마인드쉐어 % 계산
  const total = items.reduce((s, i) => s + i.score, 0) || 1
  return items.map(i => ({ ...i, pct: Math.round((i.score / total) * 100) }))
}
