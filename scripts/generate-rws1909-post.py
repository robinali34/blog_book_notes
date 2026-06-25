#!/usr/bin/env python3
"""Generate Rider-Waite 1909 tarot reference post with full Waite Pictorial Key meanings."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_posts/2026-04-28-rider-waite-1909-waite-tarot.md"
DATA = ROOT / "assets/data/waite-pictorial-key.json"
DATA_ZH = ROOT / "assets/data/waite-pictorial-key-zh.json"
LIN = ROOT / "assets/data/lin-youqing-overrides.json"
IMG = "/assets/images/tarot/rws1909"

LIN_GLOSSARY = [
    ("大东方", "格兰德·奥连特"),
    ("特朗普少校", "大阿卡纳"),
    ("大秘仪牌", "大阿卡纳"),
    ("大秘仪", "大阿卡纳"),
    ("心理赌博", "心灵赌博"),
    ("纸牌占卜手册", "《占卜手册》"),
    ("另一篇读物", "另一说"),
    ("另一种解读", "另一说"),
    ("另一个帐户", "另一说"),
    ("，如果是男性", "（若求问者为男性）"),
    ("泄露。", "泄密。"),
    ("、泄露", "、泄密"),
    ("、分配、", "、分散、"),
    ("、空虚、", "、虚无、"),
    ("日日长度", "长寿"),
    ("叛国、", "背叛、"),
    ("、政策、", "、权谋、"),
    ("精神疾病", "心智疾病"),
    ("求索者", "求问者"),
    ("室内之光", "内在之光"),
    ("谬误。", "错误。"),
    ("较小程度的欺骗和错误", "较轻程度的欺骗与错误"),
]

MAJOR = [
    (0, "0", "愚者", "The Fool", "fool", "ar00"),
    (1, "I", "魔术师", "The Magician", "magician", "ar01"),
    (2, "II", "女祭司", "The High Priestess", "high-priestess", "ar02"),
    (3, "III", "皇后", "The Empress", "empress", "ar03"),
    (4, "IV", "皇帝", "The Emperor", "emperor", "ar04"),
    (5, "V", "教皇", "The Hierophant", "hierophant", "ar05"),
    (6, "VI", "恋人", "The Lovers", "lovers", "ar06"),
    (7, "VII", "战车", "The Chariot", "chariot", "ar07"),
    (8, "VIII", "力量", "Fortitude", "strength", "ar08"),
    (9, "IX", "隐者", "The Hermit", "hermit", "ar09"),
    (10, "X", "命运之轮", "Wheel Of Fortune", "wheel-of-fortune", "ar10"),
    (11, "XI", "正义", "Justice", "justice", "ar11"),
    (12, "XII", "倒吊人", "The Hanged Man", "hanged-man", "ar12"),
    (13, "XIII", "死神", "Death", "death", "ar13"),
    (14, "XIV", "节制", "Temperance", "temperance", "ar14"),
    (15, "XV", "恶魔", "The Devil", "devil", "ar15"),
    (16, "XVI", "塔", "The Tower", "tower", "ar16"),
    (17, "XVII", "星星", "The Star", "star", "ar17"),
    (18, "XVIII", "月亮", "The Moon", "moon", "ar18"),
    (19, "XIX", "太阳", "The Sun", "sun", "ar19"),
    (20, "XX", "审判", "The Last Judgment", "judgement", "ar20"),
    (21, "XXI", "世界", "The World", "world", "ar21"),
]

MINOR_SUIT = [
    ("wands", "权杖", "Wands", "火", "行动、事业、热情、创造", "wa"),
    ("cups", "圣杯", "Cups", "水", "情感、关系、直觉、灵性", "cu"),
    ("swords", "宝剑", "Swords", "风", "思维、冲突、真相、决策", "sw"),
    ("pentacles", "星币", "Pentacles", "土", "金钱、身体、工作、物质", "pe"),
]

MINOR_NUM = [
    (1, "ace", "王牌"),
    (2, "02", "二"),
    (3, "03", "三"),
    (4, "04", "四"),
    (5, "05", "五"),
    (6, "06", "六"),
    (7, "07", "七"),
    (8, "08", "八"),
    (9, "09", "九"),
    (10, "10", "十"),
    (11, "page", "侍从"),
    (12, "knight", "骑士"),
    (13, "queen", "皇后"),
    (14, "king", "国王"),
]

COURT_SUFFIX = {11: "pa", 12: "kn", 13: "qu", 14: "ki"}


def lin_reference() -> dict:
    if not LIN.exists():
        return {}
    return json.loads(LIN.read_text(encoding="utf-8")).get("reference", {})


def apply_lin_glossary(text: str) -> str:
    for old, new in LIN_GLOSSARY:
        text = text.replace(old, new)
    return text


def load_cards() -> dict[str, dict]:
    en = {c["name_short"]: c for c in json.loads(DATA.read_text(encoding="utf-8"))["cards"]}
    zh = {c["name_short"]: c for c in json.loads(DATA_ZH.read_text(encoding="utf-8"))["cards"]}
    lin_cards = {}
    if LIN.exists():
        lin_cards = json.loads(LIN.read_text(encoding="utf-8")).get("cards", {})
    merged = {}
    for code, card in en.items():
        z = zh.get(code, {})
        lin = lin_cards.get(code, {})
        merged[code] = {
            **card,
            "meaning_up_zh": apply_lin_glossary(
                lin.get("meaning_up_zh") or z.get("meaning_up_zh") or card["meaning_up"]
            ),
            "meaning_rev_zh": apply_lin_glossary(
                lin.get("meaning_rev_zh") or z.get("meaning_rev_zh") or card["meaning_rev"]
            ),
            "desc_zh": apply_lin_glossary(
                z.get("desc_zh") or card.get("desc", "")
            ),
        }
    return merged


def minor_code(prefix: str, n: int) -> str:
    if n == 1:
        return f"{prefix}ac"
    if n >= 11:
        return f"{prefix}{COURT_SUFFIX[n]}"
    return f"{prefix}{n:02d}"


def esc(text: str) -> str:
    return text.replace("|", "\\|").strip()


def fig(path: str, alt: str, cap: str, *, card: bool = False) -> str:
    cls = "diagram-figure tarot-card-figure" if card else "diagram-figure"
    img_attrs = (
        'class="tarot-card-img" width="110" height="191" '
        if card
        else ""
    )
    return f"""<figure class="{cls}">
