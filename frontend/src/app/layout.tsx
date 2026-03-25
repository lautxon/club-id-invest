import type { Metadata } from 'next'
import { GeistSans, GeistMono } from 'geist/font'
import './globals.css'
import Providers from './providers'

export const metadata: Metadata = {
  title: 'Club ID Invest - Plataforma de Inversión Colectiva',
  description: 'Invertí en proyectos inmobiliarios a través de fideicomisos con co-inversión automática del Club',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={`${GeistSans.variable} ${GeistMono.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
