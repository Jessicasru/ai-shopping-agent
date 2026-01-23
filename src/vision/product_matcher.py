"""Match products against a style profile using Claude's vision."""

import base64
import httpx
import anthropic
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .style_analyzer import StyleProfile
from ..models.product import Product


@dataclass
class MatchResult:
    """Result of matching a product against a style profile."""

    product: Product
    score: int  # 1-10
    reasoning: str
    style_notes: str
    suggested_pairings: list[str]

    def to_dict(self) -> dict:
        return {
            "product": self.product.to_dict(),
            "score": self.score,
            "reasoning": self.reasoning,
            "style_notes": self.style_notes,
            "suggested_pairings": self.suggested_pairings,
        }


class ProductMatcher:
    """Matches products against a style profile using vision analysis."""

    def __init__(self, style_profile: StyleProfile, api_key: str | None = None):
        self.profile = style_profile
        self.client = anthropic.Anthropic(api_key=api_key)
        self.http_client = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/122.0.0.0"
            }
        )

    def _fetch_image(self, url: str) -> tuple[str, str] | None:
        """Fetch image from URL and return base64 data and media type."""
        try:
            response = self.http_client.get(url, follow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "image/jpeg")
            if ";" in content_type:
                content_type = content_type.split(";")[0]

            # Validate it's actually an image
            if not content_type.startswith("image/"):
                return None

            data = base64.standard_b64encode(response.content).decode("utf-8")
            return data, content_type
        except Exception as e:
            print(f"Error fetching image: {e}")
            return None

    def _build_profile_context(self) -> str:
        """Build a text description of the style profile for the prompt."""
        p = self.profile
        parts = []

        if p.summary:
            parts.append(f"Style Summary: {p.summary}")
        if p.color_palette:
            parts.append(f"Preferred Colors: {', '.join(p.color_palette)}")
        if p.preferred_styles:
            parts.append(f"Style Categories: {', '.join(p.preferred_styles)}")
        if p.silhouettes:
            parts.append(f"Preferred Silhouettes: {', '.join(p.silhouettes)}")
        if p.patterns:
            parts.append(f"Preferred Patterns: {', '.join(p.patterns)}")
        if p.materials:
            parts.append(f"Preferred Materials: {', '.join(p.materials)}")
        if p.aesthetics:
            parts.append(f"Aesthetic: {', '.join(p.aesthetics)}")
        if p.avoid:
            parts.append(f"Tends to Avoid: {', '.join(p.avoid)}")

        return "\n".join(parts)

    def match_product(self, product: Product) -> MatchResult | None:
        """Match a single product against the style profile."""
        if not product.image_url:
            return None

        image_data = self._fetch_image(product.image_url)
        if not image_data:
            return None

        data, media_type = image_data
        profile_context = self._build_profile_context()

        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": data,
                },
            },
            {
                "type": "text",
                "text": f"""Analyze this product image and determine how well it matches the following style profile:

{profile_context}

Product Info:
- Name: {product.name}
- Price: {product.price}
- Colors: {', '.join(product.colors) if product.colors else 'Not specified'}

Return a JSON object with:
{{
    "score": <1-10 integer, where 10 is perfect match>,
    "reasoning": "<2-3 sentences explaining the score>",
    "style_notes": "<how this piece fits or doesn't fit the aesthetic>",
    "suggested_pairings": ["<2-3 items from their wardrobe this would pair with>"]
}}

Be honest and critical. A score of 7+ means it's a strong match worth buying.
A score of 5-6 means it could work but isn't ideal.
Below 5 means it doesn't align well with the style profile.

Return ONLY the JSON object."""
            }
        ]

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": content}]
            )

            response_text = response.content[0].text
            # Clean up markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())

            return MatchResult(
                product=product,
                score=result.get("score", 0),
                reasoning=result.get("reasoning", ""),
                style_notes=result.get("style_notes", ""),
                suggested_pairings=result.get("suggested_pairings", []),
            )
        except Exception as e:
            print(f"Error matching product {product.name}: {e}")
            return None

    def match_products(
        self,
        products: list[Product],
        min_score: int = 0,
        max_workers: int = 3,
        limit: int | None = None,
    ) -> list[MatchResult]:
        """Match multiple products in parallel, filtering by minimum score."""
        # Filter to products with images
        products_with_images = [p for p in products if p.image_url]

        if limit:
            products_with_images = products_with_images[:limit]

        print(f"Matching {len(products_with_images)} products against style profile...")

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_product = {
                executor.submit(self.match_product, p): p
                for p in products_with_images
            }

            for i, future in enumerate(as_completed(future_to_product)):
                product = future_to_product[future]
                try:
                    result = future.result()
                    if result and result.score >= min_score:
                        results.append(result)
                        print(f"  [{i+1}/{len(products_with_images)}] {product.name}: {result.score}/10")
                    elif result:
                        print(f"  [{i+1}/{len(products_with_images)}] {product.name}: {result.score}/10 (below threshold)")
                    else:
                        print(f"  [{i+1}/{len(products_with_images)}] {product.name}: Could not analyze")
                except Exception as e:
                    print(f"  [{i+1}/{len(products_with_images)}] {product.name}: Error - {e}")

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def get_top_matches(
        self,
        products: list[Product],
        top_n: int = 10,
        min_score: int = 6,
    ) -> list[MatchResult]:
        """Get the top N matching products above a minimum score."""
        results = self.match_products(products, min_score=min_score)
        return results[:top_n]
