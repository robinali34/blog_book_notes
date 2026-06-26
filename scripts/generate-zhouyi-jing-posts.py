#!/usr/bin/env python3
"""Generate Zhouyi jing (64 hexagram) series posts from assets/data/zhouyi-jing.json."""

from __future__ import annotations

import json
from pathlib import Path

from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets/data/zhouyi-jing.json"
HUB_SLUG = "2026-05-07-zhouyi"
SERIES_START = date(2026, 5, 20)

# One-line glosses (from site overview + common readings)
GLOSSES: dict[str, str] = {
    "乾": "自强不息，亢则有悔",
    "坤": "厚德载物，顺而不迷",
    "屯": "草创维艰，宜建侯",
    "蒙": "启蒙教化，果行育德",
    "需": "有孚光亨，利涉大川",
    "讼": "不可终讼，宜和",
    "师": "容民畜众，贞丈人吉",
    "比": "亲比团结，先王以建万国",
    "小畜": "密云不雨，尚往则亨",
    "履": "履虎尾，慎行则吉",
    "泰": "小往大来，通泰",
    "否": "大人否亨，守正待变",
    "同人": "同人于野，利涉大川",
    "大有": "元亨，遏恶扬善",
    "谦": "谦谦君子，卑以自牧",
    "豫": "和乐之时，亦防骄逸",
    "随": "随时而动，元亨",
    "蛊": "整饬腐败，先甲后甲",
    "临": "教思无穷，容保民",
    "观": "观国之光，省方观民",
    "噬嗑": "明罚敕法，利用狱",
    "贲": "文饰有度，小利有攸往",
    "剥": "剥落衰微，不利有攸往",
    "复": "反复其道，七日来复",
    "无妄": "无妄之灾，先王以茂对天",
    "大畜": "止健，养贤",
    "颐": "养正，慎言语节饮食",
    "大过": "栋桡，独立不惧",
    "坎": "习坎，有孚维心亨",
    "离": "明两作，大人以继明照四方",
    "咸": "感而遂通，男下女吉",
    "恒": "恒久之道，利有攸往",
    "遁": "退避守正，小利贞",
    "大壮": "壮勿用，君子以非礼弗履",
    "晋": "进明出地上，自昭明德",
    "明夷": "晦其明，内难正志",
    "家人": "正家，女贞",
    "睽": "乖异中求同，小事吉",
    "蹇": "蹇难之时，反身修德",
    "解": "险难解散，赦过宥罪",
    "损": "损下益上，损盈益虚",
    "益": "损上益下，民说无疆",
    "夬": "决而能和，扬于王庭",
    "姤": "遇合，女壮勿用",
    "萃": "聚而守正，除戎器戒不虞",
    "升": "柔顺而升，南征吉",
    "困": "困而不失其所亨",
    "井": "井养而不穷，改邑不改井",
    "革": "革故鼎新，己日乃孚",
    "鼎": "正位凝命，大亨以正",
    "震": "恐惧修省，震不丧匕鬯",
    "艮": "止其所当止，思不出其位",
    "渐": "女归吉，渐进之道",
    "归妹": "征凶，无攸利",
    "丰": "丰大，日中则昃",
    "旅": "羁旅慎行，小亨",
    "巽": "巽入，申命行事",
    "兑": "和悦，朋友讲习",
    "涣": "涣散群险，王假有庙",
    "节": "节制有度，苦节不可贞",
    "中孚": "信发于中，豚鱼吉",
    "小过": "小事可过，不可大事",
    "既济": "初吉终乱，慎终如始",
    "未济": "事未终，慎辨物居方",
}

VOLUMES = [
    (1, 1, 8, "上经一", "乾至比"),
    (2, 9, 16, "上经二", "小畜至豫"),
    (3, 17, 24, "上经三", "随至复"),
    (4, 25, 32, "上经末·下经开", "无妄至恒"),
    (5, 33, 40, "下经一", "遁至解"),
    (6, 41, 48, "下经二", "损至井"),
    (7, 49, 56, "下经三", "革至旅"),
    (8, 57, 64, "下经末", "巽至未济"),
]

# Stagger dates from 2026-06-26 (one volume per day)


def vol_date(vol: int) -> date:
    return SERIES_START + timedelta(days=vol - 1)


def vol_date_slug(vol: int) -> str:
    d = vol_date(vol)
    return f"{d.year}/{d.month:02d}/{d.day:02d}"


def vol_filename(vol: int, start: int, end: int) -> str:
    d = vol_date(vol)
    return f"{d.isoformat()}-zhouyi-{start:02d}-{end:02d}.md"


def rel(slug: str) -> str:
    return f"{{{{ '/{slug}.html' | relative_url }}}}"


def hub_link() -> str:
    return rel(f"2026/{HUB_SLUG.split('-', 1)[0]}/{HUB_SLUG.split('-', 2)[2]}")


def volume_slug(vol: int, start: int, end: int) -> str:
    d = vol_date(vol)
    return f"{d.isoformat()}-zhouyi-{start:02d}-{end:02d}"


