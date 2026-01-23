# AI Personal Shopping Agent

An AI-powered personal shopping assistant that scrapes new arrivals from fashion retailers and uses Claude's vision API to match products against your unique style profile.

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Your Style     │     │  Retailer       │     │  Claude Vision  │
│  Images         │────▶│  Scraping       │────▶│  Matching       │
│  (3-10 photos)  │     │  (New Arrivals) │     │  (Score 1-10)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Style Profile  │     │  Product Data   │     │  Curated Feed   │
│  (JSON)         │     │  (Name, Price,  │     │  (HTML Report)  │
│                 │     │   Image, URL)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 1. Style Analysis
Add your outfit photos or fashion inspiration images. Claude analyzes them to extract your preferences:
- Color palette
- Preferred silhouettes
- Patterns and materials
- Overall aesthetic

### 2. Product Scraping
The agent scrapes new arrivals from supported retailers, extracting:
- Product name and price
- High-resolution images
- Product URLs
- Available colors

### 3. Vision Matching
Each product image is analyzed against your style profile. Claude provides:
- Match score (1-10)
- Reasoning for the score
- Style notes
- Suggested pairings

## Supported Retailers

| Retailer | Status | Method |
|----------|--------|--------|
| Sézane | ✅ Working | HTTP |
| Arket | ⚠️ Blocked | Playwright (blocked by Akamai) |

## Setup

### Prerequisites
- Python 3.11+
- Anthropic API key

### Installation

```bash
# Clone and enter directory
cd shopping-agent

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JS-heavy sites)
playwright install chromium

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Configuration

Create a `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Usage

### Quick Start

```bash
# 1. Add your style images to data/style_profiles/
#    (outfit photos, Pinterest inspiration, etc.)

# 2. Analyze your style
python3 analyze_style.py

# 3. Run the shopping agent
python3 shop.py
```

### Commands

| Script | Description |
|--------|-------------|
| `analyze_style.py` | Build style profile from your images |
| `shop.py` | Full pipeline: scrape + match + save results |
| `run_scrapers.py` | Scrape only (no matching) |
| `find_matches.py` | Match only (use cached products) |
| `generate_feed.py` | Generate HTML feed from recommendations |

### Options

```bash
# Scrape only (no API calls)
python3 shop.py --scrape-only

# Match cached products
python3 shop.py --match-only --limit 50 --min-score 7 --top 20

# Generate HTML feed
python3 generate_feed.py --output my-picks.html
```

## Example Output

### Style Profile

```
YOUR STYLE PROFILE
============================================================

This style embodies effortless European sophistication with a focus on
quality basics, neutral tones, and timeless pieces. The aesthetic combines
minimalist elegance with relaxed tailoring, emphasizing comfort without
sacrificing style.

Colors:    denim blue, crisp white, charcoal black, warm brown, olive green
Styles:    minimalist chic, European casual, classic Parisian, elevated basics
Silhouettes: wide-leg jeans, oversized blazers, midi length, high-waisted
Patterns:  solid colors, subtle stripes, minimal prints
Materials: denim, wool, cashmere, cotton, linen, leather
Aesthetic: effortless elegance, understated luxury, French girl chic
Avoids:    bright neon, overly fitted clothing, excessive patterns
```

### Product Matches

```
TOP MATCHES FOR YOU
============================================================

1. Gary Maxi Bag
   ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10)
   Price: $445 | Sezane
   This chocolate brown leather bag perfectly embodies the effortless
   European sophistication aesthetic with its clean lines and quality
   construction.
   🔗 https://www.sezane.com/us-en/product/gary-maxi-bag/choco

2. Pierce Coat
   ⭐⭐⭐⭐⭐⭐⭐⭐⭐☆ (9/10)
   Price: $355 | Sezane
   Classic double-breasted trench in light beige. The neutral color
   and timeless silhouette embody French girl chic perfectly.
   🔗 https://www.sezane.com/us-en/product/pierce-coat/light-beige

3. Alphee Jacket
   ⭐⭐⭐⭐⭐⭐⭐⭐☆☆ (8/10)
   Price: $285 | Sezane
   Honey-colored oversized blazer matching the preference for warm
   neutrals and relaxed tailoring.
   🔗 https://www.sezane.com/us-en/product/alphee-jacket/honey
```

### HTML Feed

The agent generates a beautiful, responsive HTML feed:

![Feed Preview](data/feed-preview.png)

## Project Structure

```
shopping-agent/
├── shop.py                 # Main entry point
├── analyze_style.py        # Style profile builder
├── find_matches.py         # Product matcher
├── run_scrapers.py         # Scraper runner
├── generate_feed.py        # HTML feed generator
├── requirements.txt
├── .env.example
│
├── src/
│   ├── scrapers/
│   │   ├── base.py         # HTTP scraper base class
│   │   ├── browser.py      # Playwright browser scraper
│   │   ├── sezane.py       # Sézane scraper
│   │   └── arket.py        # Arket scraper
│   │
│   ├── vision/
│   │   ├── style_analyzer.py   # Extracts style from images
│   │   └── product_matcher.py  # Matches products to style
│   │
│   └── models/
│       └── product.py      # Product data model
│
└── data/
    ├── style_profiles/     # Your style images + profile.json
    ├── scraped_items/      # Scraped products + recommendations
    └── feed.html           # Generated HTML feed
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| AI/Vision | Claude API (claude-sonnet-4-20250514) |
| HTTP Client | httpx |
| Browser Automation | Playwright |
| HTML Parsing | BeautifulSoup4 + lxml |
| Config | python-dotenv |

## API Costs

The agent uses Claude's vision API for style analysis and product matching:

| Operation | Model | Est. Cost |
|-----------|-------|-----------|
| Style Analysis | claude-sonnet-4-20250514 | ~$0.05-0.10 (10 images) |
| Product Match | claude-sonnet-4-20250514 | ~$0.01-0.02 per product |
| 50 Products | claude-sonnet-4-20250514 | ~$0.50-1.00 total |

## Adding New Retailers

1. Create a new scraper in `src/scrapers/`:

```python
from .base import BaseScraper
from ..models.product import Product

class NewRetailerScraper(BaseScraper):
    BASE_URL = "https://www.retailer.com"

    def get_new_arrivals_url(self) -> str:
        return f"{self.BASE_URL}/new-arrivals"

    def parse_products(self, html: str) -> list[Product]:
        # Parse HTML and return Product objects
        ...
```

2. Add to `src/scrapers/__init__.py`
3. Import in `shop.py` and add to `scrape_all()`

## Limitations

- **Bot Protection**: Some retailers (Arket, Zara) use aggressive bot detection
- **Dynamic Content**: Sites with heavy JavaScript may need Playwright
- **Rate Limiting**: Add delays between requests for production use
- **Price Extraction**: Prices aren't always in the initial HTML

## License

MIT
