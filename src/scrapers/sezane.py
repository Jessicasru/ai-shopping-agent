import re
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..models.product import Product


class SezaneScraper(BaseScraper):
    """Scraper for Sezane new arrivals."""

    BASE_URL = "https://www.sezane.com"

    def get_new_arrivals_url(self) -> str:
        return f"{self.BASE_URL}/us-en/new-in"

    def parse_products(self, html: str) -> list[Product]:
        """Parse Sezane product listings."""
        soup = BeautifulSoup(html, "lxml")
        products = []
        seen_urls = set()

        # Find all product links - look for unique product URLs
        product_links = soup.select('a[href*="/product/"]')
        print(f"Found {len(product_links)} product links")

        for link in product_links:
            try:
                href = link.get("href", "")
                if not href or "/product/" not in href:
                    continue

                # Normalize URL - remove fragments (size variants) to deduplicate
                full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                base_url = full_url.split('#')[0]  # Remove fragment

                # Skip if already seen this URL
                if base_url in seen_urls:
                    continue
                seen_urls.add(base_url)

                product = self._parse_product_link(link, base_url, full_url)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Error parsing product: {e}")
                continue

        print(f"Deduplicated to {len(products)} unique products")
        return products

    def _parse_product_link(self, link, base_url: str, full_url: str) -> Product | None:
        """Parse product from link element."""
        # Extract product name from URL path
        # URL pattern: /product/product-name/color
        match = re.search(r'/product/([^/]+)', base_url)
        if match:
            # Convert URL slug to readable name
            name_slug = match.group(1)
            name = name_slug.replace('-', ' ').title()
            # Clean up common patterns
            name = re.sub(r'\s+Sezane\s+X\s+', ' × ', name, flags=re.IGNORECASE)
        else:
            name = "Unknown"

        # Extract color from URL if present (before fragment)
        color_match = re.search(r'/product/[^/]+/([^/?#]+)', base_url)
        colors = [color_match.group(1).replace('-', ' ').title()] if color_match else []

        url = base_url  # Use base URL without fragment

        # Find image - check the link and its parent containers
        img = link.find("img")
        if not img:
            parent = link.parent
            for _ in range(3):  # Check up to 3 levels up
                if parent:
                    img = parent.find("img")
                    if img:
                        break
                    parent = parent.parent

        image_url = ""
        if img:
            image_url = img.get("src") or img.get("data-src") or ""
            # Handle srcset
            if not image_url and img.get("srcset"):
                srcset = img.get("srcset", "")
                # Get first image from srcset
                image_url = srcset.split(",")[0].split()[0]
            if image_url and not image_url.startswith("http"):
                image_url = f"https:{image_url}" if image_url.startswith("//") else f"{self.BASE_URL}{image_url}"

        # Try to find price near the link
        price = "N/A"
        parent = link.parent
        for _ in range(4):
            if parent:
                price_elem = parent.find(string=re.compile(r'\$\d+'))
                if price_elem:
                    price = price_elem.strip()
                    break
                # Also check for price class
                price_div = parent.select_one('[class*="price"], [class*="Price"]')
                if price_div:
                    price = price_div.get_text(strip=True)
                    break
                parent = parent.parent

        return Product(
            name=name,
            price=price,
            url=url,
            image_url=image_url,
            retailer="Sezane",
            colors=colors,
        )


if __name__ == "__main__":
    scraper = SezaneScraper()
    products = scraper.scrape_new_arrivals()
    print(f"\nFound {len(products)} products:\n")
    for p in products[:10]:
        print(f"- {p.name}: {p.price}")
        print(f"  URL: {p.url}")
        print(f"  Image: {p.image_url[:80]}..." if p.image_url else "  No image")
        print()
    scraper.close()
