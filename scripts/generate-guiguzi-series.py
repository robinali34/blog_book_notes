#!/usr/bin/env python3
"""Generate Guiguzi series posts from assets/data/guiguzi-jing.json."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/guiguzi-jing.json"
SERIES_START = date(2026, 4, 28)

# Twelve core chapters (hub); vol 4 adds 卷下 three parts
VOLUMES = [
    (1, 1, 4, "术·上", "捭阖至抵巇"),
    (2, 5, 8, "术·中", "飞钳至摩"),
    (3, 9, 12, "术·下与符言", "权至符言"),
    (4, 13, 15, "卷下", "本经阴符七术至中经"),
]

GLOSSES: dict[str, str] = {
    "捭阖": "开阖有时，审定虚实",
    "反应": "反以观往，覆以察来",
    "内揵": "内情相得，持之令固",
    "抵巇": "察隙乘虚，抵而塞之",
    "飞钳": "飞辞钳势，扬而笼络",
    "忤合": "因势合忤，不泥一主",
    "揣": "揣情察意，量权度能",
    "摩": "摩意试探，切近其情",
    "权": "权衡利害，因事制宜",
    "谋": "阴谋阳略，比之而合",
    "决": "决机断事，当断则断",
    "符言": "安徐正静，持符守位",
    "本经阴符七术": "七术持枢，阴符之本",
    "持枢": "持枢守中，因势制变",
    "中经": "中经察人，权谋实用",
}


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-guiguzi-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}/' | relative_url }}}}"


def series_nav(current_vol: int, max_chapter: int = 15) -> str:
    lines = ["## 系列导航", "", "| 卷 | 篇次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [鬼谷子（导读）— 纵横捭阖]({rel('2026/04/27/guiguzi')}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        if end > max_chapter:
            continue
        slug = f"{vol_date_slug(v)}/guiguzi-{start:02d}-{end:02d}"
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
    gloss = GLOSSES.get(title, "捭阖权谋，因机决断")
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


def volume_post(
    vol: int,
    start: int,
    end: int,
    label: str,
    subtitle: str,
    cards: list,
    include_vol4: bool,
) -> str:
    d = vol_date(vol)
    prev_link = next_link = ""
    vols = [v for v in VOLUMES if v[2] <= 15 or include_vol4]
    vol_idx = next(i for i, v in enumerate(vols) if v[0] == vol)
    if vol_idx > 0:
        ps, pe = vols[vol_idx - 1][1], vols[vol_idx - 1][2]
        pv = vols[vol_idx - 1][0]
        prev_link = (
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(pv)}/guiguzi-{ps:02d}-{pe:02d}')})"
        )
    if vol_idx + 1 < len(vols):
        ns, ne = vols[vol_idx + 1][1], vols[vol_idx + 1][2]
        nv = vols[vol_idx + 1][0]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(nv)}/guiguzi-{ns:02d}-{ne:02d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    scope_note = (
        "十二篇正文 + 卷下三篇"
        if include_vol4 and end > 12
        else ("十二篇正文" if end <= 12 else "卷下三篇")
    )

    body = [
        "---",
        "layout: post",
        f'title: "鬼谷子（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [鬼谷子, 纵横家, 谋略, 鬼谷子系列, {label}]",
        "---",
        "",
        f"**《鬼谷子》原文 · 第 {vol} 卷**",
        f"篇次 **{start}–{end}**（{subtitle}）· 录通行本**{scope_note}**",
        "",
        series_nav(vol, 15 if include_vol4 else 12),
        "",
        f"_方法论、史案与现代场景见 [鬼谷子（导读）]({rel('2026/04/27/guiguzi')})；本篇为**原文**全录（不含陶弘景注）。_",
        "",
        "_底本据 [维基文库](https://zh.wikisource.org/wiki/鬼谷子)（嘉庆十年江都秦氏本，转简体）。_",
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
            f"| 1 | 通读 {start}–{end}，标 3 处「捭 / 阖 / 权 / 决」落点 |",
            "| 2 | 选一史案或谈判场景，用本篇框架复盘 |",
            "| 3 | 与导读篇「读鬼谷子四步法」写一则短断语 |",
            "| 4 | 对照 [孙子兵法]({{ '/2026/06/08/sunzi/' | relative_url }}) 或 [四镜头分析]({{ '/2026/05/25/four-lenses-knowing-choosing/' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [鬼谷子（导读）— 本站笔记]({rel('2026/04/27/guiguzi')})，十二篇结构、术用总纲与史案",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if e > 15 or (e > 12 and not include_vol4):
            continue
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/guiguzi-{s:02d}-{e:02d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与场景对照_",
            "",
        ]
    )
    return "\n".join(body)


def main() -> None:
    chapters = json.loads(DATA.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in chapters}
    posts_dir = ROOT / "_posts"
    include_vol4 = len(chapters) >= 15

    for vol, start, end, label, subtitle in VOLUMES:
        if end > 12 and not include_vol4:
            continue
        batch = [by_id[i] for i in range(start, end + 1)]
        missing = [i for i in range(start, end + 1) if i not in by_id]
        if missing:
            raise SystemExit(f"volume {vol} missing: {missing}")
        out = posts_dir / vol_filename(vol, start, end)
        out.write_text(
            volume_post(vol, start, end, label, subtitle, batch, include_vol4),
            encoding="utf-8",
        )
        print(f"wrote {out.name} ({len(batch)} chapters)")


if __name__ == "__main__":
    main()
