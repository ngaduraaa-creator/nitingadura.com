#!/usr/bin/env python3
"""
inject_faqpage_schema.py — Inject FAQPage JSON-LD into buyer/seller-intent pages.

Behaviour:
- For neighborhood pages (neighborhoods/**, *neighborhood*-themed pages),
  uses the neighborhood_default Q&A with {neighborhood} interpolated from the page title.
- For buy*.html / first-time-buyer*: uses buyer_default.
- For sell*.html / fsbo*/flat-fee*/short-sale*/inherited*/divorce*/senior-downsizing*: uses seller_default.
- For community/*: uses community_default.

Idempotent — replaces any existing block tagged id="ai-faq-schema".
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAQ_FILE = ROOT / "_includes" / "faq-master.json"
MARKER_ID = "ai-faq-schema"

SCRIPT_RE = re.compile(
    rf'<script type="application/ld\+json" id="{MARKER_ID}">.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)


def detect_category(rel: str) -> str:
    rel_low = rel.lower()
    if rel_low.startswith("community/"):
        return "community_default"
    if (
        rel_low.startswith("neighborhoods/")
        or "neighborhoods.html" in rel_low
        or rel_low.startswith("long-island/")
        or rel_low.startswith("zip/")
    ):
        return "neighborhood_default"
    if any(t in rel_low for t in ("buy.html", "first-time-buyer", "buyer-guide")):
        return "buyer_default"
    if any(
        t in rel_low
        for t in (
            "sell.html",
            "fsbo",
            "flat-fee",
            "short-sale",
            "inherited",
            "divorce",
            "senior-downsizing",
            "sellers-checklist",
        )
    ):
        return "seller_default"
    if any(
        t in rel_low
        for t in (
            "hindi-speaking",
            "punjabi-speaking",
            "bengali",
            "guyanese",
            "indian-community",
            "spanish-speaking",
        )
    ):
        return "community_default"
    return ""


def detect_neighborhood(html: str, fallback: str) -> str:
    m = H1_RE.search(html)
    text = m.group(1) if m else (TITLE_RE.search(html).group(1) if TITLE_RE.search(html) else "")
    text = re.sub(r"<[^>]+>", " ", text).strip()
    text = re.split(r"[|·–\-]", text, 1)[0].strip()
    if text and len(text) < 80:
        return text
    return fallback


def build_faqpage(qas: list[dict]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": qa["q"],
                "acceptedAnswer": {"@type": "Answer", "text": qa["a"]},
            }
            for qa in qas
        ],
    }
    return (
        f'<script type="application/ld+json" id="{MARKER_ID}">\n'
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + "\n</script>"
    )


def interpolate(qas: list[dict], neighborhood: str) -> list[dict]:
    out = []
    for qa in qas:
        out.append(
            {
                "q": qa["q"].replace("{neighborhood}", neighborhood),
                "a": qa["a"].replace("{neighborhood}", neighborhood),
            }
        )
    return out


def collect_targets() -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for pattern in [
        "neighborhoods/**/*.html",
        "neighborhoods/*.html",
        "neighborhoods.html",
        "community/*.html",
        "buy.html",
        "sell.html",
        "fsbo-selling-without-broker-nyc.html",
        "flat-fee-vs-full-service.html",
        "short-sale-queens-ny.html",
        "inherited-property-sale-queens.html",
        "divorce-home-sale-queens.html",
        "senior-downsizing-queens.html",
        "1031-exchange-queens.html",
        "coop-board-package-help-queens.html",
        "hindi-speaking-real-estate-agent-queens.html",
        "punjabi-speaking-real-estate-agent-queens.html",
        "first-time-buyer-guide/**/*.html",
        "sellers-checklist/**/*.html",
        "faq/*.html",
        "long-island/**/*.html",
        "zip/*.html",
    ]:
        if "*" in pattern:
            for p in ROOT.glob(pattern):
                if p.is_file() and p.suffix == ".html" and p not in seen:
                    seen.add(p)
                    out.append(p)
        else:
            p = ROOT / pattern
            if p.is_file() and p not in seen:
                seen.add(p)
                out.append(p)
    return out


def inject(html: str, block: str) -> tuple[str, str]:
    if MARKER_ID in html:
        new_html, n = SCRIPT_RE.subn(block + "\n", html, count=1)
        if n:
            return new_html, "replaced"
        return html, "noop"
    if "</head>" not in html:
        return html, "noop"
    return html.replace("</head>", f"{block}\n</head>", 1), "inserted"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    faq_data = json.loads(FAQ_FILE.read_text(encoding="utf-8"))
    targets = collect_targets()
    print(f"FAQ targets: {len(targets)}")

    counts = {"inserted": 0, "replaced": 0, "noop": 0}
    for p in targets:
        rel = p.relative_to(ROOT).as_posix()
        category = detect_category(rel)
        if not category:
            counts["noop"] += 1
            continue
        try:
            html = p.read_text(encoding="utf-8")
        except Exception:
            continue
        qas = faq_data[category]
        if category == "neighborhood_default":
            nb = detect_neighborhood(html, "Queens")
            qas = interpolate(qas, nb)
        block = build_faqpage(qas)
        new_html, action = inject(html, block)
        counts[action] += 1
        if args.apply and new_html != html:
            p.write_text(new_html, encoding="utf-8")

    print("\nResults:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"\nMode: {'APPLIED' if args.apply else 'DRY-RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
