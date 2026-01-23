import re
from bs4 import BeautifulSoup
from ..models.product import Product

try:
    from .browser import BrowserScraper
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False
    BrowserScraper = object  # Fallback for type hints


class ArketScraper(BrowserScraper if BROWSER_AVAILABLE else object):
    """Scraper for Arket new arrivals using browser automation."""

    BASE_URL = "https://www.arket.com"

    def __init__(self):
        if BROWSER_AVAILABLE:
            super().__init__()

    def get_new_arrivals_url(self) -> str:
        return f"{self.BASE_URL}/en-ww/women/new-arrivals/"

    def parse_products(self, html: str) -> list[Product]:
        """Parse Arket product listings."""
        soup = BeautifulSoup(html, "lxml")
        products = []
        seen_urls = set()

        # Look for product links - Arket uses various patterns
        product_links = soup.select('a[href*="/p/"], a[href*="/product"]')
        if not product_links:
            product_links = soup.select('[class*="product"] a[href]')

        print(f"Found {len(product_links)} product links")

        for link in product_links:
            try:
                href = link.get("href", "")
                if not href or ("/p/" not in href and "/product" not in href):
                    continue

                full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                base_url = full_url.split('?')[0]  # Remove query params

                if base_url in seen_urls:
                    continue
                seen_urls.add(base_url)

                product = self._parse_product_link(link, base_url)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Error parsing product: {e}")
                continue

        print(f"Deduplicated to {len(products)} unique products")
        return products

    def _parse_product_link(self, link, url: str) -> Product | None:
        """Parse product from link element."""
        # Try to extract name from the link or nearby elements
        name = None

        # Check link text
        link_text = link.get_text(strip=True)
        if link_text and len(link_text) > 3 and len(link_text) < 100:
            name = link_text

        # Check for title/name elements
        if not name:
            name_elem = link.select_one('[class*="name"], [class*="title"], h2, h3, span')
            if name_elem:
                name = name_elem.get_text(strip=True)

        # Extract from URL as fallback
        if not name or name == "":
            match = re.search(r'/p/([^/?]+)', url) or re.search(r'/([^/]+)\.html', url)
            if match:
                name = match.group(1).replace('-', ' ').title()
            else:
                name = "Unknown"

        # Find image
        img = link.find("img")
        if not img:
            parent = link.parent
            for _ in range(3):
                if parent:
                    img = parent.find("img")
                    if img:
                        break
                    parent = parent.parent

        image_url = ""
        if img:
            image_url = img.get("src") or img.get("data-src") or ""
            if not image_url and img.get("srcset"):
                image_url = img.get("srcset", "").split(",")[0].split()[0]
            if image_url and not image_url.startswith("http"):
                image_url = f"https:{image_url}" if image_url.startswith("//") else f"{self.BASE_URL}{image_url}"

        # Find price near the link
        price = "N/A"
        parent = link.parent
        for _ in range(4):
            if parent:
                price_elem = parent.select_one('[class*="price"], [class*="Price"]')
                if price_elem:
                    price = price_elem.get_text(strip=True)
                    break
                parent = parent.parent

        return Product(
            name=name,
            price=price,
            url=url,
            image_url=image_url,
            retailer="Arket",
            colors=[],
        )

    def scrape_new_arrivals(self, debug: bool = False) -> list:
        """Scrape using browser if available, otherwise return empty with message."""
        if not BROWSER_AVAILABLE:
            print("Playwright not available. Install with: pip install playwright && playwright install chromium")
            return []
        products = super().scrape_new_arrivals(debug=debug)
        if not products:
            print("Note: Arket has strong bot protection (Akamai). Consider using their mobile app API or RSS feeds.")
        return products


if __name__ == "__main__":
    scraper = ArketScraper()
    products = scraper.scrape_new_arrivals()
    print(f"\nFound {len(products)} products:\n")
    for p in products[:10]:
        print(f"- {p.name}: {p.price}")
        print(f"  URL: {p.url}")
        print(f"  Image: {p.image_url[:80]}..." if p.image_url else "  No image")
        print()
    scraper.close()
