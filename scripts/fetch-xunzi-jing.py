#!/usr/bin/env python3
"""Fetch Xunzi 32 chapters from Wikisource into JSON (simplified, 正文去注)."""

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
OUT = ROOT / "assets/data/xunzi-jing.json"

CHAPTERS = [
    (1, "劝学", "%E5%8B%B8%E5%AD%B8%E7%AF%87"),
    (2, "修身", "%E4%BF%AE%E8%BA%AB%E7%AF%87"),
    (3, "不苟", "%E4%B8%8D%E8%8B%9F%E7%AF%87"),
    (4, "荣辱", "%E6%A6%AE%E8%BE%B1%E7%AF%87"),
    (5, "非相", "%E9%9D%9E%E7%9B%B8%E7%AF%87"),
    (6, "非十二子", "%E9%9D%9E%E5%8D%81%E4%BA%8C%E5%AD%90%E7%AF%87"),
    (7, "仲尼", "%E4%BB%B2%E5%B0%BC%E7%AF%87"),
    (8, "儒效", "%E5%84%92%E6%95%88%E7%AF%87"),
    (9, "王制", "%E7%8E%8B%E5%88%B6%E7%AF%87"),
    (10, "富国", "%E5%AF%8C%E5%9C%8B%E7%AF%87"),
    (11, "王霸", "%E7%8E%8B%E9%9C%B8%E7%AF%87"),
    (12, "君道", "%E5%90%9B%E9%81%93%E7%AF%87"),
    (13, "臣道", "%E8%87%A3%E9%81%93%E7%AF%87"),
    (14, "致士", "%E8%87%B4%E5%A3%AB%E7%AF%87"),
    (15, "议兵", "%E8%AD%B0%E5%85%B5%E7%AF%87"),
    (16, "强国", "%E5%BD%8A%E5%9C%8B%E7%AF%87"),
    (17, "天论", "%E5%A4%A9%E8%AB%96%E7%AF%87"),
    (18, "正论", "%E6%AD%A3%E8%AB%96%E7%AF%87"),
    (19, "礼论", "%E7%A6%AE%E8%AB%96%E7%AF%87"),
    (20, "乐论", "%E6%A8%82%E8%AB%96%E7%AF%87"),
    (21, "解蔽", "%E8%A7%A3%E8%94%BD%E7%AF%87"),
    (22, "正名", "%E6%AD%A3%E5%90%8D%E7%AF%87"),
    (23, "性恶", "%E6%80%A7%E6%83%A1%E7%AF%87"),
    (24, "君子", "%E5%90%9B%E5%AD%90%E7%AF%87"),
    (25, "成相", "%E6%88%90%E7%9B%B8%E7%AF%87"),
    (26, "赋", "%E8%B3%A6%E7%AF%87"),
    (27, "大略", "%E5%A4%A7%E7%95%A5%E7%AF%87"),
    (28, "宥坐", "%E5%AE%A5%E5%9D%90%E7%AF%87"),
    (29, "子道", "%E5%AD%90%E9%81%93%E7%AF%87"),
    (30, "法行", "%E6%B3%95%E8%A1%8C%E7%AF%87"),
    (31, "哀公", "%E5%93%80%E5%85%AC%E7%AF%87"),
    (32, "尧问", "%E5%A0%AF%E5%95%8F%E7%AF%87"),
]


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


def strip_commentary(text: str) -> str:
    text = re.sub(r"〈[^〉]*〉", "", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_chapter(path: str) -> str:
    url = f"https://zh.wikisource.org/wiki/%E8%8D%80%E5%AD%90/{path}"
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
    paras = re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)
    lines: list[str] = []
    for para in paras:
        para = re.sub(r"<[^>]+>", "", para).replace("&nbsp;", " ").strip()
        para = strip_commentary(para)
        if para and "检索自" not in para:
            lines.append(para)
    return "\n\n".join(lines)


def main() -> None:
    if opencc is None:
        raise SystemExit("opencc required: use .venv/bin/python or pip install opencc-python-reimplemented")

    entries: list[dict] = []
    for num, short, path in CHAPTERS:
        text = to_simplified(fetch_chapter(path))
        if not text:
            raise RuntimeError(f"empty chapter {num} {short}")
        entries.append(
            {
                "id": num,
                "slug": short,
                "title": short,
                "full_title": f"{short}篇第{num}",
                "text": text,
            }
        )

    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} chapters to {OUT}")
    for entry in entries:
        print(f"  {entry['id']:2d} {entry['title']} ({len(entry['text'])} chars)")


if __name__ == "__main__":
    main()
