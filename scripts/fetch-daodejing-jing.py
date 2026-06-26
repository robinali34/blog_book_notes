#!/usr/bin/env python3
"""Fetch Laozi 81 chapters from Wikisource 老子 (匯校版) into JSON (simplified, main text)."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import quote

try:
    import opencc
except ImportError:
    opencc = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/data/daodejing-jing.json"
WIKI_PATH = "老子 (匯校版)"

CN_DIGITS = "零一二三四五六七八九"
CN_UNITS = ("", "十", "百")


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


def cn_to_int(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("empty numeral")
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + (CN_DIGITS.index(s[1]) if len(s) > 1 else 0)
    if "十" in s:
        parts = s.split("十", 1)
        tens = CN_DIGITS.index(parts[0]) if parts[0] else 1
        ones = CN_DIGITS.index(parts[1]) if len(parts) > 1 and parts[1] else 0
        return tens * 10 + ones
    total = 0
    for ch in s:
        if ch in CN_DIGITS:
            total = total * 10 + CN_DIGITS.index(ch)
    return total


def parse_chapter_num(title: str) -> int:
    title = re.sub(r"\[编辑\]|\[編輯\]", "", title).strip()
    m = re.match(r"^(.+?)章$", title)
    if not m:
        raise ValueError(f"unexpected chapter title: {title!r}")
    return cn_to_int(m.group(1))


def opening_phrase(text: str, max_len: int = 12) -> str:
    line = text.replace("\n", "").strip()
    line = re.sub(r"[「」『』]", "", line)
    for sep in "。；，":
        if sep in line:
            line = line.split(sep)[0]
            break
    if len(line) > max_len:
        return line[:max_len] + "…"
    return line


def clean_chunk(chunk: str) -> str:
    chunk = re.sub(r"<style[^>]*>.*?</style>", "", chunk, flags=re.S)
    chunk = re.sub(r"<link[^>]*>", "", chunk)
    chunk = re.sub(r'<span class="variant-tooltip">.*?</span>', "", chunk, flags=re.S)
    chunk = re.sub(r'<span class="variant-text"[^>]*>', "", chunk)
    chunk = chunk.replace("</span>", "")
    paras = re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S)
    lines: list[str] = []
    for p in paras:
        text = re.sub(r"<[^>]+>", "", p).strip()
        text = text.replace("&nbsp;", " ")
        if not text:
            continue
        if "Public domain" in text or text.startswith("此作品在全世界"):
            continue
        lines.append(text)
    return to_simplified("\n\n".join(lines))


def fetch_html() -> str:
    url = "https://zh.wikisource.org/wiki/" + quote(WIKI_PATH)
    req = urllib.request.Request(url, headers={"User-Agent": "blog-book-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_chapters(html: str) -> list[dict]:
    pattern = (
        r'<div class="mw-heading mw-heading3">(.*?)</div>\s*'
        r"(.*?)(?=<div class=\"mw-heading mw-heading3\">|"
        r'<div class="mw-heading mw-heading2">|</div>\s*<div id="catlinks")'
    )
    blocks = re.findall(pattern, html, re.S)
    if len(blocks) != 81:
        raise RuntimeError(f"expected 81 chapters, got {len(blocks)}")

    entries: list[dict] = []
    for heading, chunk in blocks:
        raw_title = re.sub(r"<[^>]+>", "", heading).strip()
        num = parse_chapter_num(raw_title)
        text = clean_chunk(chunk)
        if not text:
            raise RuntimeError(f"empty text for chapter {num}")
        part = "道经" if num <= 37 else "德经"
        phrase = opening_phrase(text)
        entries.append(
            {
                "id": num,
                "slug": f"{num:02d}",
                "title": f"第{cn_title(num)}章",
                "part": part,
                "opening": phrase,
                "text": text,
            }
        )

    entries.sort(key=lambda e: e["id"])
    if [e["id"] for e in entries] != list(range(1, 82)):
        raise RuntimeError("chapter numbering gap")
    return entries


def cn_title(num: int) -> str:
    if num <= 10:
        return ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"][num]
    if num < 20:
        return "十" + cn_title(num - 10)
    if num % 10 == 0:
        return cn_title(num // 10) + "十"
    tens, ones = divmod(num, 10)
    return cn_title(tens) + "十" + cn_title(ones)


def main() -> None:
    if opencc is None:
        raise SystemExit("opencc required: use .venv/bin/python")
    html = fetch_html()
    entries = parse_chapters(html)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} chapters to {OUT}")
    for e in entries:
        print(f"  {e['id']:2d} {e['part']} {e['opening']} ({len(e['text'])} chars)")


if __name__ == "__main__":
    main()
