export function Footer() {
  const links = [
    { label: 'Features', href: '#features' },
    { label: 'Social Sniper', href: '#sniper' },
    { label: 'Bot', href: 'https://t.me/SuiJarvisBot' },
    { label: 'Docs', href: 'https://docs.sui.io/' },
    { label: 'GitHub', href: 'https://github.com/wrx1234/sui-hackathon' },
  ]

  return (
    <footer className="border-t border-neutral-800/50 bg-[#09090b] py-8">
      <div className="max-w-6xl mx-auto px-4 flex flex-col items-center gap-4">
        <nav className="flex flex-wrap justify-center gap-6">
          {links.map((l) => (
            <a
              key={l.label}
              href={l.href}
              target={l.href.startsWith('http') ? '_blank' : undefined}
              rel={l.href.startsWith('http') ? 'noopener noreferrer' : undefined}
              className="text-sm text-neutral-400 hover:text-white transition"
            >
              {l.label}
            </a>
          ))}
        </nav>
        <p className="text-neutral-600 text-xs">© 2026 Sui DeFi Jarvis</p>
      </div>
    </footer>
  )
}
