import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()

FIRECRAWL_API_KEY = os.environ["FIRECRAWL_API_KEY"]
OUTPUT_DIR = Path("knowledge/raw")

URLS = [
    # simprogroup.com — company website (6 pages)
    ("simpro_about",              "https://www.simprogroup.com/about-us"),
    ("simpro_solutions",          "https://www.simprogroup.com/solutions"),
    ("simpro_features",           "https://www.simprogroup.com/features"),
    ("simpro_pricing",            "https://www.simprogroup.com/pricing"),
    ("simpro_customers",          "https://www.simprogroup.com/customers"),
    ("simpro_blog",               "https://www.simprogroup.com/blog"),
    # g2.com — reviews and comparisons (4 pages)
    ("g2_simpro_reviews",         "https://www.g2.com/products/simPRO/reviews"),
    ("g2_simpro_overview",        "https://www.g2.com/products/simPRO"),
    ("g2_fsm_category",           "https://www.g2.com/categories/field-service-management"),
    ("g2_simpro_vs_servicetitan", "https://www.g2.com/compare/simpro-vs-servicetitan"),
    # capterra.com — reviews (3 pages)
    ("capterra_simpro",           "https://www.capterra.com/p/158621/simPRO/"),
    ("capterra_simpro_reviews",   "https://www.capterra.com/reviews/158621/simPRO"),
    ("capterra_fsm_comparison",   "https://www.capterra.com/field-service-management-software/"),
    # getapp.com — reviews (2 pages)
    ("getapp_simpro",             "https://www.getapp.com/operations-management-software/a/simpro/"),
    ("getapp_fsm_category",       "https://www.getapp.com/operations-management-software/field-service-management/"),
    # softwareadvice.com (1 page)
    ("softwareadvice_simpro",     "https://www.softwareadvice.com/field-service/simpro-profile/"),
    # industry / competitive context (4 pages)
    ("techradar_fsm_software",    "https://www.techradar.com/best/best-field-service-management-software"),
    ("servicetitan_about",        "https://www.servicetitan.com/about"),
    ("jobber_about",              "https://getjobber.com/about/"),
    ("fieldedge_about",           "https://fieldedge.com/about-us/"),
]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", name.lower())


def scrape_and_save(app: FirecrawlApp, name: str, url: str) -> bool:
    try:
        print(f"Scraping: {url}")
        result = app.scrape_url(url, params={"formats": ["markdown"]})
        content = result.get("markdown", "")
        if not content or len(content) < 200:
            print(f"  SKIP (too short or empty): {url}")
            return False
        filename = OUTPUT_DIR / f"{slugify(name)}.md"
        filename.write_text(f"# Source: {url}\n\n{content}", encoding="utf-8")
        print(f"  SAVED: {filename} ({len(content):,} chars)")
        return True
    except Exception as e:
        print(f"  FAILED: {url} — {e}")
        return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    saved = 0
    for name, url in URLS:
        if scrape_and_save(app, name, url):
            saved += 1
        time.sleep(1)

    print(f"\nDone: {saved}/{len(URLS)} sources saved to {OUTPUT_DIR}/")
    if saved < 15:
        print("WARNING: fewer than 15 sources saved. Add more URLs and re-run.")


if __name__ == "__main__":
    main()
