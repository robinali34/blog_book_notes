#!/usr/bin/env python3
"""Fetch Hanfeizi 55 chapters (simplified) from ctext.org into JSON."""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/data/hanfeizi-jing.json"
INDEX_URL = "https://ctext.org/hanfeizi/zhs"

# Traditional ordinal suffix for display titles
ORDINALS = "一二三四五六七八九十"


def ordinal(n: int) -> str:
    if n <= 10:
        return ORDINALS[n - 1]
    if n < 20:
        return "十" + ORDINALS[n - 11]
    tens, ones = divmod(n, 10)
    s = ORDINALS[tens - 1] + "十"
    if ones:
        s += ORDINALS[ones - 1]
    return s


def fetch_index() -> list[tuple[str, str, str]]:
    req = urllib.request.Request(INDEX_URL, headers={"User-Agent": "blog-book-notes/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
    rows = re.findall(r'href="(hanfeizi/([^"]+)/zhs)"[^>]*>([^<]+)</a>', html)
    if len(rows) != 55:
        raise RuntimeError(f"expected 55 chapters, got {len(rows)}")
    return [(slug, slug_part, title.strip()) for slug, slug_part, title in rows]


def fetch_chapter_text(slug: str) -> str:
    url = f"https://ctext.org/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": "blog-book-notes/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
    parts = re.findall(r'<td class="ctext"[^>]*>(.*?)</td>', html, re.S)
    if not parts:
        raise RuntimeError(f"no ctext body in {url}")
    chunks: list[str] = []
    for part in parts:
        part = re.sub(r"<br\s*/?>", "\n", part)
        part = re.sub(r"<[^>]+>", "", part)
        part = part.replace("&nbsp;", " ").strip()
        if part:
            chunks.append(part)
    text = "\n\n".join(chunks)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def main() -> None:
    chapters_meta = fetch_index()
    entries: list[dict] = []
    for i, (slug, slug_part, title) in enumerate(chapters_meta, 1):
        text = fetch_chapter_text(slug)
        entries.append(
            {
                "id": i,
                "slug": slug_part,
                "title": title,
                "full_title": f"{title}第{ordinal(i)}",
                "text": text,
            }
        )
        print(f"{i:2d} {title} ({len(text)} chars)")
        time.sleep(0.15)

    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} chapters to {OUT}")


if __name__ == "__main__":
    main()
