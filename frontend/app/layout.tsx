import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MT5 Multi-Account Dashboard',
  description: 'Real-time MetaTrader 5 Performance Analytics & Leaderboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-zinc-950 text-zinc-100 min-h-screen">
        {children}
      </body>
    </html>
  )
}