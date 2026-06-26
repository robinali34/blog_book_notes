#!/usr/bin/env python3
"""Generate Xunzi 32-chapter series posts from assets/data/xunzi-jing.json."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/xunzi-jing.json"
SERIES_START = date(2026, 5, 11)

VOLUMES = [
    (1, 1, 8, "卷一至八", "劝学至儒效"),
    (2, 9, 16, "卷九至十六", "王制至强国"),
    (3, 17, 24, "卷十七至二十四", "天论至君子"),
    (4, 25, 32, "卷二十五至三十二", "成相至尧问"),
]

GLOSSES: dict[str, str] = {
    "劝学": "学不可以已，积伪成德",
    "修身": "见善修然，见不善惕然",
    "不苟": "君子养心莫善于诚",
    "荣辱": "荣辱之分，义利之辨",
    "非相": "相人不如论德",
    "非十二子": "辨诸子偏蔽，宗仲尼",
    "仲尼": "仲尼之门，五子为臣",
    "儒效": "儒者之功，化民成俗",
    "王制": "王制之本，分定群治",
    "富国": "富国之道，节用裕民",
    "王霸": "王霸之辨，以德服人",
    "君道": "君者仪也，隆礼法而治",
    "臣道": "臣道之要，忠顺而不怠",
    "致士": "致士之方，礼贤下士",
    "议兵": "议兵之要，仁义为本",
    "强国": "强国之术，隆礼重法",
    "天论": "天行有常，不为尧存",
    "正论": "正论刑赏，辟奸除邪",
    "礼论": "礼者分也，养人之欲",
    "乐论": "乐者同也，中和之教",
    "解蔽": "解蔽壹心，虚壹而静",
    "正名": "正名定分，名实相符",
    "性恶": "性恶可化，其善者伪",
    "君子": "君子之行，隆礼法而近仁",
    "成相": "成相之辞，警策为政",
    "赋": "礼义之赋，文质之喻",
    "大略": "大略纲要，杂采荀义",
    "宥坐": "宥坐之鉴，水镜之喻",
    "子道": "子道五孝，事亲之方",
    "法行": "法行不阿，君子之节",
    "哀公": "哀公问政，君道之戒",
    "尧问": "尧问舜禹，择贤传国",
}


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-xunzi-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 篇次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [荀子（导读）— 化性起伪]({rel('2026/06/18/xunzi')}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/xunzi-{start:02d}-{end:02d}"
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
    gloss = GLOSSES.get(title, "化性起伪，隆礼重法")
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
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(vol - 1)}/xunzi-{ps:02d}-{pe:02d}')})"
        )
    if vol < 4:
        ns, ne = VOLUMES[vol][1], VOLUMES[vol][2]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(vol + 1)}/xunzi-{ns:02d}-{ne:02d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "荀子（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [荀子, 荀卿, 儒家, 先秦, 性恶, 礼法, 荀子系列, {label}]",
        "---",
        "",
        f"**《荀子》原文 · 第 {vol} 卷**",
        f"篇次 **{start}–{end}**（{subtitle}）· 录通行本**三十二篇原文**",
        "",
        series_nav(vol),
        "",
        f"_方法论、孟荀对读与现代映射见 [荀子（导读）]({rel('2026/06/18/xunzi')})；本篇为**原文**全录。_",
        "",
        "_底本据 [维基文库](https://zh.wikisource.org/wiki/荀子)（《四部丛刊》本，转简体；杨倞注不录）。_",
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
            f"| 1 | 通读 {start}–{end}，标 3 处「礼 / 法 / 伪」落点 |",
            "| 2 | 选一史案或组织情境，用本篇框架复盘 |",
            "| 3 | 与导读篇「读荀子四步法」写一则教化/制度短断语 |",
            "| 4 | 对照 [韩非子]({{ '/2026/05/02/hanfeizi.html' | relative_url }}) 或 [商君书]({{ '/2026/05/13/shangjunshu.html' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [荀子（导读）— 本站笔记]({rel('2026/06/18/xunzi')})，八大专题、孟荀之辩与现代映射",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/xunzi-{s:02d}-{e:02d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与礼法对照_",
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
