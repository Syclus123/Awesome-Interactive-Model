#!/usr/bin/env python3
"""Build bilingual READMEs from YAML data + templates."""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRIES_DIR = DATA / "entries"
TEMPLATES = ROOT / "templates"

STATUS_ICON = {
    "open_weights": "🔓",
    "code_only": "🧩",
    "closed": "🔒",
    "paper_only": "📄",
}

STATUS_LABEL = {
    "en": {
        "open_weights": "open weights",
        "code_only": "code / runtime",
        "closed": "closed API / product",
        "paper_only": "paper only / unreleased",
    },
    "zh": {
        "open_weights": "开放权重",
        "code_only": "代码 / 运行时",
        "closed": "闭源 API / 产品",
        "paper_only": "仅论文 / 未发布",
    },
}

REQUIRED = {"id", "name", "title", "date", "status", "sections"}

# Fields rendered verbatim into the English README.
EN_FIELDS = ("name", "title", "venue", "note_en")
CJK_RE = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def badge(label: str, color: str, url: str) -> str:
    safe = str(url).replace(" ", "%20")
    text = label.replace("-", "--").replace("_", "__")
    return f"[![{label}](https://img.shields.io/badge/{text}-{color}.svg)]({safe})"


def arxiv_badge(url: str) -> str:
    m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?", url)
    aid = m.group(1) if m else "Paper"
    return badge(f"arXiv-{aid}", "b31b1b", url)


def link_badges(links: dict | None) -> str:
    if not links:
        return ""
    parts = []
    if links.get("arxiv"):
        parts.append(arxiv_badge(links["arxiv"]))
    if links.get("web"):
        parts.append(badge("Website-Link", "blue", links["web"]))
    if links.get("code"):
        parts.append(badge("Code-GitHub", "green", links["code"]))
    if links.get("hf"):
        parts.append(badge("HF-Model", "yellow", links["hf"]))
    if links.get("blog"):
        parts.append(badge("Blog-Link", "orange", links["blog"]))
    if links.get("docs"):
        parts.append(badge("Docs-Link", "lightgrey", links["docs"]))
    if links.get("data"):
        parts.append(badge("Data-Link", "9b59b6", links["data"]))
    return " ".join(parts)


def format_date(date: str | None) -> str:
    if not date:
        return ""
    date = str(date)
    if re.fullmatch(r"\d{4}-\d{2}", date):
        return date
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        return date[:7]
    if re.fullmatch(r"\d{4}", date):
        return date
    return date


def sort_key(entry: dict) -> tuple:
    d = str(entry.get("date") or "0000-00")
    # reverse chronological
    return (d, entry.get("name") or "")


def validate_entry(e: dict, path: Path, section_ids: set[str]) -> list[str]:
    errs = []
    missing = REQUIRED - set(e.keys())
    if missing:
        errs.append(f"{path.name}/{e.get('id','?')}: missing {sorted(missing)}")
    if e.get("status") not in STATUS_ICON:
        errs.append(f"{path.name}/{e.get('id','?')}: bad status {e.get('status')}")
    for s in e.get("sections") or []:
        if s not in section_ids:
            errs.append(f"{path.name}/{e.get('id','?')}: unknown section '{s}'")
    for field in EN_FIELDS:
        if CJK_RE.search(str(e.get(field) or "")):
            errs.append(f"{path.name}/{e.get('id','?')}: Chinese text in English field '{field}'")
    return errs


def collect_section_ids(sections: list) -> set[str]:
    ids = set()
    for s in sections:
        ids.add(s["id"])
        for c in s.get("children") or []:
            ids.add(c["id"])
    return ids


def leaf_sections(sections: list) -> list[dict]:
    """Flatten to ordered leaf sections (children if present, else parent)."""
    leaves = []
    for s in sections:
        kids = s.get("children") or []
        if kids:
            for c in kids:
                leaves.append({**c, "parent": s})
        else:
            leaves.append({**s, "parent": None})
    return leaves


def render_entry(e: dict, lang: str) -> str:
    star = "[⭐️] " if e.get("star") else ""
    date = format_date(e.get("date"))
    venue = e.get("venue") or ""
    prefix_bits = []
    if date:
        prefix_bits.append(date)
    if venue:
        prefix_bits.append(venue)
    prefix = f"**[{'] ['.join(prefix_bits)}]** " if prefix_bits else ""
    status = STATUS_ICON.get(e.get("status"), "")
    badges = link_badges(e.get("links"))
    note = e.get(f"note_{lang}") or e.get("note_en") or ""
    line = f"- {star}{prefix}**{e['name']}** - {e['title']}."
    if badges:
        line += f" {badges}"
    if status:
        line += f" {status}"
    if note:
        line += f"\n  - _{note}_"
    return line


