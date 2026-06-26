#!/usr/bin/env python3
"""Fetch 传习录 (三卷) + 大学问 from Wikisource into yangming-jing.json."""

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
OUT = ROOT / "assets/data/yangming-jing.json"

WIKI_VOLS = [
    ("上", "傳習錄/卷上"),
    ("中", "傳習錄/卷中"),
    ("下", "傳習錄/卷下"),
]
DAXUE_WIKI = "大學問"


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


def fetch_html(path: str) -> str:
    from urllib.parse import quote

    url = "https://zh.wikisource.org/wiki/" + quote(path)
    req = urllib.request.Request(url, headers={"User-Agent": "blog-book-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_paragraphs(html: str) -> list[str]:
    paras = re.findall(r"<p[^>]*>(.*?)</p>", html, re.S)
    out: list[str] = []
    for p in paras:
        p = re.sub(r"<small[^>]*>.*?</small>", "", p, flags=re.S)
        text = re.sub(r"<[^>]+>", "", p).strip()
        text = re.sub(r"&#91;\d+&#93;", "", text)
        text = text.replace("&lt;", "<").replace("&gt;", ">")
        text = to_simplified(text)
        if not text or text.startswith("检索自"):
            continue
        if "Public domain" in text or text in ("传习录", "傳習錄"):
            continue
        out.append(text)
    return out


def is_entry_start(para: str, vol: str) -> bool:
    if re.match(r"^门人.+[录書书]\。?$", para):
        return True
    if re.match(r"^右.+录\。?$", para):
        return True
    if vol == "中" and para.startswith("来书云："):
        return True
    if vol == "中" and para.startswith("德洪曰：") and len(para) > 100:
        return True
    if re.match(r"^[^。]{1,12}问[：:]", para):
        return True
    if para.startswith("问「") or para.startswith("问:"):
        return True
    if para.startswith("先生曰：") and len(para) < 80:
        return True
    return False


def title_from(para: str) -> str:
    t = para.replace("\n", " ")
    if len(t) > 40:
        return t[:40] + "…"
    return t


def group_entries(vol_label: str, paragraphs: list[str]) -> list[dict]:
    entries: list[dict] = []
    cur: list[str] = []
    cur_title = f"卷{vol_label}"

    for para in paragraphs:
        if is_entry_start(para, vol_label) and cur:
            entries.append(
                {
                    "volume": vol_label,
                    "title": cur_title,
                    "text": "\n\n".join(cur),
                }
            )
            cur = [para]
            cur_title = title_from(para)
        elif is_entry_start(para, vol_label) and not cur:
            cur = [para]
            cur_title = title_from(para)
        else:
            if not cur:
                cur = [para]
                cur_title = title_from(para)
            else:
                cur.append(para)

    if cur:
        entries.append(
            {
                "volume": vol_label,
                "title": cur_title,
                "text": "\n\n".join(cur),
            }
        )
    return entries


def main() -> None:
    all_entries: list[dict] = []

    for vol_label, wiki_path in WIKI_VOLS:
        html = fetch_html(wiki_path)
        paragraphs = extract_paragraphs(html)
        grouped = group_entries(vol_label, paragraphs)
        all_entries.extend(grouped)
        print(f"卷{vol_label}: {len(paragraphs)} paragraphs -> {len(grouped)} entries")

    daxue_paras = extract_paragraphs(fetch_html(DAXUE_WIKI))
    all_entries.append(
        {
            "volume": "大学问",
            "title": "大学问",
            "text": "\n\n".join(daxue_paras),
        }
    )
    print(f"大学问: {len(daxue_paras)} paragraphs -> 1 entry")

    payload = []
    for i, entry in enumerate(all_entries, start=1):
        payload.append(
            {
                "id": i,
                "volume": entry["volume"],
                "title": entry["title"],
                "text": entry["text"],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(payload)} entries)")


if __name__ == "__main__":
    main()
