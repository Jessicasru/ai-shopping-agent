#!/usr/bin/env python3
"""Find products that match your style profile."""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.vision import StyleAnalyzer, ProductMatcher
from src.models.product import Product

load_dotenv()


def load_products(path: Path) -> list[Product]:
    """Load products from JSON file."""
    with open(path) as f:
        data = json.load(f)

    products = []
    for p in data.get("products", []):
        products.append(Product(
            name=p["name"],
            price=p["price"],
            url=p["url"],
            image_url=p["image_url"],
            retailer=p["retailer"],
            category=p.get("category"),
            colors=p.get("colors", []),
            sizes=p.get("sizes", []),
            description=p.get("description"),
        ))
    return products


def main():
    # Load style profile
    profile_path = Path("data/style_profiles/profile.json")
    if not profile_path.exists():
        print("No style profile found. Run analyze_style.py first.")
        print("Add your style images to data/style_profiles/ and run:")
        print("  python3 analyze_style.py")
        sys.exit(1)

    analyzer = StyleAnalyzer()
    profile = analyzer.load_profile(profile_path)
    print("Loaded style profile:")
    print(f"  {profile.summary}\n")

    # Load scraped products
    products_path = Path("data/scraped_items/latest_arrivals.json")
    if not products_path.exists():
        print("No scraped products found. Run run_scrapers.py first.")
        sys.exit(1)

    products = load_products(products_path)
    print(f"Loaded {len(products)} products\n")

    # Match products
    matcher = ProductMatcher(profile)

    # For demo, limit to first 20 products (API calls cost money)
    # Adjust limit as needed
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20, help="Max products to analyze")
    parser.add_argument("--min-score", type=int, default=6, help="Minimum match score (1-10)")
    parser.add_argument("--all", action="store_true", help="Analyze all products (can be slow/expensive)")
    args = parser.parse_args()

    limit = None if args.all else args.limit

    results = matcher.match_products(
        products,
        min_score=args.min_score,
        limit=limit,
    )

    # Display results
    print("\n" + "=" * 60)
    print(f"TOP MATCHES (score >= {args.min_score})")
    print("=" * 60)

    if not results:
        print("\nNo products matched your style profile above the threshold.")
        print("Try lowering --min-score or adding more style reference images.")
    else:
        for i, result in enumerate(results[:15], 1):
            print(f"\n{i}. {result.product.name}")
            print(f"   Score: {result.score}/10 | Price: {result.product.price}")
            print(f"   {result.reasoning}")
            if result.suggested_pairings:
                print(f"   Pairs with: {', '.join(result.suggested_pairings)}")
            print(f"   URL: {result.product.url}")

    # Save results
    output_path = Path("data/scraped_items/matched_products.json")
    with open(output_path, "w") as f:
        json.dump({
            "style_summary": profile.summary,
            "total_analyzed": limit or len(products),
            "matches_found": len(results),
            "min_score_threshold": args.min_score,
            "results": [r.to_dict() for r in results],
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
