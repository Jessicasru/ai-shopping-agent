#!/usr/bin/env python3
"""Analyze style profile images and save the profile."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.vision import StyleAnalyzer

load_dotenv()


def main():
    style_dir = Path("data/style_profiles")

    # Find all images in style_profiles directory
    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    image_paths = [
        p for p in style_dir.iterdir()
        if p.suffix.lower() in image_extensions
    ]

    if not image_paths:
        print(f"No images found in {style_dir}/")
        print("Please add your style reference images (outfit photos, inspiration, etc.)")
        print("Supported formats: JPG, PNG, WebP, GIF")
        sys.exit(1)

    print(f"Found {len(image_paths)} style reference images:")
    for p in image_paths:
        print(f"  - {p.name}")

    print("\nAnalyzing your style...")
    analyzer = StyleAnalyzer()
    profile = analyzer.analyze_style_images(image_paths)

    # Save profile
    profile_path = style_dir / "profile.json"
    analyzer.save_profile(profile, profile_path)

    print("\n" + "=" * 60)
    print("YOUR STYLE PROFILE")
    print("=" * 60)

    print(f"\n{profile.summary}\n")

    if profile.color_palette:
        print(f"Colors: {', '.join(profile.color_palette)}")
    if profile.preferred_styles:
        print(f"Styles: {', '.join(profile.preferred_styles)}")
    if profile.silhouettes:
        print(f"Silhouettes: {', '.join(profile.silhouettes)}")
    if profile.patterns:
        print(f"Patterns: {', '.join(profile.patterns)}")
    if profile.materials:
        print(f"Materials: {', '.join(profile.materials)}")
    if profile.aesthetics:
        print(f"Aesthetic: {', '.join(profile.aesthetics)}")
    if profile.avoid:
        print(f"Avoids: {', '.join(profile.avoid)}")

    print(f"\nProfile saved to: {profile_path}")


if __name__ == "__main__":
    main()
