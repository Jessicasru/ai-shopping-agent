function ScoreDot({ score }) {
  const color =
    score >= 8
      ? 'bg-emerald-500'
      : score >= 6
        ? 'bg-amber-400'
        : 'bg-neutral-400';

  return (
    <span
      className={`inline-block size-2 rounded-full ${color}`}
      aria-hidden="true"
    />
  );
}

export function ProductCard({ image, name, price, score, reasoning, url }) {
  const scoreLabel =
    score >= 8 ? 'Great match' : score >= 6 ? 'Good match' : 'Low match';

  return (
    <article className="group flex w-full max-w-sm flex-col overflow-hidden rounded-lg bg-[hsl(var(--card))] transition-shadow duration-300 hover:shadow-lg">
      {/* Product Image */}
      <div className="relative aspect-[4/5] w-full overflow-hidden rounded-t-lg">
        <img
          src={image || ''}
          alt={name}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
        />
      </div>

      {/* Card Content */}
      <div className="flex flex-1 flex-col gap-4 p-5">
        {/* Name & Price */}
        <div className="flex items-baseline justify-between gap-3">
          <h3 className="text-base font-medium tracking-tight text-[hsl(var(--card-foreground))]">
            {name}
          </h3>
          <span className="shrink-0 text-sm text-[hsl(var(--muted-foreground))]">
            {price}
          </span>
        </div>

        {/* AI Match Score */}
        <div className="flex items-center gap-2">
          <ScoreDot score={score} />
          <span className="text-xs font-medium tracking-wide text-[hsl(var(--card-foreground))]">
            {score.toFixed(1)}/10 match
          </span>
          <span className="sr-only">{scoreLabel}</span>
        </div>

        {/* Reasoning */}
        <p className="line-clamp-3 text-xs leading-relaxed text-[hsl(var(--muted-foreground))]">
          {reasoning}
        </p>

        {/* View Product Link */}
        <div className="mt-auto pt-2">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block text-xs font-medium tracking-wide text-[hsl(var(--card-foreground))] underline underline-offset-4 transition-opacity hover:opacity-60"
          >
            View Product
          </a>
        </div>
      </div>
    </article>
  );
}
