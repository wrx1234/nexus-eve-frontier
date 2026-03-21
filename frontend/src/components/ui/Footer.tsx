export function Footer() {
  const links = [
    { label: 'Features', href: '#features' },
    { label: 'Ecosystem', href: '#ecosystem' },
    { label: 'Bot', href: 'https://t.me/EVENexusBot' },
    { label: 'EVE Frontier', href: 'https://www.evefrontier.com/' },
    { label: 'GitHub', href: 'https://github.com/CryptoMaN-Kamel/eve-frontier-hackathon' },
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
        <p className="text-neutral-600 text-xs">EVE Frontier × Sui Hackathon 2026 · © 2026 NEXUS</p>
      </div>
    </footer>
  )
}
