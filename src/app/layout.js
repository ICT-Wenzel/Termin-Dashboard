import './globals.css'

export const metadata = {
  title: 'Nachhilfe Dashboard',
  description: 'Dashboard zur Verwaltung von Nachhilfe-Terminen',
}

export default function RootLayout({ children }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  )
}