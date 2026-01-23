#!/usr/bin/env python3
"""Test script to run scrapers and see extracted data."""

import json
from datetime import datetime
from src.scrapers import SezaneScraper, ArketScraper


def main():
    all_products = []

    # Scrape Sezane
    print("=" * 60)
    print("SCRAPING SEZANE NEW ARRIVALS")
    print("=" * 60)
    sezane = SezaneScraper()
    sezane_products = sezane.scrape_new_arrivals()
    all_products.extend(sezane_products)
    sezane.close()

    print(f"\nSezane: Found {len(sezane_products)} products")
    for p in sezane_products[:5]:
        print(f"\n  Name: {p.name}")
        print(f"  Price: {p.price}")
        print(f"  URL: {p.url}")
        if p.image_url:
            print(f"  Image: {p.image_url[:70]}...")
        if p.colors:
            print(f"  Colors: {', '.join(p.colors)}")

    # Scrape Arket
    print("\n" + "=" * 60)
    print("SCRAPING ARKET NEW ARRIVALS")
    print("=" * 60)
    arket = ArketScraper()
    arket_products = arket.scrape_new_arrivals(debug=True)
    all_products.extend(arket_products)
    # Browser scraper handles cleanup automatically

    print(f"\nArket: Found {len(arket_products)} products")
    for p in arket_products[:5]:
        print(f"\n  Name: {p.name}")
        print(f"  Price: {p.price}")
        print(f"  URL: {p.url}")
        if p.image_url:
            print(f"  Image: {p.image_url[:70]}...")
        if p.colors:
            print(f"  Colors: {', '.join(p.colors)}")

    # Save results
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total products scraped: {len(all_products)}")
    print(f"  - Sezane: {len(sezane_products)}")
    print(f"  - Arket: {len(arket_products)}")

    # Save to JSON
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total_products": len(all_products),
        "products": [p.to_dict() for p in all_products]
    }

    output_path = "data/scraped_items/latest_arrivals.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
