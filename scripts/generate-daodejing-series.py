#!/usr/bin/env python3
"""Generate 道德经 series posts from assets/data/daodejing-jing.json."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/daodejing-jing.json"
HUB_SLUG = "2026/06/24/daodejing"
SERIES_START = date(2026, 5, 30)

VOLUMES = [
    (1, 1, 10, "道经·上", "道可道至上善若水"),
    (2, 11, 20, "道经·中", "有物混成至大道废"),
    (3, 21, 30, "道经·下", "孔德之容至以道佐主"),
    (4, 31, 37, "道经·末", "夫兵者至道法自然"),
    (5, 38, 47, "德经·上", "上德不德至祸兮福所倚"),
    (6, 48, 57, "德经·中", "为学日益至以正治国"),
    (7, 58, 67, "德经·下", "其政闷闷至天下皆谓我大"),
    (8, 68, 81, "德经·末", "善为士者至为而不争"),
]

GLOSS_KEYWORDS: list[tuple[str, str]] = [
    (r"道可道|非常道", "道不可名，强言非常"),
    (r"无为而无不为|为无为", "无为而无不为"),
    (r"上善若水|利万物而不争", "上善若水，不争几于道"),
    (r"知足|知止|不殆", "知足不辱，知止不殆"),
    (r"柔弱|坚强|天下莫柔弱于水", "柔弱胜刚强"),
    (r"反者道之动|弱者道之用", "反者道之动，弱者道之用"),
    (r"圣人|侯王|治国|天下", "圣人无为，百姓自化"),
    (r"上德不德|失道而后德", "上德不德，失道而后德"),
    (r"三宝|慈俭|不敢为天下先", "三宝：慈、俭、不敢先"),
    (r"为学日益|为道日损", "为道日损，少则得"),
    (r"信言不美|为而不争", "信言不美，为而不争"),
]


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-daodejing-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def gloss(ch: dict) -> str:
    blob = ch["text"][:200]
    for pattern, meaning in GLOSS_KEYWORDS:
        if re.search(pattern, blob):
            return meaning
    part_gloss = {
        "道经": "道本体与自然运行",
        "德经": "德性处世与治国",
    }
    return part_gloss.get(ch["part"], "道法自然，虚静守中")


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 章次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [道德经（导读）— 道法自然]({rel(HUB_SLUG)}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/daodejing-{start:02d}-{end:02d}"
        title = f"原文 {start}–{end}（{subtitle}）"
        if v == current_vol:
            lines.append(f"| **{v}** | {start}–{end} | **{title}** ← 本篇 |")
        else:
            lines.append(f"| {v} | {start}–{end} | [{title}]({rel(slug)}) |")
    lines.append("")
    return "\n".join(lines)


def format_body(text: str) -> str:
    lines: list[str] = []
    for para in text.split("\n\n"):
        para = para.strip()
        if para:
            lines.extend(["", para, ""])
    return "\n".join(lines).strip()


def chapter_section(ch: dict) -> str:
    num = ch["id"]
    opening = ch["opening"]
    part = ch["part"]
    gloss_text = gloss(ch)
    body = format_body(ch["text"])
    return "\n".join(
        [
            f"### {num} · {opening}",
            "",
            f"**{part}** · **要义**：{gloss_text}",
            "",
            body,
            "",
            "---",
            "",
        ]
    )


def volume_post(vol: int, start: int, end: int, label: str, subtitle: str, batch: list) -> str:
    d = vol_date(vol)
    prev_link = next_link = ""
    vol_idx = next(i for i, v in enumerate(VOLUMES) if v[0] == vol)
    if vol_idx > 0:
        ps, pe = VOLUMES[vol_idx - 1][1], VOLUMES[vol_idx - 1][2]
        pv = VOLUMES[vol_idx - 1][0]
        prev_link = (
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(pv)}/daodejing-{ps:02d}-{pe:02d}')})"
        )
    if vol_idx + 1 < len(VOLUMES):
        ns, ne = VOLUMES[vol_idx + 1][1], VOLUMES[vol_idx + 1][2]
        nv = VOLUMES[vol_idx + 1][0]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(nv)}/daodejing-{ns:02d}-{ne:02d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "道德经（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [道德经, 老子, 道家, 道德经系列, {label}]",
        "---",
        "",
        f"**《道德经》原文 · 第 {vol} 卷**",
        f"章次 **{start}–{end}**（{subtitle}）· 录通行本**八十一章**（王弼章序，汇校本正文）",
        "",
        series_nav(vol),
        "",
        f"_方法论、史案与现代场景见 [道德经（导读）]({rel(HUB_SLUG)})；本篇为**原文**全录（不含校勘异文注）。_",
        "",
        "_底本据 [维基文库](https://zh.wikisource.org/wiki/老子_(匯校版))《老子（汇校版）》，转简体。_",
        "",
        "---",
        "",
        f"## 原文 {start}–{end}（{subtitle}）",
        "",
    ]
    for ch in batch:
        body.append(chapter_section(ch))
    body.extend(
        [
            "## 读本卷提示",
            "",
            "| 步骤 | 做法 |",
            "|------|------|",
            f"| 1 | 通读 {start}–{end}，标 3 处「无为 / 柔弱 / 知足」落点 |",
            "| 2 | 选一史案或组织场景，问：此刻是「为」还是「妄为」？ |",
            "| 3 | 与导读篇「读道德经四步法」写一则短断语 |",
            "| 4 | 对照 [周易]({{ '/2026/05/07/zhouyi.html' | relative_url }}) 或 [黄帝内经]({{ '/2026/06/25/huangdi-neijing.html' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [道德经（导读）— 本站笔记]({rel(HUB_SLUG)})，八大专题、四步法与史案",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/daodejing-{s:02d}-{e:02d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与版本对照_",
            "",
        ]
    )
    return "\n".join(body)


def main() -> None:
    chapters = json.loads(DATA.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in chapters}
    posts_dir = ROOT / "_posts"

    for vol, start, end, label, subtitle in VOLUMES:
        batch = [by_id[i] for i in range(start, end + 1)]
        missing = [i for i in range(start, end + 1) if i not in by_id]
        if missing:
            raise SystemExit(f"volume {vol} missing chapters: {missing}")
        out = posts_dir / vol_filename(vol, start, end)
        out.write_text(volume_post(vol, start, end, label, subtitle, batch), encoding="utf-8")
        print(f"wrote {out.name} ({len(batch)} chapters)")


if __name__ == "__main__":
    main()