<img {img_attrs}src="{{{{ '{IMG}/{path}' | relative_url }}}}" alt="{alt}" loading="lazy" />
<figcaption>{cap}</figcaption>
</figure>"""


def blockquote(text: str) -> str:
    text = esc(text)
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not parts:
        parts = [text]
    return "\n\n".join("\n".join(f"> {line}" for line in p.split("\n")) for p in parts)


def meanings_block(card: dict, *, include_desc: bool = False) -> str:
    up = esc(card["meaning_up_zh"]).replace("\n", " ")
    rev = esc(card["meaning_rev_zh"]).replace("\n", " ")
    lines = [
        '<div class="tarot-meanings-compact">',
        f'<div class="tarot-meaning-upright"><span class="tarot-meaning-label">正位</span>{up}</div>',
        f'<div class="tarot-meaning-reversed"><span class="tarot-meaning-label">逆位</span>{rev}</div>',
        "</div>",
    ]
    desc = card.get("desc_zh") or ""
    if include_desc and desc.strip():
        lines.extend(["", "**牌面描述**", "", blockquote(desc)])
    return "\n".join(lines)


def major_section(by_short: dict[str, dict]) -> str:
    lines = [
        "## 大阿卡纳 — 22 张全解（韦特牌义）",
        "",
        "_编号采用韦特版：力量 VIII、正义 XI；愚者为 0。以下 **正位 / 逆位 / 牌面描述** 均为 A. E. Waite《图解塔罗》*The Pictorial Key to the Tarot*（1910）**据英文原著译出之完整中文**，大阿卡纳占卜牌义并对照林侑青译《韦特塔罗图像解读秘钥》（2024）校正术语，未作删节。_",
        "",
    ]
    for idx, num, zh, en, slug, code in MAJOR:
        card = by_short[code]
        path = f"major/{idx:02d}-{slug}.jpg"
        lines.append(f"### {num} · {zh}（{en}）")
        lines.append("")
        lines.append(fig(path, f"{zh} {en}", f"图 — {zh}（RWS 1909）", card=True))
        lines.append("")
        lines.append(meanings_block(card, include_desc=True))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def minor_section(by_short: dict[str, dict]) -> str:
    lines = [
        "## 小阿卡纳 — 56 张全解",
        "",
        "_韦特与史密斯首次为全部数字牌绘制场景。以下牌义与牌面描述均据原著英文**原义译出**。_",
        "",
    ]
    for key, zh_suit, en_suit, elem, domain, prefix in MINOR_SUIT:
        lines.append(f"### {zh_suit} {en_suit}（{elem} · {domain}）")
        lines.append("")
        for n, _, rank_zh in MINOR_NUM:
            code = minor_code(prefix, n)
            card = by_short[code]
            en_name = card["name"]
            zh_name = f"{zh_suit}{rank_zh}" if n > 1 or rank_zh == "王牌" else f"{zh_suit}王牌"
            if n >= 11:
                zh_name = f"{zh_suit}{rank_zh}"
            path = f"minor/{key}-{n:02d}.jpg"
            lines.append(f"#### {zh_name} · {en_name}")
            lines.append("")
            lines.append(fig(path, en_name, f"图 — {en_name}（RWS 1909）", card=True))
            lines.append("")
            lines.append(meanings_block(card, include_desc=True))
            lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def intro() -> str:
    return f"""---
