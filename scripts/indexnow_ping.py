#!/usr/bin/env python3
"""
indexnow_ping.py — Submit URLs to IndexNow (Bing, Yandex, Naver, Seznam, Yep).
ChatGPT, Grok, and Copilot all use Bing's index — IndexNow is the fastest path
to recrawl after content changes.

Setup (one-time):
1. Generate a key: a 32-char hex string. Save to scripts/indexnow.key
2. Place the key file at https://nitingadura.com/<key>.txt with the same content
   (this is the Bing IndexNow ownership-verification handshake).
3. Run this script daily, or after every batch of edits.

Usage:
    python3 scripts/indexnow_ping.py                       # ping changed-since-yesterday
    python3 scripts/indexnow_ping.py --all                 # ping every URL in sitemap
    python3 scripts/indexnow_ping.py --since 2026-04-20    # ping URLs modified since a date
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "scripts" / "indexnow.key"
HOST = "nitingadura.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def load_key() -> str:
    if not KEY_FILE.exists():
        print(f"ERROR: {KEY_FILE} not found. Generate a 32-char hex key:")
        print('  python3 -c "import secrets; print(secrets.token_hex(16))" > scripts/indexnow.key')
        print(f"Then place the same contents at https://{HOST}/<key>.txt for verification.")
        sys.exit(1)
    return KEY_FILE.read_text(encoding="utf-8").strip()


def parse_sitemap(path: Path) -> list[tuple[str, dt.date]]:
    """Returns [(url, lastmod_date)]."""
    out: list[tuple[str, dt.date]] = []
    if not path.exists():
        return out
    tree = ET.parse(path)
    root = tree.getroot()
    for url_node in root.findall("sm:url", NS):
        loc = url_node.findtext("sm:loc", default="", namespaces=NS).strip()
        lm = url_node.findtext("sm:lastmod", default="", namespaces=NS).strip()
        if not loc:
            continue
        try:
            d = dt.date.fromisoformat(lm[:10]) if lm else dt.date.today()
        except ValueError:
            d = dt.date.today()
        out.append((loc, d))
    return out


def collect_urls(since: dt.date | None, all_flag: bool) -> list[str]:
    sitemap = ROOT / "sitemap.xml"
    blog_sitemap = ROOT / "blog-sitemap.xml"
    entries = parse_sitemap(sitemap) + parse_sitemap(blog_sitemap)
    if all_flag:
        return [u for u, _ in entries]
    cutoff = since or (dt.date.today() - dt.timedelta(days=2))
    return [u for u, d in entries if d >= cutoff]


def submit(key: str, urls: list[str]) -> None:
    # IndexNow accepts up to 10,000 URLs per request.
    BATCH = 9000
    for i in range(0, len(urls), BATCH):
        batch = urls[i : i + BATCH]
        payload = {
            "host": HOST,
            "key": key,
            "keyLocation": f"https://{HOST}/{key}.txt",
            "urlList": batch,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            ENDPOINT,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"[indexnow] batch {i // BATCH + 1}: {len(batch)} URLs → HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            print(f"[indexnow] HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}")
        except Exception as e:
            print(f"[indexnow] error: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="submit every URL in sitemap")
    ap.add_argument("--since", help="YYYY-MM-DD; submit URLs with lastmod >= this date")
    args = ap.parse_args()
    since = dt.date.fromisoformat(args.since) if args.since else None
    key = load_key()
    urls = collect_urls(since, args.all)
    print(f"URLs to submit: {len(urls)}")
    if urls:
        submit(key, urls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
