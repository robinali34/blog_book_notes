#!/usr/bin/env python3
"""Generate Sunzi Bingfa 13-chapter series posts from assets/data/sunzi-jing.json."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/sunzi-jing.json"
HUB_SLUG = "2026-06-08-sunzi"
SERIES_START = date(2026, 6, 9)

VOLUMES = [
    (1, 1, 4, "上篇一", "始计至军形"),
    (2, 5, 7, "上篇二", "兵势至军争"),
    (3, 8, 10, "下篇一", "九变至地形"),
    (4, 11, 13, "下篇二", "九地至用间"),
]

GLOSSES: dict[str, str] = {
    "始计": "庙算五事七计，多算胜",
    "作战": "贵胜不贵久，因粮于敌",
    "谋攻": "伐谋为上，知彼知己",
    "军形": "先为不可胜，形胜之本",
    "兵势": "以正合以奇胜，任势不责人",
    "虚实": "致人而不致于人，避实击虚",
    "军争": "以迂为直，先知迂直",
    "九变": "九变之利，五危之戒",
    "行军": "处军相敌，察兆知变",
    "地形": "六地六败，知地知天",
    "九地": "九地之变，投之亡地然后存",
    "火攻": "五火之变，慎战止怒",
    "用间": "先知五间，三军所恃",
}


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-sunzi-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 篇次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [孙子兵法（导读）— 先胜后战]({rel('2026/06/08/sunzi')}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/sunzi-{start:02d}-{end:02d}"
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
    title = ch["title"]
    gloss = GLOSSES.get(title, "庙算利害，全胜为上")
    body = format_body(ch["text"])
    return "\n".join(
        [
            f"### {num} · {title}",
            "",
            f"**要义**：{gloss}",
            "",
            body,
            "",
            "---",
            "",
        ]
    )


def volume_post(vol: int, start: int, end: int, label: str, subtitle: str, cards: list) -> str:
    d = vol_date(vol)
    prev_link = next_link = ""
    if vol > 1:
        ps, pe = VOLUMES[vol - 2][1], VOLUMES[vol - 2][2]
        prev_link = (
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(vol - 1)}/sunzi-{ps:02d}-{pe:02d}')})"
        )
    if vol < 4:
        ns, ne = VOLUMES[vol][1], VOLUMES[vol][2]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(vol + 1)}/sunzi-{ns:02d}-{ne:02d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "孙子兵法（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [孙子兵法, 孙武, 春秋, 谋略, 孙子兵法系列, {label}]",
        "---",
        "",
        f"**《孙子兵法》原文 · 第 {vol} 卷**",
        f"篇次 **{start}–{end}**（{subtitle}）· 录通行本**十三篇原文**",
        "",
        series_nav(vol),
        "",
        f"_方法论、战役复盘与现代对照见 [孙子兵法（导读）]({rel('2026/06/08/sunzi')})；本篇为**原文**全录。_",
        "",
        "_底本据 [维基文库](https://zh.wikisource.org/wiki/孫子兵法)（通行十三篇，转简体）。_",
        "",
        "---",
        "",
        f"## 原文 {start}–{end}（{subtitle}）",
        "",
    ]
    for ch in cards:
        body.append(chapter_section(ch))
    body.extend(
        [
            "## 读本卷提示",
            "",
            "| 步骤 | 做法 |",
            "|------|------|",
            f"| 1 | 通读 {start}–{end}，标 3 处「庙算 / 全胜 / 虚实」落点 |",
            "| 2 | 选一古代战役，用本篇框架复盘 |",
            "| 3 | 与导读篇「读孙子四步法」写一则决策短断语 |",
            "| 4 | 对照 [鬼谷子]({{ '/2026/04/27/guiguzi.html' | relative_url }}) 或 [管理的本质]({{ '/2026/06/02/management-essence-interest-exchange.html' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [孙子兵法（导读）— 本站笔记]({rel('2026/06/08/sunzi')})，十三篇主题、史案与现代映射",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/sunzi-{s:02d}-{e:02d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补战役复盘与现代对照_",
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
            raise SystemExit(f"volume {vol} missing: {missing}")
        out = posts_dir / vol_filename(vol, start, end)
        out.write_text(volume_post(vol, start, end, label, subtitle, batch), encoding="utf-8")
        print(f"wrote {out.name} ({len(batch)} chapters)")


if __name__ == "__main__":
    main()