def series_nav(current_vol: int) -> str:
    lines = ["## 系列导航", "", "| 卷 | 卦次 | 篇目 |", "|----|------|------|"]
    lines.append(
        f"| **导读** | — | [周易（导读）— 观象系辞]({rel('2026/05/07/zhouyi')}) |"
    )
    for v, start, end, label, subtitle in VOLUMES:
        slug = f"{vol_date_slug(v)}/zhouyi-{start:02d}-{end:02d}"
        title = f"经传 {start}–{end}（{subtitle}）"
        if v == current_vol:
            lines.append(f"| **{v}** | {start}–{end} | **{title}** ← 本篇 |")
        else:
            lines.append(f"| {v} | {start}–{end} | [{title}]({rel(slug)}) |")
    lines.append("")
    return "\n".join(lines)


def hexagram_section(g: dict) -> str:
    num = g["id"]
    name = g["name"]
    symbol = g["symbol"]
    lower, upper = g["combination"]
    gloss = GLOSSES.get(name, "察势守位，因时变通")
    lines = [
        f"### {num} · {name} {symbol}",
        "",
        f"**卦象**：{upper}上{lower}下",
        "",
        "**卦辞**",
        "",
        f"> {g['scripture']}",
        "",
        "**爻辞**",
        "",
        "| 爻 | 原文 |",
        "|----|------|",
    ]
    for line in g["lines"]:
        lines.append(f"| {line['name']} | {line['scripture']} |")
    lines.extend(
        [
            "",
            f"**要义**：{gloss}",
            "",
            "---",
            "",
        ]
    )
    return "\n".join(lines)


def volume_post(vol: int, start: int, end: int, section: str, subtitle: str, cards: list) -> str:
    d = vol_date(vol)
    prev_link = next_link = ""
    if vol > 1:
        ps, pe = VOLUMES[vol - 2][1], VOLUMES[vol - 2][2]
        prev_link = f"上一篇：[经传 {ps}–{pe}]({rel(f'{vol_date_slug(vol - 1)}/zhouyi-{ps:02d}-{pe:02d}')})"
    if vol < 8:
        ns, ne = VOLUMES[vol][1], VOLUMES[vol][2]
        next_link = f"下一篇：[经传 {ns}–{ne}]({rel(f'{vol_date_slug(vol + 1)}/zhouyi-{ns:02d}-{ne:02d}')})"

    nav_footer = " · ".join(x for x in [prev_link, next_link] if x)

    body = [
        "---",
        "layout: post",
        f'title: "周易（经传 {start}–{end}）— {subtitle}"',
        f"date: {d.isoformat()} 09:00:00 -0000",
        "categories: philosophy chinese-classics",
        "lang: zh-CN",
        f"tags: [周易, 易经, 六十四卦, 经传, 周易系列, {section}]",
        "---",
        "",
        f"**《周易》经传 · 第 {vol} 卷**",
        f"卦序 **{start}–{end}**（{section}：{subtitle}）· 录《周易》**卦辞、爻辞原文**",
        "",
        series_nav(vol),
        "",
        f"_方法论、起卦、读辞见 [周易（导读）]({rel('2026/05/07/zhouyi')})；本篇为**经部原文**全录。_",
        "",
        "---",
        "",
        f"## 经传 {start}–{end}（{subtitle}）",
        "",
    ]
    for g in cards:
        body.append(hexagram_section(g))
    body.extend(
        [
            "## 读本卷提示",
            "",
            "| 步骤 | 做法 |",
            "|------|------|",
            f"| 1 | 通读 {start}–{end} 卦辞，标一句最熟卦辞 |",
            "| 2 | 选一卦写内外卦（上下卦）与当下事之对照 |",
            "| 3 | 选一爻辞抄录，问：此事宜「潜」还是宜「跃」？ |",
            "| 4 | 与导读篇「势→时→变→行」模板写一则短断语 |",
            "",
            nav_footer,
            "",
            "## 关联阅读",
            "",
            f"- [周易（导读）— 本站笔记]({rel('2026/05/07/zhouyi')})，阴阳八卦、时位、变易、铜钱起卦",
        ]
    )
    for v, s, e, _, sub in VOLUMES:
        if v == vol:
            continue
        slug = f"{vol_date_slug(v)}/zhouyi-{s:02d}-{e:02d}"
        body.append(f"- [经传 {s}–{e}（{sub}）— 本站笔记]({rel(slug)})")
    body.extend(
        [
            "",
            "## 状态",
            "",
            f"在读 — _经传 {start}–{end} 原文录完；随读随补象传与史案_",
            "",
        ]
    )
    return "\n".join(body)


def main() -> None:
    cards = json.loads(DATA.read_text(encoding="utf-8"))
    by_id = {g["id"]: g for g in cards}
    posts_dir = ROOT / "_posts"

    for vol, start, end, section, subtitle in VOLUMES:
        batch = [by_id[i] for i in range(start, end + 1)]
        content = volume_post(vol, start, end, section, subtitle, batch)
        out = posts_dir / vol_filename(vol, start, end)
        out.write_text(content, encoding="utf-8")
        print("wrote", out.name, f"({len(batch)} hexagrams)")


if __name__ == "__main__":
    main()
