#!/usr/bin/env python3
"""Generate Hanfeizi 55-chapter series posts from assets/data/hanfeizi-jing.json."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/hanfeizi-jing.json"
HUB_SLUG = "2026-05-02-hanfeizi"
SERIES_START = date(2026, 7, 12)

VOLUMES = [
    (1, 1, 7, "卷一", "初见秦至二柄"),
    (2, 8, 14, "卷二", "扬权至奸劫弑臣"),
    (3, 15, 21, "卷三", "亡徵至喻老"),
    (4, 22, 28, "卷四", "说林上至功名"),
    (5, 29, 35, "卷五", "大体至外储说右下"),
    (6, 36, 42, "卷六", "难一至问田"),
    (7, 43, 49, "卷七", "定法至五蠹"),
    (8, 50, 55, "卷八", "显学至制分"),
]

GLOSSES: dict[str, str] = {
    "初见秦": "入秦陈策，存亡之机",
    "存韩": "存韩安秦，地缘政治",
    "难言": "臣道忠言，进退两难",
    "爱臣": "近幸之患，防壅蔽",
    "主道": "南面而治，因任参验",
    "有度": "法度度量，国之根本",
    "二柄": "刑德二柄，制臣之要",
    "扬权": "独擅赏罚，勿使臣擅",
    "八奸": "八奸之术，内控风控",
    "十过": "十过之戒，君主自省",
    "孤愤": "法术难行，士之孤愤",
    "说难": "进言多危，名篇",
    "和氏": "宝玉不售，法不阿贵",
    "奸劫弑臣": "奸臣劫主，弑逆之防",
    "亡徵": "亡国征兆，察微杜渐",
    "三守": "三守之要，君主自守",
    "备内": "备内防变，宫闱之戒",
    "南面": "君主南面，执虚责实",
    "饰邪": "饰邪去奸，名实之辨",
    "解老": "解老子义，道法相通",
    "喻老": "喻老子言，以事证理",
    "说林上": "寓言林上，警策故事",
    "说林下": "寓言林下，警策故事",
    "观行": "观行察人，因任授官",
    "安危": "安危之辨，势位为本",
    "守道": "守道持势，勿失其柄",
    "用人": "用人之道，参验其功",
    "功名": "功名之本，循名责实",
    "大体": "大体之治，无为而治",
    "内储说上": "七术六微，驭臣之术",
    "内储说下": "六微之察，防奸细目",
    "外储说左上": "外储寓言，法术例证",
    "外储说左下": "外储寓言，法术例证",
    "外储说右上": "外储寓言，法术例证",
    "外储说右下": "外储寓言，法术例证",
    "难一": "难一辩难，名实之辩",
    "难二": "难二辩难，法术之辩",
    "难三": "难三辩难，君臣之辩",
    "难四": "难四辩难，势法之辩",
    "难势": "难势篇，势与法辩",
    "问辩": "问辩篇，辩说之难",
    "问田": "问田篇，法势之问",
    "定法": "定法篇，法之常立",
    "说疑": "说疑篇，疑臣之防",
    "诡使": "诡使篇，奸臣之使",
    "六反": "六反篇，六种反态",
    "八说": "八说篇，八种妄说",
    "八经": "八经篇，治国八纲",
    "五蠹": "五蠹篇，蠹国五类",
    "显学": "显学篇，排儒墨",
    "忠孝": "忠孝篇，忠孝之辨",
    "人主": "人主篇，君主之职",
    "饬令": "饬令篇，令行禁止",
    "心度": "心度篇，心术之度",
    "制分": "制分篇，名分制御",
}


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    return f"{vol_date(vol).isoformat()}-hanfeizi-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 篇次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [韩非子（导读）— 法术势]({rel('2026/05/02/hanfeizi')}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/hanfeizi-{start:02d}-{end:02d}"
        title = f"原文 {start}–{end}（{subtitle}）"
        if v == current_vol:
            lines.append(f"| **{v}** | {start}–{end} | **{title}** ← 本篇 |")
        else:
            lines.append(f"| {v} | {start}–{end} | [{title}]({rel(slug)}) |")
    lines.append("")
    return "\n".join(lines)


def format_body(text: str) -> str:
    """Render chapter text as markdown paragraphs."""
    lines: list[str] = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        # Section headers like 一、二、 within 储说 chapters
        if re.match(r"^[一二三四五六七八九十百]+、", para) and len(para) < 80:
            lines.extend(["", f"#### {para}", ""])
        elif re.match(r"^参观[一二三四五六七八九十]+$", para):
            lines.extend(["", f"#### {para}", ""])
        else:
            lines.extend(["", para, ""])
    return "\n".join(lines).strip()


def chapter_section(ch: dict) -> str:
    num = ch["id"]
    title = ch["title"]
    gloss = GLOSSES.get(title, "法术势，因任参验")
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
            f"上一篇：[原文 {ps}–{pe}]({rel(f'{vol_date_slug(vol - 1)}/hanfeizi-{ps:02d}-{pe:02d}')})"
        )
    if vol < 8:
        ns, ne = VOLUMES[vol][1], VOLUMES[vol][2]
        next_link = (
            f"下一篇：[原文 {ns}–{ne}]({rel(f'{vol_date_slug(vol + 1)}/hanfeizi-{ns:02d}-{ne:02d}')})"
        )
    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "韩非子（原文 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [韩非子, 法家, 韩非, 先秦, 韩非子系列, {label}]",
        "---",
        "",
        f"**《韩非子》原文 · 第 {vol} 卷**",
        f"篇次 **{start}–{end}**（{subtitle}）· 录通行本**五十五篇原文**",
        "",
        series_nav(vol),
        "",
        f"_方法论、史案与组织治理对照见 [韩非子（导读）]({rel('2026/05/02/hanfeizi')})；本篇为**原文**全录。_",
        "",
        f"_底本据 [ctext.org](https://ctext.org/hanfeizi/zhs)（《四部丛刊初编》本，简体）。_",
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
            f"| 1 | 通读 {start}–{end}，标 3 处「法 / 术 / 势」落点 |",
            "| 2 | 选一寓言或史案，问：规则是否公开一致？ |",
            "| 3 | 与导读篇「读韩非四步法」写一则组织/制度短断语 |",
            "| 4 | 对照 [商君书]({{ '/2026/05/13/shangjunshu.html' | relative_url }}) 或 [管理的本质]({{ '/2026/06/02/management-essence-interest-exchange.html' | relative_url }}) |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [韩非子（导读）— 本站笔记]({rel('2026/05/02/hanfeizi')})，法术势、八奸、说难与史案",
        ]
    )
    for v, s, e, _label, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/hanfeizi-{s:02d}-{e:02d}"
        body.append(f"- [原文 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _原文 {start}–{end} 录完；随读随补批注与治理对照_",
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
