#!/usr/bin/env python3
"""Build Chinese translation JSON from Waite Pictorial Key English source."""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "assets/data/waite-pictorial-key.json"
OUT_PATH = ROOT / "assets/data/waite-pictorial-key-zh.json"

# Pre-translate fixed terms so output stays close to Waite's original wording.
GLOSSARY = {
    "Querent": "求问者",
    "querent": "求问者",
    "the Querent": "求问者",
    "the Querent, if male": "求问者（若为男性）",
    "the Querent herself, if female": "求问者本人（若为女性）",
    "the woman who interests the Querent, if male": "令求问者关心的女子（若求问者为男性）",
    "the man to whom the Querent has recourse": "求问者所求助之人",
    "Divinatory Meanings": "占卜牌义",
    "Greater Arcana": "大阿卡纳",
    "Trumps Major": "大阿卡纳",
    "Trump Major": "大阿卡纳",
    "another reading": "另一说",
    "Another account": "另一说",
    "according to another reading": "另一说为",
    "by another account": "另一说为",
    "Grand Orient": "格兰德·奥连特",
    "Instituted Mysteries": "立誓秘仪",
    "Manual of Cartomancy": "《占卜手册》",
    "Holy Spirit": "圣灵",
    "High Priestess": "女祭司",
    "The Empress": "皇后",
    "Fortitude": "力量",
    "bewrayment": "泄密",
    "distribution": "分散",
    "nullity": "虚无",
    "address": "辞令",
    "Magus": "术士",
    "Shekinah": "舍金纳",
    "Binah": "比纳",
    "Malkuth": "马拉赫特",
    "MaIkuth": "马拉赫特",
    "Ogdoad": "八数（奥格多德）",
    "Regina coeli": "天后",
    "Gloria Mundi": "尘世荣光",
    "Sanctum Sanctorum": "至圣所",
    "Crux ansata": "安卡十字",
    "sign of his suit": "所属花色的象征",
    "unsheathed sign of his suit": "出鞘的所属花色象征",
    "Dark young man": "发色深的年轻男子",
    "dark young man": "发色深的年轻男子",
    "A dark young man": "发色深的年轻男子",
    "A dark woman": "发色深的女子",
    "dark woman": "发色深的女子",
    "Dark man": "发色深的男子",
    "dark man": "发色深的男子",
    "Fair young man": "发色浅的年轻男子",
    "Fair man": "发色浅的男子",
    "Good, fair woman": "发色浅、品貌端正的女子",
    "length of days": "长寿",
    "treason": "背叛",
    "policy": "权谋",
    "calumny": "诽谤",
    "privation": "匮乏",
    "bewrayment.": "泄密。",
    "surface knowledge": "肤浅的知识",
    "science.": "学识。",
    "mental disease": "心智疾病",
    "snares of enemies": "敌人的罗网",
    "in a lesser sense": "意义略减",
    "The same in a lesser sense.": "意义略减的同样含义。",
    "flos campi": "野地之花",
    "lilium convallium": "谷中百合",
    "innocentia inviolata": "圣洁不可侵犯",
    "occult forces": "神秘力量",
    "error.": "谬误。",
    "deception and error": "欺骗与谬误",
}

