import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export default function Landing() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-24 text-center">
      <h1 className="font-serif text-5xl md:text-6xl tracking-tight text-[hsl(var(--foreground))]">
        Your AI Personal Stylist
      </h1>
      <p className="mt-6 text-base text-[hsl(var(--muted-foreground))] max-w-xl mx-auto leading-relaxed">
        Upload photos of outfits you love, and our AI analyzes your unique style
        to find perfect matches from curated retailers like S&eacute;zane.
      </p>

      <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          to="/upload"
          className="group inline-flex items-center justify-center gap-2 rounded-full bg-[hsl(var(--foreground))] px-8 py-3.5 text-sm tracking-[0.1em] uppercase text-[hsl(var(--background))] hover:opacity-90 transition-opacity"
        >
          <Sparkles className="h-4 w-4 transition-transform group-hover:rotate-12" />
          Get Started
        </Link>
        <Link
          to="/matches"
          className="inline-flex items-center justify-center rounded-full border border-[hsl(var(--border))] px-8 py-3.5 text-sm tracking-[0.1em] uppercase text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:border-[hsl(var(--foreground)/0.3)] transition-colors"
        >
          View Matches
        </Link>
      </div>

      <div className="mt-28 grid grid-cols-1 sm:grid-cols-3 gap-px bg-[hsl(var(--border))] rounded-xl overflow-hidden">
        {[
          {
            step: '01',
            title: 'Upload Style Photos',
            desc: 'Share outfit photos, Pinterest inspiration, or items you love.',
          },
          {
            step: '02',
            title: 'AI Analyzes Your Style',
            desc: 'Claude vision extracts your color palette, silhouettes, and aesthetic preferences.',
          },
          {
            step: '03',
            title: 'Get Personalized Picks',
            desc: 'See scored product matches with styling notes and pairing suggestions.',
          },
        ].map(({ step, title, desc }) => (
          <div key={step} className="bg-[hsl(var(--card))] p-8">
            <span className="text-xs tracking-[0.2em] text-[hsl(var(--muted-foreground)/0.5)]">
              {step}
            </span>
            <h3 className="mt-4 font-serif text-lg text-[hsl(var(--foreground))]">{title}</h3>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
              {desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