def render_section_block(section: dict, by_section: dict, lang: str) -> str:
    lines = []
    sid = section["id"]
    title = section.get(f"title_{lang}") or section.get("title_en")
    emoji = ""
    parent = section.get("parent")
    # top-level emoji only when rendering parent heading separately
    intro = section.get(f"intro_{lang}") or section.get("intro_en") or ""
    # For leaf under parent: use ### ; for top without children handled elsewhere
    depth = 3 if parent else 2
    hashes = "#" * depth
    lines.append(f'<a id="{section["anchor"]}"></a>')
    lines.append(f"{hashes} {title}")
    lines.append("")
    if intro and not parent:
        lines.append(intro)
        lines.append("")
    entries = by_section.get(sid, [])
    entries = sorted(entries, key=sort_key, reverse=True)
    if not entries:
        empty = "_Coming soon._" if lang == "en" else "_待补充。_"
        lines.append(empty)
        lines.append("")
        return "\n".join(lines)
    for e in entries:
        lines.append(render_entry(e, lang))
    lines.append("")
    return "\n".join(lines)


def render_all_sections(sections: list, by_section: dict, lang: str) -> str:
    parts = []
    for s in sections:
        kids = s.get("children") or []
        emoji = s.get("emoji", "")
        title = s.get(f"title_{lang}") or s.get("title_en")
        intro = s.get(f"intro_{lang}") or s.get("intro_en") or ""
        parts.append(f'<a id="{s["anchor"]}"></a>')
        parts.append(f"## {emoji} {title}".strip())
        parts.append("")
        if intro:
            parts.append(intro)
            parts.append("")
        if kids:
            for c in kids:
                parts.append(render_section_block({**c, "parent": s}, by_section, lang))
        else:
            # entries directly on parent
            entries = sorted(by_section.get(s["id"], []), key=sort_key, reverse=True)
            if entries:
                for e in entries:
                    parts.append(render_entry(e, lang))
                parts.append("")
            else:
                parts.append("_Coming soon._" if lang == "en" else "_待补充。_")
                parts.append("")
    return "\n".join(parts)


def render_toc(sections: list, lang: str) -> str:
    lines = []
    for s in sections:
        emoji = s.get("emoji", "")
        title = s.get(f"title_{lang}") or s.get("title_en")
        lines.append(f"- {emoji} [{title}](#{s['anchor']})".strip())
        for c in s.get("children") or []:
            ct = c.get(f"title_{lang}") or c.get("title_en")
            lines.append(f"  - [{ct}](#{c['anchor']})")
    return "\n".join(lines)


def stats_text(entries: list, lang: str, as_of: str) -> str:
    n = len(entries)
    by_status = defaultdict(int)
    for e in entries:
        by_status[e.get("status", "?")] += 1
    if lang == "en":
        bits = ", ".join(
            f"{STATUS_ICON[k]} {STATUS_LABEL['en'][k]}: {by_status[k]}"
            for k in STATUS_ICON
            if by_status[k]
        )
        return f"<strong>{n} curated entries</strong> ({bits}). Verified sources as of {as_of}."
    bits = "，".join(
        f"{STATUS_ICON[k]} {STATUS_LABEL['zh'][k]}：{by_status[k]}"
        for k in STATUS_ICON
        if by_status[k]
    )
    return f"<strong>收录 {n} 条</strong>（{bits}）。公开资料核验截至 {as_of}。"


def load_all_entries(section_ids: set[str]) -> tuple[list[dict], list[str]]:
    entries = []
    errors = []
    seen = {}
    for path in sorted(ENTRIES_DIR.glob("*.yaml")):
        data = load_yaml(path)
        items = data if isinstance(data, list) else data.get("entries", [])
        for e in items:
            if not isinstance(e, dict):
                continue
            errors.extend(validate_entry(e, path, section_ids))
            eid = e.get("id")
            if eid in seen:
                errors.append(f"duplicate id '{eid}' in {path.name} and {seen[eid]}")
            else:
                seen[eid] = path.name
            entries.append(e)
    return entries, errors


def build(lang: str, sections: list, entries: list, as_of: str) -> str:
    by_section: dict[str, list] = defaultdict(list)
    for e in entries:
        for sid in e.get("sections") or []:
            by_section[sid].append(e)

    tpl_name = f"README.{'en' if lang == 'en' else 'zh'}.md"
    template = (TEMPLATES / tpl_name).read_text(encoding="utf-8")

    replacements = {
        "{{AUTO_TOC}}": render_toc(sections, lang),
        "{{AUTO_STATS}}": stats_text(entries, lang, as_of),
        "{{AUTO_SECTIONS}}": render_all_sections(sections, by_section, lang),
        "{{AUTO_ENTRY_COUNT}}": str(len(entries)),
    }
    out = template
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    meta = load_yaml(DATA / "sections.yaml")
    sections = meta["sections"]
    as_of = (meta.get("meta") or {}).get("as_of") or "2026-10-19"
    section_ids = collect_section_ids(sections)
    entries, errors = load_all_entries(section_ids)

    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        # unknown section is warning-level; everything else is a hard schema error
        hard = [e for e in errors if "unknown section" not in e]
        if hard:
            return 1

    if args.check_only:
        print(f"OK: {len(entries)} entries, {len(section_ids)} section ids")
        if errors:
            print(f"Warnings: {len(errors)}")
        return 0

    for lang, out_name in (("en", "README.md"), ("zh", "README_zh.md")):
        text = build(lang, sections, entries, as_of)
        (ROOT / out_name).write_text(text, encoding="utf-8")
        print(f"Wrote {out_name} ({len(text)} chars, {len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
