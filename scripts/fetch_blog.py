from __future__ import annotations

from pathlib import Path
import datetime as dt
import time
import requests
import feedparser
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

FEEDS_YML = DATA / "feeds.yml"
OUTPUT_SNIPPET = DATA / "blog_snippet.md"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalize_entries(entries: list[dict], source_name: str) -> list[dict]:
    out: list[dict] = []
    for e in entries:
        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()

        # prefer published/updated if present
        published_parsed = e.get("published_parsed") or e.get("updated_parsed")
        published = ""
        if published_parsed:
            try:
                published = time.strftime("%Y-%m-%d", published_parsed)
            except Exception:
                published = ""

        if title and link:
            out.append(
                {
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": source_name,
                }
            )
    return out


def fetch_feed(url: str, source_name: str, timeout: int = 20) -> list[dict]:
    # Some RSS endpoints block unknown clients; use a friendly UA.
    headers = {
        "User-Agent": "Mozilla/5.0 (GitHub Profile README Bot; +https://github.com/sargisheiser)"
    }

    # Fetch raw content to reduce parser issues and get better errors.
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    parsed = feedparser.parse(resp.text)
    if getattr(parsed, "bozo", 0):
        # bozo indicates parse issues; sometimes still has entries, so don't hard-fail
        pass

    entries = getattr(parsed, "entries", []) or []
    return normalize_entries(entries, source_name)


def dedupe_keep_order(items: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for it in items:
        key = it.get("link")
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def render_snippet(entries: list[dict], max_posts: int, fallback_message: str) -> str:
    if not entries:
        return f"- {fallback_message}"

    entries = entries[:max_posts]

    # Compact + recruiter-friendly. No emoji spam.
    lines = []
    for e in entries:
        date = e.get("published", "")
        title = e.get("title", "Untitled")
        link = e.get("link", "")
        source = e.get("source", "")

        # Format: - YYYY-MM-DD · [Title](link) (source)
        prefix = f"{date} · " if date else ""
        suffix = f" ({source})" if source else ""
        lines.append(f"- {prefix}[{title}]({link}){suffix}")

    return "\n".join(lines)


def main():
    cfg = load_yaml(FEEDS_YML)

    feeds = cfg.get("feeds", []) or []
    settings = cfg.get("settings", {}) or {}

    max_posts = int(settings.get("max_posts", 5))
    fallback_message = settings.get("fallback_message", "Writing in progress — technical notes coming soon.")

    all_entries: list[dict] = []
    errors: list[str] = []

    for f in feeds:
        name = (f.get("name") or "feed").strip()
        url = (f.get("url") or "").strip()
        if not url:
            continue

        try:
            entries = fetch_feed(url, source_name=name)
            all_entries.extend(entries)
        except Exception as ex:
            errors.append(f"{name}: {ex.__class__.__name__}")

    all_entries = dedupe_keep_order(all_entries)

    # Sort by date if available; keep stable order otherwise.
    def sort_key(e: dict):
        return e.get("published") or "0000-00-00"

    all_entries.sort(key=sort_key, reverse=True)

    snippet = render_snippet(all_entries, max_posts=max_posts, fallback_message=fallback_message)

    stamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    meta = f"<!-- auto-generated: fetch_blog.py | {stamp} -->\n"
    if errors:
        # We don't fail the pipeline; we annotate for debugging.
        meta += f"<!-- feed errors (non-blocking): {', '.join(errors)} -->\n"

    OUTPUT_SNIPPET.write_text(meta + snippet + "\n", encoding="utf-8")
    print(f"✅ Wrote {OUTPUT_SNIPPET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
