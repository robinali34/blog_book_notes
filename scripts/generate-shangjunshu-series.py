#!/usr/bin/env python3
"""Generate Shangjunshu 24-chapter series posts from assets/data/shangjunshu-jing.json."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/shangjunshu-jing.json"
SERIES_START = date(2026, 5, 14)

VOLUMES = [
    (1, 1, 6, "卷一·上", "更法至算地"),
    (2, 7, 12, "卷二·三", "开塞至兵守"),
    (3, 13, 18, "卷三·四", "靳令至境内"),
    (4, 19, 24, "卷五", "弱民至定分"),
]

GLOSSES: dict[str, str] = {
    "更法": "便国不法古，变法正当性",
    "垦令": "垦荒令，重农抑末",
    "农战": "农战为本，壹赏壹刑",
    "去强": "去民之强，弱私强公",
    "说民": "说民之术，什伍连坐",
    "算地": "算地知民，国力底盘",
    "开塞": "开塞之道，赏刑之要",
    "壹言": "壹言为教，明法令",
    "错法": "错法任贤，因任授官",
    "战法": "战法十过，慎战之戒",
    "立本": "立本在农，兵守在赏",
    "兵守": "兵守之法，守战之要",
    "靳令": "靳令行禁，壹教之本",
    "修权": "修权信赏，君主之柄",
    "徕民": "徕民实邑，招徕之策",
    "赏刑": "信赏必罚，壹赏壹刑",
    "画策": "画策庙算，变法总纲",
    "境内": "境内之法，户籍什伍",
    "弱民": "弱民强国，抑私论",
    "外内": "外内之别，重农战轻末利",
    "君臣": "君臣之分，勿使臣擅",
    "禁使": "禁使奸私，防壅蔽",
    "慎法": "慎法无刑，法之信用",
    "定分": "定分守职，名分之本",
}


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-shangjunshu-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}/' | relative_url }}}}"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 篇次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [商君书（导读）— 变法强国]({rel('2026/05/13/shangjunshu')}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/shangjunshu-{start:02d}-{end:02d}"
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
    gloss = GLOSSES.get(title, "变法耕战，信赏必罚")
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
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(vol - 1)}/shangjunshu-{ps:02d}-{pe:02d}')})"
        )
    if vol < 4:
        ns, ne = VOLUMES[vol][1], VOLUMES[vol][2]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(vol + 1)}/shangjunshu-{ns:02d}-{ne:02d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "商君书（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [商君书, 商鞅, 法家, 先秦, 变法, 商君书系列, {label}]",
        "---",
        "",
        f"**《商君书》原文 · 第 {vol} 卷**",
        f"篇次 **{start}–{end}**（{subtitle}）· 录通行本**二十四篇原文**（刑约、御盗二篇亡）",
        "",
        series_nav(vol),
        "",
        f"_方法论、史案与现代对照见 [商君书（导读）]({rel('2026/05/13/shangjunshu')})；本篇为**原文**全录。_",
        "",
        "_底本据 [维基文库](https://zh.wikisource.org/wiki/商君書)（《指海》本五卷，转简体；刑约第十六、御盗第二十一篇亡不录）。_",
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
            f"| 1 | 通读 {start}–{end}，标 3 处「更法 / 赏刑 / 农战」落点 |",
            "| 2 | 选一变法史案，用本篇框架复盘 |",
            "| 3 | 与导读篇「读商君四步法」写一则制度/变革短断语 |",
            "| 4 | 对照 [韩非子]({{ '/2026/05/02/hanfeizi/' | relative_url }}) 或 [管理的本质]({{ '/2026/06/02/management-essence-interest-exchange/' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [商君书（导读）— 本站笔记]({rel('2026/05/13/shangjunshu')})，八大专题、变法史案与现代映射",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/shangjunshu-{s:02d}-{e:02d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与变革对照_",
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
