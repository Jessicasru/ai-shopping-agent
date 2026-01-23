#!/usr/bin/env python3
"""Main shopping agent - scrape and match in one command."""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.scrapers import SezaneScraper, ArketScraper
from src.vision import StyleAnalyzer, ProductMatcher
from src.models.product import Product

load_dotenv()


def scrape_all() -> list[Product]:
    """Scrape all retailers and return products."""
    all_products = []

    print("Scraping new arrivals...")

    # Sezane
    print("  - Sezane...", end=" ", flush=True)
    sezane = SezaneScraper()
    sezane_products = sezane.scrape_new_arrivals()
    all_products.extend(sezane_products)
    sezane.close()
    print(f"{len(sezane_products)} products")

    # Arket (may fail due to bot protection)
    print("  - Arket...", end=" ", flush=True)
    arket = ArketScraper()
    arket_products = arket.scrape_new_arrivals()
    all_products.extend(arket_products)
    print(f"{len(arket_products)} products")

    return all_products


def save_products(products: list[Product], path: Path):
    """Save products to JSON."""
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total_products": len(products),
        "products": [p.to_dict() for p in products],
    }
    with open(path, "w") as f:
        json.dump(output, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered personal shopping agent"
    )
    parser.add_argument(
        "--scrape-only",
        action="store_true",
        help="Only scrape products, don't match",
    )
    parser.add_argument(
        "--match-only",
        action="store_true",
        help="Only match products (use cached scraped data)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Max products to analyze for matching",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=6,
        help="Minimum match score to show (1-10)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top matches to display",
    )
    args = parser.parse_args()

    products_path = Path("data/scraped_items/latest_arrivals.json")
    profile_path = Path("data/style_profiles/profile.json")

    # Scrape products
    if not args.match_only:
        products = scrape_all()
        save_products(products, products_path)
        print(f"\nTotal: {len(products)} products scraped\n")
    else:
        # Load cached products
        if not products_path.exists():
            print("No cached products. Run without --match-only first.")
            return
        with open(products_path) as f:
            data = json.load(f)
        products = [
            Product(
                name=p["name"],
                price=p["price"],
                url=p["url"],
                image_url=p["image_url"],
                retailer=p["retailer"],
                colors=p.get("colors", []),
            )
            for p in data["products"]
        ]
        print(f"Loaded {len(products)} cached products\n")

    if args.scrape_only:
        print("Scrape complete. Run with --match-only to find matches.")
        return

    # Check for style profile
    if not profile_path.exists():
        print("=" * 60)
        print("STYLE PROFILE NEEDED")
        print("=" * 60)
        print("\nTo find products that match your style, add reference images:")
        print("  1. Add outfit photos or inspiration images to:")
        print("     data/style_profiles/")
        print("  2. Run: python3 analyze_style.py")
        print("  3. Then run this script again")
        return

    # Load profile and match
    print("=" * 60)
    print("FINDING YOUR PERFECT MATCHES")
    print("=" * 60)

    analyzer = StyleAnalyzer()
    profile = analyzer.load_profile(profile_path)
    print(f"\nYour style: {profile.summary}\n")

    matcher = ProductMatcher(profile)
    results = matcher.match_products(
        products,
        min_score=args.min_score,
        limit=args.limit,
    )

    # Display top results
    print("\n" + "=" * 60)
    print(f"🛍️  TOP {min(args.top, len(results))} MATCHES FOR YOU")
    print("=" * 60)

    if not results:
        print("\nNo strong matches found. Try:")
        print("  - Lowering --min-score")
        print("  - Adding more style reference images")
        print("  - Increasing --limit to analyze more products")
    else:
        for i, result in enumerate(results[: args.top], 1):
            p = result.product
            print(f"\n{i}. {p.name}")
            print(f"   {'⭐' * result.score}{'☆' * (10 - result.score)} ({result.score}/10)")
            print(f"   Price: {p.price} | {p.retailer}")
            print(f"   {result.reasoning}")
            if result.style_notes:
                print(f"   Style note: {result.style_notes}")
            print(f"   🔗 {p.url}")

    # Save full results
    output_path = Path("data/scraped_items/recommendations.json")
    with open(output_path, "w") as f:
        json.dump(
            {
                "generated_at": datetime.now().isoformat(),
                "style_summary": profile.summary,
                "products_analyzed": args.limit,
                "matches_found": len(results),
                "recommendations": [r.to_dict() for r in results],
            },
            f,
            indent=2,
        )
    print(f"\n\nFull results saved to: {output_path}")


if __name__ == "__main__":
    main()