layout: post
title: "Rider-Waite 1909 韦特塔罗 — 全牌解析与用法"
date: 2026-04-28 14:00:00 -0000
categories: tarot reference
lang: zh-CN
tags: [塔罗, Rider-Waite, 韦特, A.E.Waite, Pamela Colman Smith, 1909, 牌义]
---

**Rider-Waite-Smith Tarot（1909）**  
作者：**Arthur Edward Waite**（亚瑟·爱德华·韦特）· 绘师：**Pamela Colman Smith**（帕梅拉·科尔曼·史密斯）· 出版：**William Rider & Son**，伦敦，1909 年 12 月

> 史上第一副**全部 78 张牌均有场景插图**的塔罗牌。市面所称「韦特塔罗」「Rider Tarot」「Tarot original 1909」多指此系谱的再版或 1909 复刻本。

**关联入门笔记**：[塔罗牌 — 新手入门笔记]({{{{ '/2026/04/30/tarot-getting-started.html' | relative_url }}}})

---

## 牌组背景

| 项目 | 说明 |
|------|------|
| **作者** | A. E. Waite（1857–1942），英国神秘学家，Golden Dawn 成员 |
| **绘师** | Pamela Colman Smith「Pixie」（1878–1951），受 Waite 指导构图 |
| **首版** | 1909 年 12 月，Rider & Son，伦敦 |
| **历史意义** | 小阿卡纳数字牌首次有完整叙事画面，影响此后几乎所有塔罗设计 |
| **编号特点** | 力量 VIII、正义 XI（与马赛系相反）；愚者编号 0 |
| **1909 原背** | 玫瑰与百合（Roses and Lilies）图案 |
| **牌义来源** | *The Pictorial Key to the Tarot*（1910）— **中文全译，未删节** |
| **中文参考** | 林侑青译《韦特塔罗图像解读秘钥》【新译完整版】（地平线文化，2024，ISBN 9786269821334） |

{% include tarot-structure-diagram.html caption="图 0 — 大阿卡纳 22 + 小阿卡纳 56（权杖/圣杯/宝剑/星币各 14）" %}

### 市面常见版本

| 版本 | 特点 |
|------|------|
| **Tarot original 1909 / Centennial** | 贴近首版配色与牌背，收藏与学习常用 |
| **Rider Tarot Deck（US Games）** | 全球流通最广的韦特系标准版 |
| **Radiant / Universal / Premier Waite** | 同系谱，色调或尺寸略异 |
| **Smith-Waite Centennial Edition** | US Games 2010 年前后推出的 1909 复刻 |

