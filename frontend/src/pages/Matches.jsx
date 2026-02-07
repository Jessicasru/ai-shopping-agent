import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ProductCard } from '../components/ProductCard';
import { getRecommendations, findMatches } from '../api';

export default function Matches() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getRecommendations().then((d) => {
      setData(d);
      setLoading(false);
    });
  }, []);

  const handleRunMatching = async () => {
    setMatching(true);
    setError(null);
    try {
      const result = await findMatches({ limit: 25, min_score: 6 });
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setMatching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-[hsl(var(--border))] border-t-[hsl(var(--foreground))]" />
      </div>
    );
  }

  if (!data || !data.recommendations?.length) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-24 text-center">
        <h2 className="font-serif text-2xl text-[hsl(var(--foreground))]">No Matches Yet</h2>
        <p className="mt-3 text-sm text-[hsl(var(--muted-foreground))]">
          Run the matching engine to find products that fit your style.
        </p>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
        <button
          onClick={handleRunMatching}
          disabled={matching}
          className="mt-6 rounded-full bg-[hsl(var(--foreground))] px-6 py-2.5 text-sm font-medium text-[hsl(var(--background))] hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {matching ? 'Matching products...' : 'Find Matches'}
        </button>
        <p className="mt-4 text-xs text-[hsl(var(--muted-foreground))]">
          Need a profile first?{' '}
          <Link to="/upload" className="underline underline-offset-4">Upload photos</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-16">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-serif text-3xl md:text-4xl tracking-tight text-[hsl(var(--foreground))]">
            Your matches
          </h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {data.matches_found} matches from {data.products_analyzed} products analyzed
          </p>
        </div>
        <button
          onClick={handleRunMatching}
          disabled={matching}
          className="rounded-full border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-5 py-2 text-xs tracking-[0.1em] uppercase text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:border-[hsl(var(--foreground)/0.3)] disabled:opacity-40 transition-colors"
        >
          {matching ? 'Matching...' : 'Refresh'}
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {data.recommendations.map((match, i) => (
          <ProductCard
            key={i}
            image={match.product.image_url}
            name={match.product.name}
            price={match.product.price !== 'N/A' ? match.product.price : ''}
            score={match.score}
            reasoning={match.reasoning}
            url={match.product.url}
          />
        ))}
      </div>
    </div>
  );
}
