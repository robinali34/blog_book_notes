#!/usr/bin/env python3
"""Parse Qing 375-entry Caigentan into JSON (simplified original text only)."""

from __future__ import annotations

import json
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/data/caigentan-375-source.txt"
OUT = ROOT / "assets/data/caigentan-jing.json"
TAIL_CACHE = ROOT / "assets/data/caigentan-375-tail.txt"

SECTIONS = [
    ("xiushen", "修身", 1, 31),
    ("yingchou", "应酬", 32, 82),
    ("pingyi", "评议", 83, 130),
    ("xianshi", "闲适", 131, 178),
    ("gailun", "概论", 179, 375),
]

SECTION_MARKERS = [
    ("一、修身", "xiushen"),
    ("二、应酬", "yingchou"),
    ("三、评议", "pingyi"),
    ("四、闲适", "xianshi"),
    ("五、概论", "gailun"),
]

SECTION_FOR_ID = []
for slug, title, lo, hi in SECTIONS:
    for i in range(lo, hi + 1):
        SECTION_FOR_ID.append((i, slug, title))


def strip_translation(text: str) -> str:
    if "【大意】" in text:
        text = text.split("【大意】", 1)[0]
    return re.sub(r"\s+", "", text).strip()


def is_noise_line(line: str) -> bool:
    if not line.strip():
        return True
    noise = (
        "展开全文",
        "说明:",
        "大 中 小",
        "沧海一粟",
        "转藏",
        "本站是提供",
        "猜你喜欢",
        "类似文章",
        "热门阅读",
        "发送到手机",
        "分享文章",
        "朗读全文",
        "《菜根谭》全文",
    )
    return any(x in line for x in noise)


def parse_source_file(text: str) -> dict[int, str]:
    lines: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if is_noise_line(line) or line.startswith("#") or line.startswith("|"):
            continue
        lines.append(line)
    blob = "\n".join(lines)

    # Drop TOC line that concatenates all section headers
    blob = re.sub(r"一、\s*修身（1—31）二、.*五、\s*概论（178—374）", "", blob)

    parts: dict[str, str] = {}
    ordered_keys = [k for _, k in SECTION_MARKERS]
    for marker, key in SECTION_MARKERS:
        idx = blob.find(marker)
        if idx >= 0:
            parts[key] = blob[idx:]

    for i, key in enumerate(ordered_keys):
        if key not in parts:
            continue
        start = re.sub(r"^[一二三四五]、[^\n]+\n", "", parts[key], count=1)
        if i + 1 < len(ordered_keys):
            next_marker = next(m for m, k in SECTION_MARKERS if k == ordered_keys[i + 1])
            j = start.find(next_marker)
            if j > 0:
                start = start[:j]
        parts[key] = start

    entries: dict[int, str] = {}
    pattern = re.compile(r"(?<!\d)(\d{1,3})[．.]([\s\S]*?)(?=(?:\d{1,3}[．.])|$)")
    for slug, _title, lo, hi in SECTIONS:
        chunk = parts.get(slug, "")
        for m in pattern.finditer(chunk):
            num = int(m.group(1))
            if not (lo <= num <= hi):
                continue
            body = strip_translation(m.group(2))
            if len(body) < 4:
                continue
            entries[num] = body
    return entries


def fetch_8bei_entry(num: int) -> str | None:
    url = f"https://www.8bei8.com/book/caigentan_{num}.html"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (blog-book-notes)"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = re.search(r"<div class=yuanwen>(.*?)</div>", html, re.S)
    if not m:
        return None
    chunk = m.group(1)
    chunk = re.sub(r"<sup[^>]*>.*?</sup>", "", chunk)
    chunk = re.sub(r"<tt[^>]*>|</tt>", "", chunk)
    chunk = re.sub(r"<p[^>]*>|</p>", "", chunk)
    return unescape(chunk).strip()


def load_tail_entries(start: int = 301, end: int = 375) -> dict[int, str]:
    cached: dict[int, str] = {}
    if TAIL_CACHE.exists():
        for line in TAIL_CACHE.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(\d{1,3})\.(.+)$", line.strip())
            if m:
                cached[int(m.group(1))] = m.group(2).strip()

    entries: dict[int, str] = {}
    lines_out: list[str] = []
    for num in range(start, end + 1):
        if num in cached:
            entries[num] = cached[num]
            lines_out.append(f"{num}.{cached[num]}")
            continue
        text = fetch_8bei_entry(num)
        if not text:
            raise RuntimeError(f"failed to fetch entry {num} from 8bei8")
        entries[num] = text
        lines_out.append(f"{num}.{text}")
        time.sleep(0.12)

    TAIL_CACHE.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    return entries


def build_entries() -> list[dict]:
    text = SOURCE.read_text(encoding="utf-8")
    by_id = parse_source_file(text)
    missing_low = [i for i in range(1, 301) if i not in by_id]
    if missing_low:
        print(f"warning: missing {len(missing_low)} entries in 1–300: {missing_low[:15]}...")

    tail = load_tail_entries(301, 375)
    by_id.update(tail)

    entries: list[dict] = []
    for num, slug, title in SECTION_FOR_ID:
        if num not in by_id:
            continue
        entries.append(
            {
                "id": num,
                "section": slug,
                "section_title": title,
                "text": by_id[num],
            }
        )
    entries.sort(key=lambda x: x["id"])
    return entries


def main() -> None:
    entries = build_entries()
    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} entries to {OUT}")
    missing = [i for i in range(1, 376) if i not in {e["id"] for e in entries}]
    if missing:
        print(f"still missing {len(missing)}: {missing}")


if __name__ == "__main__":
    main()