本文牌面图来自 Wikimedia Commons 的 **RWS1909** 扫描系列（公有领域）。牌义与牌面描述英文底本来自 [tarot-api](https://github.com/ekelen/tarot-api) 所辑 *Pictorial Key* 原文，**据原义译为中文**；大阿卡纳占卜牌义并对照**林侑青**译《[韦特塔罗图像解读秘钥](https://www.andbooks.com.tw/book.php?book_sn=3782)》（地平线文化，2024）校正术语。

---

## 韦特怎么用牌（《图解塔罗》要旨）

韦特在 *The Pictorial Key to the Tarot*（1910）第二部分阐述占卜方法，核心如下。

### 洗牌与切牌

1. 将 78 张牌全部反转混合，**意念集中于所问之事**。
2. 用**左手**切牌（韦特沿袭当时惯例：左手属「接收」）。
3. 可自己抽牌，也可由求问者抽牌；韦特认为**解牌者**应专注读象。

### 指示牌（Significator）

韦特建议先选定一张代表求问者的牌，置于牌阵中央或一旁：

| 对象 | 韦特建议指示牌 |
|------|----------------|
| 浅色头发年轻男性 | 圣杯骑士 |
| 深色头发年轻男性 | 权杖骑士 |
| 浅色头发成熟男性 | 国王（任意花色的国王，或按语境） |
| 深色头发成熟男性 | 星币国王 |
| 浅色头发年轻女性 | 圣杯侍从 |
| 深色头发年轻女性 | 权杖侍从 |
| 浅色头发成熟女性 | 圣杯皇后 |
| 深色头发成熟女性 | 星币皇后 |

_现代实践中也常简化为：按直觉选一张宫廷牌或大阿卡纳代表当事人，不必拘泥发色。_

### 正位与逆位

韦特在书中为每张牌给出正位与逆位牌义。逆位并非「变坏」，而是能量阻滞、内化或过度。以下 78 张牌列出**原著完整中文译文**。

### 凯尔特十字（Celtic Cross）

韦特推广的十张牌阵，至今仍是最常用的深度牌阵之一：

| 位置 | 含义 |
|------|------|
| 1 中心 | 现状 / 核心课题 |
| 2 横叠 | 交叉影响 / 助力或阻力 |
| 3 上 | 理想或意识目标 |
| 4 下 | 根基 / 潜意识 |
| 5 左 | 过去 |
| 6 右 | 近未来趋势 |
| 7–10 列 | 自我、环境、希望/恐惧、结果 |

### 其他用法

| 方法 | 说明 |
|------|------|
| **每日一牌** | 晨间抽一张，晚间对照省思 |
| **三张牌** | 过去 / 现在 / 未来（或情境 / 行动 / 结果） |
| **只读大阿卡纳** | 韦特时代亦常见；22 张原型适合人生阶段议题 |

---

"""


def outro() -> str:
    ref = lin_reference()
    lin_row = ""
    if ref:
        pub_url = ref.get("urls", {}).get("publisher", "")
        lin_row = (
            f"| 《{ref.get('title', '韦特塔罗图像解读秘钥')}》— "
            f"林侑青译 | 韦特原著权威中译本（{ref.get('publisher', '地平线文化')}，"
            f"{ref.get('year', 2024)}，ISBN {ref.get('isbn', '')}）"
            + (f"；[出版页]({pub_url})" if pub_url else "")
            + " |\n"
        )
    return f"""
## 学习建议

| 阶段 | 做法 |
|------|------|
| 1 | 通读大阿卡纳 22 张，对照画面与韦特牌义 |
| 2 | 按权杖→圣杯→宝剑→星币顺序学小阿卡纳 |
| 3 | 每日一牌 + 写笔记，记录正逆位与当日事件 |
| 4 | 熟练后试凯尔特十字，注意位置逻辑而非死记 |

## 延伸阅读

| 资源 | 说明 |
|------|------|
| *The Pictorial Key to the Tarot* — A. E. Waite | 韦特原著，牌义权威来源 |
{lin_row}| *78 Degrees of Wisdom* — Rachel Pollack | 现代经典深度解读 |
| [入门笔记]({{{{ '/2026/04/30/tarot-getting-started.html' | relative_url }}}}) | 本博客塔罗学习起点 |

## 图例说明

牌面插图：Wikimedia Commons **RWS1909** 系列。牌义与描述：《图解塔罗》（1910）据英文原著原义译出；大阿卡纳占卜牌义参照林侑青译本术语校正。

---

_全 78 张韦特牌义中文译本 — 配合 Tarot original 1909 使用。_
"""


def main():
    by_short = load_cards()
    body = intro() + major_section(by_short) + minor_section(by_short) + outro()
    OUT.write_text(body, encoding="utf-8")
    print(f"Wrote {OUT} ({len(body)} chars, ~{body.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
