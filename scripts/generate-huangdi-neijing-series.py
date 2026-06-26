#!/usr/bin/env python3
"""Generate 黄帝内经 series posts from assets/data/huangdi-neijing-jing.json."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/huangdi-neijing-jing.json"
HUB_SLUG = "2026/06/25/huangdi-neijing"
SERIES_START = date(2026, 6, 9)

VOLUMES = [
    (1, 1, 10, "素问·一", "上古天真论至五脏别论"),
    (2, 11, 20, "素问·二", "异法方宜论至三部九候论"),
    (3, 21, 30, "素问·三", "经脉别论至阳明脉解"),
    (4, 31, 40, "素问·四", "热论至腹中论"),
    (5, 41, 50, "素问·五", "刺腰痛论至刺要论"),
    (6, 51, 60, "素问·六", "刺齐论至水热穴论"),
    (7, 61, 70, "素问·七", "调经论至五常政大论"),
    (8, 71, 81, "素问·八", "六元正纪大论至解精微论"),
    (9, 82, 91, "灵枢·一", "九针十二原至经脉"),
    (10, 92, 101, "灵枢·二", "经别至五邪"),
    (11, 102, 111, "灵枢·三", "师传至病传"),
    (12, 112, 121, "灵枢·四", "淫邪发梦至五味"),
    (13, 122, 131, "灵枢·五", "水胀至阴阳二十五人"),
    (14, 132, 141, "灵枢·六", "五音五味至通天"),
    (15, 142, 151, "灵枢·七", "官能至九宫八风"),
    (16, 152, 162, "灵枢·八", "九针论至痈疽"),
]

GLOSS_KEYWORDS: list[tuple[str, str]] = [
    (r"治未病|未病|先防", "圣人不治已病治未病"),
    (r"正气存内|邪不可干", "正气存内，邪不可干"),
    (r"阴阳|寒暑|四时", "法于阴阳，和于术数"),
    (r"五行|五藏|五脏|六腑", "五行相胜，脏腑相应"),
    (r"经络|经脉|腧穴|针刺|九针", "经脉者，所以决死生"),
    (r"气血|营卫|津液", "营卫之气，昼行夜止"),
    (r"情志|喜怒|悲恐", "百病生于气也"),
    (r"虚邪贼风|恬淡虚无", "虚邪贼风，避之有时"),
]


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-huangdi-neijing-{start:03d}-{end:03d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}/' | relative_url }}}}"


def gloss(ch: dict) -> str:
    if ch.get("lost"):
        return "王冰本缺篇，仅存篇目"
    blob = ch["text"][:240]
    for pattern, meaning in GLOSS_KEYWORDS:
        if re.search(pattern, blob):
            return meaning
    if ch["book"] == "素问":
        return "素问论病机、治则与养生"
    return "灵枢论经络、针刺与形神"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 篇次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [黄帝内经（导读）— 天人合一]({rel(HUB_SLUG)}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/huangdi-neijing-{start:03d}-{end:03d}"
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
    book = ch["book"]
    chap = ch["chapter"]
    title = ch["title"]
    opening = ch["opening"]
    gloss_text = gloss(ch)
    body = format_body(ch["text"])
    label = f"{book}第{chap} · {title}"
    return "\n".join(
        [
            f"### {num} · {opening}",
            "",
            f"**{label}** · **要义**：{gloss_text}",
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
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(pv)}/huangdi-neijing-{ps:03d}-{pe:03d}')})"
        )
    if vol_idx + 1 < len(VOLUMES):
        ns, ne = VOLUMES[vol_idx + 1][1], VOLUMES[vol_idx + 1][2]
        nv = VOLUMES[vol_idx + 1][0]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(nv)}/huangdi-neijing-{ns:03d}-{ne:03d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    book_note = "素问八十一篇 + 灵枢八十一篇"
    body = [
        "---",
        "layout: post",
        f'title: "黄帝内经（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: medicine chinese-classics",
        "lang: zh-CN",
        f"tags: [黄帝内经, 中医, 素问, 灵枢, 黄帝内经系列, {label}]",
        "---",
        "",
        f"**《黄帝内经》原文 · 第 {vol} 卷**",
        f"篇次 **{start}–{end}**（{subtitle}）· 录通行本**{book_note}**",
        "",
        series_nav(vol),
        "",
        f"_方法论、史案与现代场景见 [黄帝内经（导读）]({rel(HUB_SLUG)})；本篇为**原文**全录（不含王冰注等注文）。_",
        "",
        "_底本：《素问》据 [四库全书本](https://zh.wikisource.org/wiki/黄帝内經素問_(四庫全書本)) 与 [黃帝內經/素問](https://zh.wikisource.org/wiki/黃帝內經) 对勘；《灵枢》据 [黃帝內經/灵枢](https://zh.wikisource.org/wiki/黃帝內經) 十二卷本，转简体。刺法论、本病论王冰本缺。_",
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
            f"| 1 | 通读 {start}–{end}，标 3 处「阴阳 / 正气 / 治未病」落点 |",
            "| 2 | 选一生活或公卫场景，问：此刻身与四时是否相得？ |",
            "| 3 | 与导读篇「读内经四步法」写一则短省察 |",
            "| 4 | 对照 [道德经]({{ '/2026/06/24/daodejing/' | relative_url }}) 或 [周易]({{ '/2026/05/07/zhouyi/' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [黄帝内经（导读）— 本站笔记]({rel(HUB_SLUG)})，八大专题、四步法与史案",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/huangdi-neijing-{s:03d}-{e:03d}"
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
