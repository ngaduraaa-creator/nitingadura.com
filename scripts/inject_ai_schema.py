#!/usr/bin/env python3
"""
inject_ai_schema.py — Inject the Nitin-centric AI master schema across all pages.

Idempotent. Replaces any existing block with id="ai-master-schema".
Does NOT touch existing JSON-LD blocks (they may have unique BreadcrumbList,
ItemList, Product, etc. — those are kept).
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILE = ROOT / "_includes" / "ai-master-schema.html"
MARKER_ID = "ai-master-schema"

GLOBS = [
    "*.html",
    "**/*.html",
]
SKIP_PARTS = {"_includes", "scripts", ".git", ".github", "_site"}
SKIP_FILES = {"404.html"}

SCRIPT_RE = re.compile(
    rf'<script type="application/ld\+json" id="{MARKER_ID}">.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)


def collect():
    seen = set()
    out = []
    for pat in GLOBS:
        for p in ROOT.glob(pat):
            if not p.is_file() or p.suffix != ".html":
                continue
            if p.name in SKIP_FILES:
                continue
            if any(part in SKIP_PARTS for part in p.relative_to(ROOT).parts):
                continue
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
    return out


def inject(html, block):
    if MARKER_ID in html:
        new, n = SCRIPT_RE.subn(block + "\n", html, count=1)
        if n:
            return new, "replaced"
        return html, "noop"
    if "</head>" not in html:
        return html, "noop"
    return html.replace("</head>", f"{block}\n</head>", 1), "inserted"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    block = SCHEMA_FILE.read_text(encoding="utf-8").rstrip()
    pages = collect()
    print(f"Targets: {len(pages)}")
    counts = {"inserted": 0, "replaced": 0, "noop": 0}
    for p in pages:
        try:
            html = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new_html, action = inject(html, block)
        counts[action] += 1
        if args.apply and new_html != html:
            p.write_text(new_html, encoding="utf-8")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"\nMode: {'APPLIED' if args.apply else 'DRY-RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
