#!/usr/bin/env python3
"""Fetch Shangjunshu 24 chapters from Wikisource into JSON (simplified)."""

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
OUT = ROOT / "assets/data/shangjunshu-jing.json"

# 通行二十六篇目，刑约第十六、御盗第二十一篇亡，录存二十四篇
CHAPTERS = [
    (1, "更法", "更法第一"),
    (2, "垦令", "墾令第二"),
    (3, "农战", "農戰第三"),
    (4, "去强", "去彊第四"),
    (5, "说民", "說民第五"),
    (6, "算地", "算地第六"),
    (7, "开塞", "開塞第七"),
    (8, "壹言", "壹言第八"),
    (9, "错法", "錯法第九"),
    (10, "战法", "戰法第十"),
    (11, "立本", "立本第十一"),
    (12, "兵守", "兵守第十二"),
    (13, "靳令", "靳令第十三"),
    (14, "修权", "修權第十四"),
    (15, "徕民", "徠民第十五"),
    (16, "赏刑", "賞刑第十七"),
    (17, "画策", "畫策第十八"),
    (18, "境内", "境內第十九"),
    (19, "弱民", "弱民第二十"),
    (20, "外内", "外內第二十二"),
    (21, "君臣", "君臣第二十三"),
    (22, "禁使", "禁使第二十四"),
    (23, "慎法", "慎法第二十五"),
    (24, "定分", "定分第二十六"),
]

VOLUME_PATHS = [
    "%E5%8D%B7%E4%B8%80",
    "%E5%8D%B7%E4%BA%8C",
    "%E5%8D%B7%E4%B8%89",
    "%E5%8D%B7%E5%9B%9B",
    "%E5%8D%B7%E4%BA%94",
]


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


def fetch_volume(path: str) -> dict[str, str]:
    url = f"https://zh.wikisource.org/wiki/%E5%95%86%E5%90%9B%E6%9B%B8/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "blog-book-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = re.search(
        r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>(.*)<div id="catlinks"',
        html,
        re.S,
    )
    if not m:
        raise RuntimeError(f"could not parse {url}")
    body = m.group(1)
    parts = re.split(r"<h2[^>]*>(.*?)</h2>", body, flags=re.S)
    sections: dict[str, str] = {}
    i = 1
    while i + 1 < len(parts):
        title = to_simplified(re.sub(r"<[^>]+>", "", parts[i]).strip())
        chunk = parts[i + 1]
        paras = re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S)
        lines: list[str] = []
        for para in paras:
            para = re.sub(r"<[^>]+>", "", para).replace("&nbsp;", " ").strip()
            if para:
                lines.append(para)
        if title not in ("目录", "目錄"):
            sections[title] = "\n\n".join(lines)
        i += 2
    return sections


def main() -> None:
    if opencc is None:
        raise SystemExit("opencc required: use .venv/bin/python or pip install opencc-python-reimplemented")

    all_sections: dict[str, str] = {}
    for path in VOLUME_PATHS:
        all_sections.update(fetch_volume(path))

    entries: list[dict] = []
    for num, short, wiki_title in CHAPTERS:
        text = all_sections.get(to_simplified(wiki_title), "")
        if not text:
            for key, value in all_sections.items():
                if short in key:
                    text = value
                    break
        if not text:
            raise RuntimeError(f"missing chapter {num} {wiki_title}; have {list(all_sections)}")
        entries.append(
            {
                "id": num,
                "slug": short,
                "title": short,
                "full_title": to_simplified(wiki_title),
                "text": text,
            }
        )

    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} chapters to {OUT}")
    for entry in entries:
        print(f"  {entry['id']:2d} {entry['title']} ({len(entry['text'])} chars)")


if __name__ == "__main__":
    main()
