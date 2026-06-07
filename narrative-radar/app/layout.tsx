import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Narrative Radar',
  description: '크립토 내러티브를 가장 빠르게 파악하는 곳',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
