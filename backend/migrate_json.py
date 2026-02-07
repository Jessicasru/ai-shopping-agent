"""Migrate products from JSON files into the Postgres database."""

import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models import init_db, save_products


def migrate(json_path: str | None = None) -> None:
    path = Path(json_path) if json_path else PROJECT_ROOT / "data" / "scraped_items" / "latest_arrivals.json"

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    products = data.get("products", [])
    scraped_at = data.get("scraped_at")

    if not products:
        print("No products found in JSON file.")
        sys.exit(1)

    print(f"Found {len(products)} products in {path.name}")
    print("Initializing database...")
    init_db()

    print("Saving products...")
    saved = save_products(products, scraped_at=scraped_at)
    print(f"Done — {saved} products saved to database.")


if __name__ == "__main__":
    json_file = sys.argv[1] if len(sys.argv) > 1 else None
    migrate(json_file)
