"""Analyze style profile images to extract aesthetic preferences."""

import base64
import httpx
from pathlib import Path
from dataclasses import dataclass, field
import anthropic
import json


@dataclass
class StyleProfile:
    """Represents extracted style preferences from user images."""

    color_palette: list[str] = field(default_factory=list)
    preferred_styles: list[str] = field(default_factory=list)
    silhouettes: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    materials: list[str] = field(default_factory=list)
    aesthetics: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "color_palette": self.color_palette,
            "preferred_styles": self.preferred_styles,
            "silhouettes": self.silhouettes,
            "patterns": self.patterns,
            "materials": self.materials,
            "aesthetics": self.aesthetics,
            "avoid": self.avoid,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StyleProfile":
        return cls(**data)


class StyleAnalyzer:
    """Analyzes images to build a style profile using Claude's vision."""

    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.http_client = httpx.Client(timeout=30.0)

    def _load_image(self, path: Path) -> tuple[str, str]:
        """Load image and return base64 data and media type."""
        suffix = path.suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_types.get(suffix, "image/jpeg")

        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        return data, media_type

    def _fetch_image_url(self, url: str) -> tuple[str, str] | None:
        """Fetch image from URL and return base64 data and media type."""
        try:
            response = self.http_client.get(url, follow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "image/jpeg")
            if ";" in content_type:
                content_type = content_type.split(";")[0]

            data = base64.standard_b64encode(response.content).decode("utf-8")
            return data, content_type
        except Exception as e:
            print(f"Error fetching image {url}: {e}")
            return None

    def analyze_style_images(self, image_paths: list[Path]) -> StyleProfile:
        """Analyze multiple style reference images to build a profile."""
        if not image_paths:
            raise ValueError("No images provided")

        # Build content with all images
        content = []
        for path in image_paths[:10]:  # Limit to 10 images
            if not path.exists():
                print(f"Skipping missing image: {path}")
                continue

            data, media_type = self._load_image(path)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": data,
                },
            })

        if not content:
            raise ValueError("No valid images found")

        content.append({
            "type": "text",
            "text": """Analyze these style reference images to create a comprehensive style profile.
These images represent the user's personal style preferences - they may be outfit photos,
fashion inspiration, or items they own and love.

Extract and return a JSON object with these fields:
{
    "color_palette": ["list of preferred colors, be specific (e.g., 'warm beige', 'navy blue', 'forest green')"],
    "preferred_styles": ["list of style categories (e.g., 'French minimalist', 'bohemian', 'classic tailored')"],
    "silhouettes": ["preferred fits and shapes (e.g., 'high-waisted', 'oversized blazers', 'midi length')"],
    "patterns": ["preferred patterns (e.g., 'subtle stripes', 'florals', 'solid colors')"],
    "materials": ["preferred fabrics (e.g., 'linen', 'cashmere', 'silk')"],
    "aesthetics": ["overall aesthetic descriptors (e.g., 'effortless chic', 'understated elegance')"],
    "avoid": ["styles/elements that seem absent or contrary to the aesthetic"],
    "summary": "A 2-3 sentence description of the overall style identity"
}

Return ONLY the JSON object, no other text."""
        })

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": content}]
        )

        # Parse response
        response_text = response.content[0].text
        # Clean up potential markdown formatting
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        try:
            data = json.loads(response_text.strip())
            return StyleProfile.from_dict(data)
        except json.JSONDecodeError as e:
            print(f"Error parsing style profile: {e}")
            print(f"Response was: {response_text}")
            return StyleProfile(summary="Could not parse style profile")

    def save_profile(self, profile: StyleProfile, path: Path):
        """Save style profile to JSON file."""
        with open(path, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def load_profile(self, path: Path) -> StyleProfile:
        """Load style profile from JSON file."""
        with open(path) as f:
            return StyleProfile.from_dict(json.load(f))
