#!/usr/bin/env python3
"""Generate 阳明心学 《大学问》 post from assets/data/yangming-jing.json."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/yangming-jing.json"
HUB_SLUG = "2026/06/22/yangming-xinxue"
CHUANXILU_HUB = "2026/06/17/chuanxilu-wang-yangming"
POST_DATE = date(2026, 4, 27)
ENTRY_ID = 255


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def format_body(text: str) -> str:
    lines: list[str] = []
    for para in text.split("\n\n"):
        para = para.strip()
        if para:
            lines.extend(["", para, ""])
    return "\n".join(lines).strip()


def main() -> None:
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    entry = next(e for e in entries if e["id"] == ENTRY_ID)
    body = "\n".join(
        [
            "---",
            "layout: post",
            'title: "阳明心学（原文）— 《大学问》"',
            f"date: {POST_DATE.isoformat()} 09:00:00 -0000",
            "categories: philosophy chinese-classics",
            "lang: zh-CN",
            "tags: [阳明心学, 王阳明, 大学问, 心学, 阳明心学系列]",
            "---",
            "",
            "**《大学问》原文**",
            "王守仁晚年纲领 · 格物致知新释 · 与《传习录》三卷并列为心学经部",
            "",
            f"_《传习录》254 条原文见 [传习录（导读）]({rel(CHUANXILU_HUB)}) 系列 8 卷；本篇为**大学问**全录。_",
            "",
            "_底本据 [维基文库](https://zh.wikisource.org/wiki/大學問)（转简体）。_",
            "",
            "---",
            "",
            "## 《大学问》",
            "",
            f"**要义**：纲领一篇，格物致知总其要",
            "",
            format_body(entry["text"]),
            "",
            "---",
            "",
            "## 读本卷提示",
            "",
            "| 步骤 | 做法 |",
            "|------|------|",
            "| 1 | 通读《大学问》，标 3 处「格物 / 致知 / 明明德」落点 |",
            "| 2 | 与《传习录》上卷格物问答对照，问：格物格什么？ |",
            "| 3 | 与导读篇「读阳明四步法」写一则短断语 |",
            "| 4 | 对照 [传习录原文 1–34]({{ '/2026/06/03/chuanxilu-001-034.html' | relative_url }}) |",
            "",
            f"上一篇：[传习录原文 231–254]({rel('2026/05/11/chuanxilu-231-254')})",
            "",
            "## 关联阅读",
            "",
            f"- [阳明心学（导读）— 本站笔记]({rel(HUB_SLUG)})，八大专题、四句教与史案",
            f"- [传习录（导读）— 本站笔记]({rel(CHUANXILU_HUB)})，诚意与边界栈",
            "- [传习录原文 1–34 — 本站笔记]({{ '/2026/06/03/chuanxilu-001-034.html' | relative_url }})",
            "",
            "## 状态",
            "",
            "在读 — _《大学问》录完；随读随补与传习录格物条对照_",
            "",
        ]
    )
    out = ROOT / "_posts" / f"{POST_DATE.isoformat()}-yangming-daxuewen.md"
    out.write_text(body, encoding="utf-8")
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
