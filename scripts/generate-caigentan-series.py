#!/usr/bin/env python3
"""Generate Caigentan 375-entry series posts from assets/data/caigentan-jing.json."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/caigentan-jing.json"
HUB_SLUG = "2026-06-03-caigentan"
SERIES_START = date(2026, 6, 17)

VOLUMES = [
    (1, 1, 31, "修身", "1–31"),
    (2, 32, 82, "应酬", "32–82"),
    (3, 83, 130, "评议", "83–130"),
    (4, 131, 178, "闲适", "131–178"),
    (5, 179, 231, "概论", "179–231"),
    (6, 232, 284, "概论", "232–284"),
    (7, 285, 337, "概论", "285–337"),
    (8, 338, 375, "概论", "338–375"),
]


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-caigentan-{start:03d}-{end:03d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 则次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [菜根谭（导读）— 布衣菜根]({rel('2026/06/03/caigentan')}) |"
    )
    for v, start, end, section, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/caigentan-{start:03d}-{end:03d}"
        title = f"原文 {subtitle}（{section}）"
        if v == current_vol:
            lines.append(f"| **{v}** | {start}–{end} | **{title}** ← 本篇 |")
        else:
            lines.append(f"| {v} | {start}–{end} | [{title}]({rel(slug)}) |")
    lines.append("")
    return "\n".join(lines)


def entry_block(e: dict) -> str:
    num = e["id"]
    section = e["section_title"]
    text = e["text"]
    return "\n".join(
        [
            f"### {num} · {section}",
            "",
            f"> {text}",
            "",
            "---",
            "",
        ]
    )


def volume_post(vol: int, start: int, end: int, section: str, subtitle: str, cards: list) -> str:
    d = vol_date(vol)
    prev_link = next_link = ""
    if vol > 1:
        ps, pe = VOLUMES[vol - 2][1], VOLUMES[vol - 2][2]
        prev_link = (
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(vol - 1)}/caigentan-{ps:03d}-{pe:03d}')})"
        )
    if vol < 8:
        ns, ne = VOLUMES[vol][1], VOLUMES[vol][2]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(vol + 1)}/caigentan-{ns:03d}-{ne:03d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "菜根谭（原文 {subtitle}）— {section}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [菜根谭, 洪应明, 处世, 格言, 菜根谭系列, {section}]",
        "---",
        "",
        f"**《菜根谭》原文 · 第 {vol} 卷**",
        f"则次 **{start}–{end}**（{section}：{subtitle}）· 录通行本**原文**",
        "",
        series_nav(vol),
        "",
        f"_方法论、史案与场景应用见 [菜根谭（导读）]({rel('2026/06/03/caigentan')})；本篇为**原文**全录。_",
        "",
        "---",
        "",
        f"## 原文 {subtitle}（{section}）",
        "",
    ]
    for e in cards:
        body.append(entry_block(e))
    body.extend(
        [
            "## 读本卷提示",
            "",
            "| 步骤 | 做法 |",
            "|------|------|",
            f"| 1 | 通读 {start}–{end}，标 3 条最触动己者 |",
            "| 2 | 选一则抄录，问：今日何处可践行？ |",
            "| 3 | 晚间回顾：做到了吗？偏差在哪？ |",
            "| 4 | 与导读篇五编主题表对照，补一则史案或当下事例 |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [菜根谭（导读）— 本站笔记]({rel('2026/06/03/caigentan')})，五编结构、史案与现代映射",
        ]
    )
    for v, s, e, sec, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/caigentan-{s:03d}-{e:03d}"
        body.append(f"- [原文 {sub}（{sec}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与个人日课_",
            "",
        ]
    )
    return "\n".join(body)


def main() -> None:
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in entries}
    for vol, start, end, section, subtitle in VOLUMES:
        cards = [by_id[i] for i in range(start, end + 1)]
        missing = [i for i in range(start, end + 1) if i not in by_id]
        if missing:
            raise SystemExit(f"volume {vol} missing ids: {missing}")
        out = ROOT / "_posts" / vol_filename(vol, start, end)
        out.write_text(volume_post(vol, start, end, section, subtitle, cards), encoding="utf-8")
        print(f"wrote {out.name} ({len(cards)} entries)")


if __name__ == "__main__":
    main()
