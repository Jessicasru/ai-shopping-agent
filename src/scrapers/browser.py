"""Browser-based scraper for JavaScript-heavy sites using Playwright."""

import asyncio
from abc import abstractmethod
from typing import Optional

try:
    from playwright.async_api import async_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class BrowserScraper:
    """Base class for browser-based scraping with Playwright."""

    def __init__(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
        self.browser = None
        self.context = None

    async def _init_browser(self):
        """Initialize the browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

    async def _close_browser(self):
        """Close the browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def fetch_page(self, url: str, wait_selector: Optional[str] = None) -> Optional[str]:
        """Fetch page content using a real browser."""
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)

            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=10000)
                except Exception:
                    pass  # Continue even if selector not found

            # Scroll to load lazy content
            await self._scroll_page(page)

            html = await page.content()
            await page.close()
            return html
        except Exception as e:
            print(f"Browser error fetching {url}: {e}")
            return None

    async def _scroll_page(self, page: Page, scroll_count: int = 3):
        """Scroll page to trigger lazy loading."""
        for _ in range(scroll_count):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(0.5)
        # Scroll back to top
        await page.evaluate("window.scrollTo(0, 0)")

    @abstractmethod
    def get_new_arrivals_url(self) -> str:
        pass

    @abstractmethod
    def parse_products(self, html: str) -> list:
        pass

    async def scrape_new_arrivals_async(self, debug: bool = False) -> list:
        """Main async method to scrape new arrivals."""
        await self._init_browser()
        try:
            url = self.get_new_arrivals_url()
            print(f"Fetching (browser): {url}")
            html = await self.fetch_page(url)
            if html:
                if debug:
                    # Save HTML for debugging
                    debug_path = f"data/debug_{self.__class__.__name__}.html"
                    with open(debug_path, "w") as f:
                        f.write(html)
                    print(f"Saved debug HTML to {debug_path}")
                return self.parse_products(html)
            return []
        finally:
            await self._close_browser()

    def scrape_new_arrivals(self, debug: bool = False) -> list:
        """Sync wrapper for scraping."""
        return asyncio.run(self.scrape_new_arrivals_async(debug=debug))
