from abc import ABC, abstractmethod
import httpx
from typing import Optional


class BaseScraper(ABC):
    """Base class for all retail scrapers."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=30.0)

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"Error fetching {url}: {e}")
            return None

    @abstractmethod
    def get_new_arrivals_url(self) -> str:
        """Return the URL for new arrivals."""
        pass

    @abstractmethod
    def parse_products(self, html: str) -> list:
        """Parse products from HTML content."""
        pass

    def scrape_new_arrivals(self) -> list:
        """Main method to scrape new arrivals."""
        url = self.get_new_arrivals_url()
        print(f"Fetching: {url}")
        html = self.fetch_page(url)
        if html:
            return self.parse_products(html)
        return []

    def close(self):
        self.client.close()
