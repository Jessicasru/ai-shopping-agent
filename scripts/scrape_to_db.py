"""Standalone scraper script for Railway cron jobs.

Runs the Sézane scraper and saves products directly to the shared Postgres DB.
Exits with code 1 on failure so Railway marks the cron run as failed.

Usage:
    python scripts/scrape_to_db.py

Railway cron schedule (Mondays 9am UTC):
    0 9 * * 1
"""

import sys
from pathlib import Path

# Add project root to path so we can import from src/ and backend/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models import init_db, save_products
from src.scrapers.sezane import SezaneScraper


def main():
    print("Initialising database...")
    init_db()

    print("Starting Sézane scrape...")
    scraper = SezaneScraper()
    try:
        products = scraper.scrape_new_arrivals()
    finally:
        scraper.close()

    if not products:
        print("ERROR: Scraper returned 0 products.", file=sys.stderr)
        sys.exit(1)

    print(f"Scraped {len(products)} products. Saving to DB...")
    product_dicts = [p.to_dict() for p in products]
    saved = save_products(product_dicts)
    print(f"Done. {saved} products upserted.")


if __name__ == "__main__":
    main()
