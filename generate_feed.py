#!/usr/bin/env python3
"""Generate a beautiful HTML product feed from recommendations."""

import json
import html
from pathlib import Path
from datetime import datetime
from string import Template


CSS = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #fafafa;
            color: #1a1a1a;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 60px 40px;
        }

        header {
            text-align: center;
            margin-bottom: 60px;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 300;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 16px;
        }

        .subtitle {
            font-size: 1rem;
            color: #666;
            max-width: 600px;
            margin: 0 auto;
            font-weight: 300;
        }

        .meta {
            font-size: 0.75rem;
            color: #999;
            margin-top: 20px;
            letter-spacing: 0.05em;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid #eee;
        }

        .stat {
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 300;
        }

        .stat-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #888;
            margin-top: 4px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 40px;
        }

        .card {
            background: #fff;
            border-radius: 2px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.08);
        }

        .card-image {
            position: relative;
            aspect-ratio: 3/4;
            overflow: hidden;
            background: #f5f5f5;
        }

        .card-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }

        .card:hover .card-image img {
            transform: scale(1.03);
        }

        .score-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 8px 14px;
            border-radius: 2px;
            font-size: 0.8rem;
            font-weight: 500;
            letter-spacing: 0.02em;
        }

        .score-badge.excellent {
            background: rgba(26, 26, 26, 0.9);
            color: #fff;
        }

        .score-dots {
            display: flex;
            gap: 3px;
            margin-top: 4px;
        }

        .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #ddd;
        }

        .dot.filled {
            background: currentColor;
        }

        .score-badge.excellent .dot {
            background: #444;
        }

        .score-badge.excellent .dot.filled {
            background: #fff;
        }

        .card-content {
            padding: 24px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .product-name {
            font-size: 1.1rem;
            font-weight: 500;
            letter-spacing: 0.01em;
            flex: 1;
            padding-right: 16px;
        }

        .product-price {
            font-size: 1rem;
            color: #1a1a1a;
            font-weight: 400;
            white-space: nowrap;
        }

        .retailer {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #888;
            margin-bottom: 16px;
        }

        .reasoning {
            font-size: 0.9rem;
            color: #555;
            line-height: 1.7;
            margin-bottom: 20px;
        }

        .buy-link {
            display: inline-block;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: #1a1a1a;
            text-decoration: none;
            padding-bottom: 2px;
            border-bottom: 1px solid #1a1a1a;
            transition: opacity 0.2s;
        }

        .buy-link:hover {
            opacity: 0.6;
        }

        .no-image {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #ccc;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        footer {
            text-align: center;
            margin-top: 80px;
            padding-top: 40px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }

        @media (max-width: 768px) {
            .container {
                padding: 40px 20px;
            }

            h1 {
                font-size: 1.8rem;
            }

            .grid {
                grid-template-columns: 1fr;
                gap: 30px;
            }

            .stats {
                gap: 24px;
            }

            .stat-value {
                font-size: 1.5rem;
            }
        }
"""


def generate_dots(score: int) -> str:
    """Generate score indicator dots."""
    dots = []
    for i in range(10):
        filled = " filled" if i < score else ""
        dots.append(f'<span class="dot{filled}"></span>')
    return "\n                            ".join(dots)


def generate_card(result: dict) -> str:
    """Generate HTML for a single product card."""
    product = result.get("product", {})

    name = html.escape(product.get("name", "Unknown"))
    price = product.get("price", "N/A")
    if price == "N/A" or not price:
        price = "Price on site"
    price = html.escape(str(price))

    retailer = html.escape(product.get("retailer", ""))
    url = html.escape(product.get("url", "#"))
    image_url = product.get("image_url", "")

    score = result.get("score", 0)
    reasoning = html.escape(result.get("reasoning", ""))

    # Image HTML
    if image_url:
        image_html = f'<img src="{html.escape(image_url)}" alt="{name}" loading="lazy">'
    else:
        image_html = '<div class="no-image">No image available</div>'

    # Score class for styling
    score_class = " excellent" if score >= 9 else ""

    # Generate dots
    dots = generate_dots(score)

    return f"""
            <article class="card">
                <div class="card-image">
                    {image_html}
                    <div class="score-badge{score_class}">
                        {score}/10
                        <div class="score-dots">
                            {dots}
                        </div>
                    </div>
                </div>
                <div class="card-content">
                    <div class="card-header">
                        <h2 class="product-name">{name}</h2>
                        <span class="product-price">{price}</span>
                    </div>
                    <p class="retailer">{retailer}</p>
                    <p class="reasoning">{reasoning}</p>
                    <a href="{url}" target="_blank" rel="noopener" class="buy-link">View Product</a>
                </div>
            </article>"""


def generate_feed(input_path: Path, output_path: Path):
    """Generate HTML feed from recommendations JSON."""
    with open(input_path) as f:
        data = json.load(f)

    results = data.get("recommendations", []) or data.get("results", [])
    if not results:
        print("No results found in recommendations.json")
        return

    # Generate cards
    cards = [generate_card(r) for r in results]
    product_cards = "\n".join(cards)

    # Calculate stats
    scores = [r.get("score", 0) for r in results]
    top_score = max(scores) if scores else 0
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # Format date
    generated_at = data.get("generated_at", "")
    if generated_at:
        try:
            dt = datetime.fromisoformat(generated_at)
            generated_date = dt.strftime("%B %d, %Y at %I:%M %p")
        except ValueError:
            generated_date = generated_at
    else:
        generated_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    style_summary = html.escape(data.get("style_summary", ""))

    # Build final HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Curated Picks</title>
    <style>{CSS}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Your Curated Picks</h1>
            <p class="subtitle">{style_summary}</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(results)}</div>
                    <div class="stat-label">Matches Found</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{top_score}/10</div>
                    <div class="stat-label">Best Score</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{avg_score}</div>
                    <div class="stat-label">Avg Score</div>
                </div>
            </div>
            <p class="meta">Generated {generated_date}</p>
        </header>

        <div class="grid">
{product_cards}
        </div>

        <footer>
            Curated by AI Shopping Agent · Powered by Claude Vision
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, "w") as f:
        f.write(html_content)

    print(f"Generated feed with {len(results)} products")
    print(f"Saved to: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate HTML product feed")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/scraped_items/recommendations.json"),
        help="Input recommendations JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/feed.html"),
        help="Output HTML file",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}")
        print("Run shop.py first to generate recommendations.")
        return

    generate_feed(args.input, args.output)


if __name__ == "__main__":
    main()
