#!/usr/bin/env python3
"""Generate 传习录 series posts from assets/data/chuanxilu-jing.json."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/chuanxilu-jing.json"
HUB_SLUG = "2026/06/17/chuanxilu-wang-yangming"
SERIES_START = date(2026, 8, 29)

VOLUMES = [
    (1, 1, 34, "卷上·一", "徐爱录至格物问答"),
    (2, 35, 76, "卷上·二", "上卷问答续"),
    (3, 77, 111, "卷上末·中卷序", "上卷末至中卷开篇"),
    (4, 112, 128, "卷中·一", "答罗整庵等书信"),
    (5, 129, 139, "卷中·二", "答聂文蔚等书信"),
    (6, 140, 190, "卷中下", "中卷末至下卷初"),
    (7, 191, 230, "卷下·一", "九川诸友问答"),
    (8, 231, 254, "卷下·末", "下卷末语录"),
]

GLOSS_KEYWORDS: list[tuple[str, str]] = [
    (r"知行合一|不行不足谓之知", "知行为一，不行不足以为知"),
    (r"致良知|良知", "致良知，扩充本然之明"),
    (r"格物|穷理", "格物在事，为善去恶"),
    (r"诚意|自欺", "诚意无自欺，言行动本"),
    (r"心即理|心外无理", "心即理，理不外求"),
    (r"立志|圣人气象", "立志成德，事上磨练"),
    (r"不动心|省察", "省察克治，不动于心"),
    (r"四句教|无善无恶", "四句教：体用善恶良知格物"),
    (r"来书云", "答书辨析，破支离之弊"),
    (r"问", "友朋问答，事上体认"),
]


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-chuanxilu-{start:03d}-{end:03d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def gloss(entry: dict) -> str:
    blob = entry["title"] + entry["text"][:300]
    for pattern, meaning in GLOSS_KEYWORDS:
        if re.search(pattern, blob):
            return meaning
    vol_gloss = {
        "上": "上卷问答，龙场以来心法初阐",
        "中": "中卷书信，辨析朱陆格物之异",
        "下": "下卷语录，事上磨练与教法",
    }
    return vol_gloss.get(entry["volume"], "事上体认，存天理去人欲")


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 条次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [传习录（导读）— 诚意与边界]({rel(HUB_SLUG)}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/chuanxilu-{start:03d}-{end:03d}"
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


def entry_section(entry: dict) -> str:
    num = entry["id"]
    title = entry["title"]
    vol = entry["volume"]
    gloss_text = gloss(entry)
    body = format_body(entry["text"])
    return "\n".join(
        [
            f"### {num} · {title}",
            "",
            f"**卷**：{vol} · **要义**：{gloss_text}",
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
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(pv)}/chuanxilu-{ps:03d}-{pe:03d}')})"
        )
    if vol_idx + 1 < len(VOLUMES):
        ns, ne = VOLUMES[vol_idx + 1][1], VOLUMES[vol_idx + 1][2]
        nv = VOLUMES[vol_idx + 1][0]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(nv)}/chuanxilu-{ns:03d}-{ne:03d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "传习录（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics psychology",
        "lang: zh-CN",
        f"tags: [传习录, 王阳明, 心学, 传习录系列, {label}]",
        "---",
        "",
        f"**《传习录》原文 · 第 {vol} 卷**",
        f"条次 **{start}–{end}**（{subtitle}）· 录通行本**传习录三卷**",
        "",
        series_nav(vol),
        "",
        f"_方法论、边界栈与场景应用见 [传习录（导读）]({rel(HUB_SLUG)})；本篇为**原文**全录。_",
        "",
        "_底本据 [维基文库](https://zh.wikisource.org/wiki/傳習錄)（上、中、下三卷，转简体）。_",
        "",
        "---",
        "",
        f"## 原文 {start}–{end}（{subtitle}）",
        "",
    ]
    for entry in batch:
        body.append(entry_section(entry))
    body.extend(
        [
            "## 读本卷提示",
            "",
            "| 步骤 | 做法 |",
            "|------|------|",
            f"| 1 | 通读 {start}–{end}，标 3 处「诚意 / 知行 / 良知」落点 |",
            "| 2 | 选一沟通或边界场景，问：言是否诚意、行是否相副？ |",
            "| 3 | 与导读篇「读传习录四步法」写一则短省察 |",
            "| 4 | 对照 [阳明心学（导读）]({{ '/2026/06/22/yangming-xinxue.html' | relative_url }}) 或 [四镜头分析]({{ '/2026/05/25/four-lenses-knowing-choosing.html' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [传习录（导读）— 本站笔记]({rel(HUB_SLUG)})，诚意、省察与边界栈",
            "- [阳明心学（导读）— 本站笔记]({{ '/2026/06/22/yangming-xinxue.html' | relative_url }})，八大专题与四句教",
            "- [《大学问》原文 — 本站笔记]({{ '/2026/09/06/yangming-daxuewen.html' | relative_url }})，纲领一篇",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/chuanxilu-{s:03d}-{e:03d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与事上对照_",
            "",
        ]
    )
    return "\n".join(body)


def main() -> None:
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in entries}
    posts_dir = ROOT / "_posts"

    for vol, start, end, label, subtitle in VOLUMES:
        batch = [by_id[i] for i in range(start, end + 1)]
        missing = [i for i in range(start, end + 1) if i not in by_id]
        if missing:
            raise SystemExit(f"volume {vol} missing entries: {missing}")
        out = posts_dir / vol_filename(vol, start, end)
        out.write_text(volume_post(vol, start, end, label, subtitle, batch), encoding="utf-8")
        print(f"wrote {out.name} ({len(batch)} entries)")


if __name__ == "__main__":
    main()
