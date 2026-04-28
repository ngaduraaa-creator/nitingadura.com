#!/usr/bin/env python3
"""
rebuild_sitemap.py — Rebuild sitemap.xml from every HTML file on disk.

Includes priority + lastmod hints for AI engines.
"""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://nitingadura.com"
TODAY = dt.date.today().isoformat()

EXCLUDE_DIRS = {
    ".git", ".github", ".netlify", ".claude",
    "_includes", "scripts", "admin", "data", "research",
    "v2", "docs", "ai-citations", "ai-monitoring",
}
EXCLUDE_FILES = {
    "404.html",
    "indexnow-submit.html",
    "idx-wrapper.html",
    "idx-policy.html",  # keep crawlable but low-priority is fine — actually keep
}


def url_for(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return f"{DOMAIN}/{rel}"


def priority_for(rel: str) -> tuple[float, str]:
    """Returns (priority, changefreq)."""
    if rel == "index.html":
        return 1.0, "daily"
    if rel.startswith("nitin-gadura/"):
        return 0.95, "weekly"
    if rel in {"buy.html", "sell.html", "neighborhoods.html", "agents.html",
               "meet-the-agents.html", "contact.html", "about.html", "reviews.html"}:
        return 0.9, "weekly"
    if rel.startswith("neighborhoods/") or rel.startswith("long-island/"):
        return 0.8, "weekly"
    if rel.startswith("zip/"):
        return 0.7, "monthly"
    if rel.startswith("community/"):
        return 0.85, "weekly"
    if rel.startswith("market-reports/"):
        return 0.7, "weekly"
    if rel.startswith("blog/"):
        return 0.6, "weekly"
    if rel.startswith("services/") or rel.startswith("home-value/"):
        return 0.7, "monthly"
    if rel.startswith(("agents/",)):
        return 0.7, "monthly"
    return 0.5, "monthly"


def collect() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if rel.name in EXCLUDE_FILES:
            continue
        out.append(p)
    return sorted(out)


def main() -> int:
    pages = collect()
    print(f"Total pages: {len(pages)}")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        rel = p.relative_to(ROOT).as_posix()
        loc = url_for(p)
        prio, cf = priority_for(rel)
        try:
            mtime = dt.date.fromtimestamp(p.stat().st_mtime).isoformat()
        except Exception:
            mtime = TODAY
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        lines.append(f"    <lastmod>{mtime}</lastmod>")
        lines.append(f"    <changefreq>{cf}</changefreq>")
        lines.append(f"    <priority>{prio:.2f}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    out = "\n".join(lines) + "\n"
    (ROOT / "sitemap.xml").write_text(out, encoding="utf-8")
    print(f"Wrote sitemap.xml ({len(pages)} URLs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
