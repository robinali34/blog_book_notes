#!/usr/bin/env python3
"""Fetch Guiguzi chapters from Wikisource into JSON (simplified, main text only)."""

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
OUT = ROOT / "assets/data/guiguzi-jing.json"

VOLUMES_WIKI = [
    ("卷01", "https://zh.wikisource.org/wiki/%E9%AC%BC%E8%B0%B7%E5%AD%90/%E5%8D%B701"),
    ("卷02", "https://zh.wikisource.org/wiki/%E9%AC%BC%E8%B0%B7%E5%AD%90/%E5%8D%B702"),
    ("卷03", "https://zh.wikisource.org/wiki/%E9%AC%BC%E8%B0%B7%E5%AD%90/%E5%8D%B703"),
]

# id, short title, wiki h2 title
CHAPTERS = [
    (1, "捭阖", "捭闔第一"),
    (2, "反应", "反應第二"),
    (3, "内揵", "內揵第三"),
    (4, "抵巇", "抵巇第四"),
    (5, "飞钳", "飛箝第五"),
    (6, "忤合", "忤合第六"),
    (7, "揣", "揣篇第七"),
    (8, "摩", "摩篇第八"),
    (9, "权", "權篇第九"),
    (10, "谋", "謀篇第十"),
    (11, "决", "決篇第十一"),
    (12, "符言", "符言第十二"),
    (13, "本经阴符七术", "夲經隂符七術"),
    (14, "持枢", "持樞"),
    (15, "中经", "中經"),
]

ORDINALS = "一二三四五六七八九十"


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


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


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "blog-book-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_chapter_text(chunk: str) -> str:
    chunk = re.sub(r'<span class="mw-editsection.*?</span>', "", chunk, flags=re.S)
    chunk = re.sub(r'<div class="mw-editsection.*?</div>', "", chunk, flags=re.S)
    paras = re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S)
    lines: list[str] = []
    for p in paras:
        p = re.sub(r"<small[^>]*>.*?</small>", "", p, flags=re.S)
        p = re.sub(r"<style[^>]*>.*?</style>", "", p, flags=re.S)
        text = re.sub(r"<[^>]+>", "", p)
        text = text.replace("&nbsp;", " ").strip()
        if text and text not in ("[编辑]", "编辑"):
            lines.append(text)
    return "\n\n".join(lines)


def parse_volume(html: str) -> dict[str, str]:
    parts = re.split(r"<h2[^>]*>(.*?)</h2>", html, flags=re.S)
    sections: dict[str, str] = {}
    i = 1
    while i + 1 < len(parts):
        title = re.sub(r"<[^>]+>", "", parts[i]).strip()
        if title in ("目录", "目錄"):
            i += 2
            continue
        sections[title] = extract_chapter_text(parts[i + 1])
        i += 2
    return sections


def main() -> None:
    if opencc is None:
        raise SystemExit("opencc required: use .venv/bin/python")

    all_sections: dict[str, str] = {}
    for _vol, url in VOLUMES_WIKI:
        html = fetch_html(url)
        all_sections.update(parse_volume(html))

    entries: list[dict] = []
    for num, short, wiki_title in CHAPTERS:
        raw = all_sections.get(wiki_title, "")
        if not raw:
            raise RuntimeError(f"missing {wiki_title}; have {list(all_sections.keys())}")
        text = to_simplified(raw)
        entries.append(
            {
                "id": num,
                "slug": short,
                "title": short,
                "full_title": wiki_title if num > 12 else f"{short}第{ordinal(num)}",
                "text": text,
            }
        )

    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} chapters to {OUT}")
    for e in entries:
        print(f"  {e['id']:2d} {e['title']} ({len(e['text'])} chars)")


if __name__ == "__main__":
    main()
