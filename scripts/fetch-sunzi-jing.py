#!/usr/bin/env python3
"""Fetch Sunzi Bingfa 13 chapters from Wikisource into JSON (simplified)."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

try:
    import opencc
except ImportError:
    opencc = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/data/sunzi-jing.json"
WIKI_URL = "https://zh.wikisource.org/wiki/%E5%AD%AB%E5%AD%90%E5%85%B5%E6%B3%95"

CHAPTERS = [
    (1, "始计", "始計第一"),
    (2, "作战", "作戰第二"),
    (3, "谋攻", "謀攻第三"),
    (4, "军形", "軍形第四"),
    (5, "兵势", "兵勢第五"),
    (6, "虚实", "虛實第六"),
    (7, "军争", "軍爭第七"),
    (8, "九变", "九變第八"),
    (9, "行军", "行軍第九"),
    (10, "地形", "地形第十"),
    (11, "九地", "九地第十一"),
    (12, "火攻", "火攻第十二"),
    (13, "用间", "用間第十三"),
]


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


def clean_wiki_text(text: str) -> str:
    text = re.sub(r"\[編輯\]\([^)]+\)", "", text)
    text = re.sub(r"一作「[^」]+」", "", text)
    text = re.sub(r"按︰.*", "", text)
    text = re.sub(r"《[^》]+》曰：", "", text)
    return text.strip()


def fetch_wikisource() -> str:
    req = urllib.request.Request(WIKI_URL, headers={"User-Agent": "blog-book-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_chapters(html: str) -> list[dict]:
    # Extract mw-parser-output
    m = re.search(r'<div class="mw-parser-output">(.*?)</div>\s*<div id="catlinks"', html, re.S)
    if not m:
        raise RuntimeError("could not find mw-parser-output")
    body = m.group(1)
    # Split on h2 headers (wikisource: <h2 id="..."><span ...></span>始計第一</h2>)
    parts = re.split(r"<h2[^>]*>(.*?)</h2>", body, flags=re.S)
    sections: dict[str, str] = {}
    i = 1
    while i + 1 < len(parts):
        title = re.sub(r"<[^>]+>", "", parts[i]).strip()
        if title in ("目录", "目錄"):
            i += 2
            continue
        chunk = parts[i + 1]
        # Stop at 答話 appendix
        if "答話" in title or "答话" in title:
            break
        paras = re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S)
        lines: list[str] = []
        for p in paras:
            p = re.sub(r"<[^>]+>", "", p)
            p = p.replace("&nbsp;", " ").strip()
            if p:
                lines.append(p)
        sections[title] = "\n\n".join(lines)
        i += 2

    entries: list[dict] = []
    for num, short, wiki_title in CHAPTERS:
        raw = sections.get(wiki_title, "")
        if not raw:
            # fuzzy match
            for k, v in sections.items():
                if short in to_simplified(k) or wiki_title[:2] in k:
                    raw = v
                    break
        if not raw:
            raise RuntimeError(f"missing chapter {num} {wiki_title}; have {list(sections.keys())}")
        text = to_simplified(clean_wiki_text(raw))
        entries.append(
            {
                "id": num,
                "slug": short,
                "title": short,
                "full_title": f"{short}第{['一','二','三','四','五','六','七','八','九','十','十一','十二','十三'][num-1]}",
                "text": text,
            }
        )
    return entries


def main() -> None:
    if opencc is None:
        raise SystemExit("opencc required: use .venv/bin/python or pip install opencc-python-reimplemented")
    html = fetch_wikisource()
    entries = parse_chapters(html)
    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} chapters to {OUT}")
    for e in entries:
        print(f"  {e['id']:2d} {e['title']} ({len(e['text'])} chars)")


if __name__ == "__main__":
    main()
