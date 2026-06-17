'use client'
import { useState } from 'react'
import MindshareTreemap from './MindshareTreemap'

type Item = {
  name: string; sector: string; score: number; pct: number;
  status: string; summary: string; momentum: string;
}

export default function MindshareClient({ data7d, data30d }: { data7d: Item[]; data30d: Item[] }) {
  const [timeframe, setTimeframe] = useState<'7d' | '30d'>('7d')
  const data = timeframe === '7d' ? data7d : data30d
  return <MindshareTreemap data={data} timeframe={timeframe} onTimeframeChange={setTimeframe} />
}