POST_FIXES = [
    ("，如果是男性", "（若求问者为男性）"),
    ("，如果是女性", "（若为女性）"),
    ("演讲、微妙", "辞令、机敏"),
    ("医师、魔法师", "医师、术士"),
    ("、迷惑。", "、泄密。"),
    ("、泄露。", "、泄密。"),
    ("、泄露", "、泄密"),
    ("、分配、", "、分散、"),
    ("、空虚、", "、虚无、"),
    ("日日长度", "长寿"),
    ("叛国、", "背叛、"),
    ("、政策、", "、权谋、"),
    ("另一篇读物", "另一说"),
    ("另一种解读", "另一说"),
    ("另一个帐户", "另一说"),
    ("大东方", "格兰德·奥连特"),
    ("特朗普少校", "大阿卡纳"),
    ("大秘仪牌", "大阿卡纳"),
    ("大秘仪", "大阿卡纳"),
    ("心理赌博", "心灵赌博"),
    ("求索者", "求问者"),
    ("皮肤黝黑", "发色深"),
    ("皮肤黝黑的", "发色深的"),
    ("格洛丽亚·蒙迪", "尘世荣光"),
    ("天王星", "天后"),
    ("仍是处女座", "仍保持处女贞洁"),
    ("西装的", "花色的"),
    ("未出鞘的标志", "出鞘的花色象征"),
    ("生命论", "象征学"),
    ("同居的荣耀", "同在的荣耀"),
    ("麦库斯", "马拉赫特"),
    ("向奥格多德", "向八数（奥格多德）"),
    ("室内之光", "内在之光"),
    ("通俗的解释", "肤浅的解释"),
    ("较小程度的欺骗和错误", "较轻程度的欺骗与错误"),
    ("科学。", "学识。"),
    ("科学、", "学识、"),
    ("稳定、动力", "稳定、权力"),
    ("一个伟大的人", "伟人"),
    ("帮助、推理", "援助、理性"),
    ("也让敌人感到困惑", "亦使敌人困惑"),
    ("仁、慈、信", "仁慈、怜悯、信誉"),
    ("社会，良好的理解", "社交、默契"),
    ("过分仁慈", "过度仁慈"),
    ("救助、天意也包括", "救助、天意；亦指"),
    ("妄自尊大", "僭越"),
    ("谨慎、谨慎", "审慎、警觉"),
    ("欺诈、", "狡诈、"),
    ("命运、财富", "命运、时运"),
    ("幸福。", "福乐。"),
    ("公平、公正、廉洁、执行", "公平、正直、廉正、执行力"),
    ("应得一方的胜利", "应得一方之胜诉"),
    ("所有部门的法律", "法律诸部门"),
    ("法律复杂性", "法律纠葛"),
    ("过度严厉", "过度严苛"),
    ("政治体。", "政体。"),
    ("对于男人来说", "对男人而言"),
    ("对于女人来说", "对女人而言"),
    ("对于女佣来说", "对少女而言"),
    ("节约、节制、节俭、管理、包容", "节俭、节制、节约、管理、调和"),
    ("死亡；", "宿命；"),
    ("苦难、痛苦、贫穷", "苦难、困顿、贫乏"),
    ("丢失、被盗", "损失、失窃"),
    ("傲慢、傲慢", "傲慢、高傲"),
    ("隐藏的敌人、危险、诽谤、黑暗、恐怖、欺骗、神秘力量、错误", "隐藏的敌人、危险、诽谤、黑暗、恐怖、欺骗、神秘力量、谬误"),
    ("物质幸福，婚姻幸福", "物质幸福、美满婚姻"),
    ("在较小的意义上也是如此", "意义略减的同样含义"),
    ("立场的改变", "地位改变"),
    ("软弱、胆怯", "软弱、怯懦"),
    ("保证成功、报酬、航程、航线、移民、飞行、迁居", "稳操胜券、报偿、旅程、路线、移民、远行、迁居"),
    ("纸牌占卜手册", "《占卜手册》"),
    ("《《占卜手册》》", "《占卜手册》"),
    ("“幽灵”标志", "圣灵印记"),
    ("幽灵和主之地", "圣灵和主之地"),
    ("这张卡片", "这张牌"),
    ("该卡片", "该牌"),
    ("一张卡片", "一张牌"),
    ("卡片的角度", "牌的四角"),
    ("占据了卡片", "占据了牌"),
    ("她旁边的卡片", "她旁边的牌"),
    ("爱之卡片", "爱之牌"),
    ("物物交换的卡片", "物物交换的牌"),
    ("回忆的卡片", "回忆之牌"),
    ("联系的卡片", "联系之牌"),
    ("挂着卡片上的剑", "挂着牌上的剑"),
    ("描述了 min 是", "描述毁灭是"),
    ("心灵赌博", "通灵赌博"),
    ("志向文化", "志向之修养"),
    ("转变为八数", "改变为八数"),
    ("惯性、固定性、停滞性、持久性", "惰性、固执、停滞、恒久不变"),
    ("卡片", "牌"),
]


def apply_glossary(text: str) -> str:
    for src in sorted(GLOSSARY, key=len, reverse=True):
        text = text.replace(src, GLOSSARY[src])
    return text


def translate_chunk(text: str, retries: int = 5) -> str:
    if not text or not text.strip():
        return text
    text = apply_glossary(text)
    q = urllib.parse.quote(text[:4500])
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=en&tl=zh-CN&dt=t&q={q}"
    )
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            return "".join(p[0] for p in data[0] if p[0]).strip()
        except Exception:
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"translate failed: {text[:80]}...")


def split_translate(text: str) -> str:
    text = text.strip()
    if len(text) <= 4200:
        return translate_chunk(text)
    chunks, buf, size = [], [], 0
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if size + len(sent) > 3500 and buf:
            chunks.append(" ".join(buf))
            buf, size = [sent], len(sent)
        else:
            buf.append(sent)
            size += len(sent) + 1
    if buf:
        chunks.append(" ".join(buf))
    return "\n\n".join(translate_chunk(c) for c in chunks)


def polish(text: str) -> str:
    text = apply_glossary(text)
    for a, b in POST_FIXES:
        text = text.replace(a, b)
    return text


def main() -> None:
    cards = json.loads(EN_PATH.read_text(encoding="utf-8"))["cards"]
    zh_cards = []
    for i, c in enumerate(cards):
        print(f"[{i + 1}/78] {c['name_short']} {c['name']}")
        zh = dict(c)
        zh["meaning_up_zh"] = polish(split_translate(c["meaning_up"]))
        time.sleep(0.35)
        zh["meaning_rev_zh"] = polish(split_translate(c["meaning_rev"]))
        time.sleep(0.35)
        if c.get("desc"):
            zh["desc_zh"] = polish(split_translate(c["desc"]))
            time.sleep(0.5)
        zh_cards.append(zh)
    payload = {
        "source": (
            "A.E. Waite, The Pictorial Key to the Tarot (1910); "
            "zh-CN 据英文原著译出，术语统一为大阿卡纳/小阿卡纳，并对照林侑青译本校正占卜牌义"
        ),
        "cards": zh_cards,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", OUT_PATH)


def polish_existing() -> None:
    payload = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    for c in payload["cards"]:
        for key in ("meaning_up_zh", "meaning_rev_zh", "desc_zh"):
            if c.get(key):
                c[key] = polish(c[key])
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Polished", OUT_PATH)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--polish-only":
        polish_existing()
    else:
        main()
