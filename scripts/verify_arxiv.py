#!/usr/bin/env python3
"""Batch-verify arXiv IDs via the public API; report title mismatches."""
from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = ROOT / "data" / "entries"
NS = {"a": "http://www.w3.org/2005/Atom"}


def extract_id(url: str) -> str | None:
    m = re.search(r"(\d{4}\.\d{4,5})", url)
    return m.group(1) if m else None


def collect_arxiv() -> dict[str, list[dict]]:
    """Map arxiv_id -> list of entries referencing it."""
    mapping: dict[str, list[dict]] = {}
    for path in sorted(ENTRIES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        items = data if isinstance(data, list) else data.get("entries", [])
        for e in items:
            url = (e.get("links") or {}).get("arxiv")
            if not url:
                continue
            aid = extract_id(url)
            if not aid:
                print(f"WARN: cannot parse arxiv from {e.get('id')}: {url}")
                continue
            mapping.setdefault(aid, []).append(e)
    return mapping


def fetch_batch(ids: list[str]) -> dict[str, str]:
    """Return arxiv_id -> title."""
    q = ",".join(ids)
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(q)}&max_results={len(ids)}"
    req = urllib.request.Request(url, headers={"User-Agent": "AwesomeInteractiveModel/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        xml = resp.read()
    root = ET.fromstring(xml)
    out = {}
    for entry in root.findall("a:entry", NS):
        id_url = entry.findtext("a:id", default="", namespaces=NS)
        title = " ".join((entry.findtext("a:title", default="", namespaces=NS) or "").split())
        aid = extract_id(id_url)
        if aid:
            out[aid] = title
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--fix", action="store_true", help="Write verified titles into YAML notes")
    args = parser.parse_args()

    mapping = collect_arxiv()
    ids = sorted(mapping.keys())
    print(f"Found {len(ids)} unique arXiv IDs across entries")

    missing = []
    for i in range(0, len(ids), args.batch_size):
        batch = ids[i : i + args.batch_size]
        try:
            titles = fetch_batch(batch)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR fetching batch {batch[0]}…: {exc}", file=sys.stderr)
            time.sleep(args.sleep * 2)
            continue
        for aid in batch:
            if aid not in titles:
                missing.append(aid)
                print(f"MISSING: {aid} (used by {[e.get('id') for e in mapping[aid]]})")
            else:
                # soft title check vs first entry title
                for e in mapping[aid]:
                    et = (e.get("title") or "").strip()
                    at = titles[aid]
                    # only flag if completely different start
                    if et and at and et.lower()[:20] not in at.lower() and at.lower()[:20] not in et.lower():
                        print(f"TITLE DIFF {aid}: entry={et[:80]!r} arxiv={at[:80]!r}")
        time.sleep(args.sleep)

    print(f"Done. Missing IDs: {len(missing)}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
