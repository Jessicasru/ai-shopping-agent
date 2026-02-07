import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: 'Home' },
  { to: '/upload', label: 'Upload' },
  { to: '/profile', label: 'Profile' },
  { to: '/matches', label: 'Matches' },
];

export default function Nav() {
  const { pathname } = useLocation();

  return (
    <nav className="border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]">
      <div className="mx-auto max-w-6xl px-6 flex items-center justify-between h-16">
        <Link to="/" className="font-serif text-lg tracking-tight text-[hsl(var(--foreground))]">
          Style agent
        </Link>
        <div className="flex gap-1">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`px-3 py-1.5 rounded-full text-xs tracking-[0.08em] uppercase transition-colors ${
                pathname === to
                  ? 'bg-[hsl(var(--foreground))] text-[hsl(var(--background))]'
                  : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
