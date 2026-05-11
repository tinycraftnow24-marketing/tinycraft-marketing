"""
Liest marketing.md aus C:/Projekte/nebenprojekte und schreibt posts.json
Ausfuehren: python scripts/convert_marketing.py
"""
import json
import re
from pathlib import Path

SOURCE_BASE = Path(r"C:\Projekte\nebenprojekte\Notion")
TARGET_BASE = Path(r"C:\Projekte\tinycraft-marketing\content")

PRODUCT_MAP = {
    "habit-tracker":    "notion-habit-tracker",
    "weekly-planner":   "notion-weekly-planner",
    "personal-finance": "notion-personal-finance",
    "job-tracker":      "notion-job-tracker",
    "product-roadmap":  "notion-product-roadmap",
    "book-tracker":     "notion-book-tracker",
}

def extract_reddit_posts(md_text: str, product_id: str) -> list:
    posts = []
    reddit_match = re.search(r'## r/Notion.*?(?=## |\Z)', md_text, re.DOTALL)
    if not reddit_match:
        return posts
    block = reddit_match.group(0)

    title_match = re.search(r'\*\*Post-Titel:\*\*\s*\n```\n(.*?)\n```', block, re.DOTALL)
    body_match  = re.search(r'\*\*Body:\*\*\s*\n```\n(.*?)\n```', block, re.DOTALL)

    if title_match and body_match:
        posts.append({
            "id": f"{product_id}-r-01",
            "platform": "reddit",
            "subreddit": "r/Notion",
            "title": title_match.group(1).strip(),
            "body": body_match.group(1).strip(),
            "status": "unused",
            "score": None,
            "posted_at": None,
            "last_image_used": None
        })
    return posts

def extract_pinterest_posts(md_text: str, product_id: str) -> list:
    posts = []
    pinterest_match = re.search(r'## Pinterest.*?(?=## |\Z)', md_text, re.DOTALL)
    if not pinterest_match:
        return posts
    block = pinterest_match.group(0)

    pin_blocks = re.findall(
        r'\*\*Pin \d.*?\*\*.*?- Titel: `(.*?)`.*?- Beschreibung: `(.*?)`',
        block, re.DOTALL
    )
    for i, (title, desc) in enumerate(pin_blocks, 1):
        posts.append({
            "id": f"{product_id}-p-0{i}",
            "platform": "pinterest",
            "title": title.strip(),
            "description": desc.strip(),
            "status": "unused",
            "score": None,
            "posted_at": None,
            "last_image_used": None
        })
    return posts

def init_assets_json(product_id: str) -> dict:
    return {
        "product_id": product_id,
        "images": [],
        "last_updated": None
    }

def main():
    for source_folder, product_id in PRODUCT_MAP.items():
        md_path = SOURCE_BASE / source_folder / "marketing.md"
        target_dir = TARGET_BASE / product_id

        if not md_path.exists():
            print(f"SKIP: {md_path} nicht gefunden")
            continue

        md_text = md_path.read_text(encoding="utf-8")
        reddit_posts    = extract_reddit_posts(md_text, product_id)
        pinterest_posts = extract_pinterest_posts(md_text, product_id)
        all_posts       = reddit_posts + pinterest_posts

        posts_path = target_dir / "posts.json"
        posts_path.write_text(json.dumps(all_posts, indent=2, ensure_ascii=False), encoding="utf-8")

        assets_path = target_dir / "assets.json"
        if not assets_path.exists():
            assets_path.write_text(json.dumps(init_assets_json(product_id), indent=2), encoding="utf-8")

        print(f"OK: {product_id} — {len(reddit_posts)} Reddit + {len(pinterest_posts)} Pinterest Posts")

if __name__ == "__main__":
    main()
