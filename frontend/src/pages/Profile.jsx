import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { getProfile } from '../api';

const SECTION_LABELS = {
  color_palette: 'Color Palette',
  preferred_styles: 'Styles',
  silhouettes: 'Silhouettes',
  patterns: 'Patterns',
  materials: 'Materials',
  aesthetics: 'Aesthetic',
  avoid: 'Avoids',
};

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProfile().then((data) => {
      setProfile(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-[hsl(var(--border))] border-t-[hsl(var(--foreground))]" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-24 text-center">
        <h2 className="font-serif text-2xl text-[hsl(var(--foreground))]">No style profile yet</h2>
        <p className="mt-3 text-sm text-[hsl(var(--muted-foreground))]">
          Upload some style inspiration photos to get started.
        </p>
        <Link
          to="/upload"
          className="mt-6 inline-flex items-center gap-2 rounded-full bg-[hsl(var(--foreground))] px-6 py-2.5 text-sm tracking-[0.1em] uppercase text-[hsl(var(--background))] hover:opacity-90 transition-opacity"
        >
          Upload photos
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="font-serif text-3xl md:text-4xl tracking-tight text-[hsl(var(--foreground))]">
        Your style profile
      </h1>

      {profile.summary && (
        <p className="mt-5 text-sm text-[hsl(var(--muted-foreground))] leading-relaxed max-w-2xl">
          {profile.summary}
        </p>
      )}

      <div className="mt-12 space-y-10">
        {Object.entries(SECTION_LABELS).map(([key, label]) => {
          const items = profile[key];
          if (!items || items.length === 0) return null;

          return (
            <div key={key}>
              <h3 className="text-xs tracking-[0.15em] uppercase text-[hsl(var(--muted-foreground))]">
                {label}
              </h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {items.map((item, i) => (
                  <span
                    key={i}
                    className={`inline-block rounded-full px-4 py-1.5 text-sm ${
                      key === 'avoid'
                        ? 'bg-red-50 text-red-700 border border-red-200'
                        : 'border border-[hsl(var(--border))] text-[hsl(var(--foreground))]'
                    }`}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-14">
        <Link
          to="/matches"
          className="group inline-flex items-center gap-2.5 rounded-full bg-[hsl(var(--foreground))] px-8 py-3.5 text-sm tracking-[0.1em] uppercase text-[hsl(var(--background))] hover:opacity-90 transition-opacity"
        >
          <Sparkles className="h-4 w-4 transition-transform group-hover:rotate-12" />
          Find matches
        </Link>
      </div>
    </div>
  );
}
