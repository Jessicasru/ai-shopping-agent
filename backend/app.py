"""Flask API for the AI Personal Shopping Agent."""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path so we can import from src/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.vision.style_analyzer import StyleAnalyzer, StyleProfile
from src.vision.product_matcher import ProductMatcher, MatchResult
from src.models.product import Product
from backend.models import init_db, get_all_products

app = Flask(__name__)
CORS(app)

# Initialize database tables on startup
if os.environ.get("DATABASE_URL"):
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database init skipped: {e}")

DATA_DIR = PROJECT_ROOT / "data"
PROFILES_DIR = DATA_DIR / "style_profiles"
SCRAPED_DIR = DATA_DIR / "scraped_items"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


# ── GET /api/products ──────────────────────────────────────────────
@app.route("/api/products", methods=["GET"])
def get_products():
    """Return products from database, falling back to JSON file."""
    if os.environ.get("DATABASE_URL"):
        try:
            products = get_all_products()
            return jsonify({
                "total_products": len(products),
                "products": products,
            })
        except Exception as e:
            print(f"Database read failed, falling back to JSON: {e}")

    products_file = SCRAPED_DIR / "latest_arrivals.json"
    if not products_file.exists():
        return jsonify({"error": "No products found. Run scrapers first."}), 404

    with open(products_file) as f:
        data = json.load(f)

    return jsonify(data)


# ── GET /api/recommendations ──────────────────────────────────────
@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """Return cached product recommendations."""
    recs_file = SCRAPED_DIR / "recommendations.json"
    if not recs_file.exists():
        return jsonify({"error": "No recommendations found. Run matching first."}), 404

    with open(recs_file) as f:
        data = json.load(f)

    return jsonify(data)


# ── GET /api/profile ──────────────────────────────────────────────
@app.route("/api/profile", methods=["GET"])
def get_profile():
    """Return the current style profile if one exists."""
    profile_file = PROFILES_DIR / "profile.json"
    if not profile_file.exists():
        return jsonify({"error": "No style profile found."}), 404

    with open(profile_file) as f:
        data = json.load(f)

    return jsonify(data)


# ── POST /api/analyze-style ──────────────────────────────────────
@app.route("/api/analyze-style", methods=["POST"])
def analyze_style():
    """Receive images, analyze style, return profile JSON."""
    if "images" not in request.files:
        return jsonify({"error": "No images provided"}), 400

    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "No images provided"}), 400

    # Save uploaded files
    session_id = str(uuid.uuid4())[:8]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for f in files:
        if f.filename and allowed_file(f.filename):
            filename = f"{len(saved_paths):02d}_{Path(f.filename).name}"
            filepath = session_dir / filename
            f.save(filepath)
            saved_paths.append(filepath)

    if not saved_paths:
        return jsonify({"error": "No valid image files provided"}), 400

    try:
        analyzer = StyleAnalyzer()
        profile = analyzer.analyze_style_images(saved_paths)

        # Save profile
        analyzer.save_profile(profile, PROFILES_DIR / "profile.json")

        return jsonify({
            "profile": profile.to_dict(),
            "images_analyzed": len(saved_paths),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── POST /api/find-matches ───────────────────────────────────────
@app.route("/api/find-matches", methods=["POST"])
def find_matches():
    """Match products against a style profile."""
    # Load style profile
    profile_file = PROFILES_DIR / "profile.json"
    if not profile_file.exists():
        return jsonify({"error": "No style profile found. Analyze style first."}), 400

    with open(profile_file) as f:
        profile = StyleProfile.from_dict(json.load(f))

    # Load products from database, falling back to JSON
    products_data = None
    if os.environ.get("DATABASE_URL"):
        try:
            products_data = get_all_products()
        except Exception as e:
            print(f"Database read failed, falling back to JSON: {e}")

    if products_data is not None:
        products = [Product(**p) for p in products_data]
    else:
        products_file = SCRAPED_DIR / "latest_arrivals.json"
        if not products_file.exists():
            return jsonify({"error": "No products found. Run scrapers first."}), 400
        with open(products_file) as f:
            raw = json.load(f)
        products = [Product(**p) for p in raw["products"]]

    # Get parameters from request body
    body = request.get_json(silent=True) or {}
    limit = body.get("limit", 25)
    min_score = body.get("min_score", 6)

    try:
        matcher = ProductMatcher(profile)
        results = matcher.match_products(
            products, min_score=min_score, limit=limit
        )

        recommendations = {
            "generated_at": datetime.now().isoformat(),
            "style_summary": profile.summary,
            "products_analyzed": min(limit, len(products)),
            "matches_found": len(results),
            "recommendations": [r.to_dict() for r in results],
        }

        # Cache results
        with open(SCRAPED_DIR / "recommendations.json", "w") as f:
            json.dump(recommendations, f, indent=2)

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Health check ─────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

print("All routes registered successfully!")
print("Routes:", [str(rule) for rule in app.url_map.iter_rules()])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
