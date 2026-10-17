#!/usr/bin/env python3
"""Check README anchors and optionally probe HTTP status of links."""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_anchors(text: str) -> set[str]:
    return set(re.findall(r'<a id="([^"]+)"></a>', text))


def extract_toc_links(text: str) -> list[str]:
    return re.findall(r"\]\(#([a-zA-Z0-9\-]+)\)", text)


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s\)\]]+", text)


def check_anchors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    anchors = extract_anchors(text)
    refs = extract_toc_links(text)
    missing = [r for r in refs if r not in anchors]
    return [f"{path.name}: TOC link #{m} has no <a id>" for m in missing]


def probe(url: str, timeout: float = 10.0) -> int | None:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "AwesomeIM-LinkCheck/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AwesomeIM-LinkCheck/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status
        except Exception:  # noqa: BLE001
            return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true", help="Probe external URLs (slow)")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    errors = []
    for name in ("README.md", "README_zh.md"):
        path = ROOT / name
        if not path.exists():
            print(f"SKIP {name} (not built yet)")
            continue
        errors.extend(check_anchors(path))

    if args.http:
        urls = []
        for name in ("README.md",):
            path = ROOT / name
            if path.exists():
                urls.extend(extract_urls(path.read_text(encoding="utf-8")))
        # unique, prefer github/arxiv/hf
        seen = []
        for u in urls:
            u = u.rstrip(".,;")
            if u not in seen:
                seen.append(u)
        for u in seen[: args.limit]:
            code = probe(u)
            if code is None or code >= 400:
                print(f"BAD {code}: {u}")
            else:
                print(f"OK  {code}: {u[:80]}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("Anchor checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
