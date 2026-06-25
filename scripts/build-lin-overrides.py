#!/usr/bin/env python3
"""Lin Youqing-aligned divinatory meaning overrides (Part 3). Descriptions use EN source via build-waite-zh.py."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/data/lin-youqing-overrides.json"

# Faithful zh-CN renderings of Waite Part 3 divinatory keywords (大阿卡纳)
MEANING_OVERRIDES: dict[str, dict[str, str]] = {
    "ar00": {
        "meaning_up_zh": "愚蠢、狂热、奢侈、陶醉、谵妄、疯狂、泄密。",
        "meaning_rev_zh": "疏忽、缺席、分散、粗心、冷漠、虚无、虚荣。",
    },
    "ar01": {
        "meaning_up_zh": "技巧、外交、辞令、机敏；疾病、痛苦、损失、灾难、敌人的罗网；自信、意志；求问者（若为男性）。",
        "meaning_rev_zh": "医师、术士、心智疾病、耻辱、不安。",
    },
    "ar02": {
        "meaning_up_zh": "秘密、神秘、尚未揭晓的未来；令求问者关心的女子（若求问者为男性）；求问者本人（若为女性）；沉默、坚韧；神秘、智慧、学识。",
        "meaning_rev_zh": "激情、道德或肉体上的热忱、自负、肤浅的知识。",
    },
    "ar03": {
        "meaning_up_zh": "丰饶、行动、主动、长寿；未知、隐秘；亦有困难、怀疑、无知。",
        "meaning_rev_zh": "光明、真理、纠缠事项的解开、公众欢庆；另一说为，犹豫不决。",
    },
    "ar04": {
        "meaning_up_zh": "稳定、权力、保护、实现；伟人；援助、理性、信念；亦指权威与意志。",
        "meaning_rev_zh": "仁慈、怜悯、信誉；亦使敌人困惑、阻碍、不成熟。",
    },
    "ar05": {
        "meaning_up_zh": "婚姻、联盟、囚禁、奴役；另一说为，慈悲与良善；灵感；求问者所求助之人。",
        "meaning_rev_zh": "社交、默契、和谐、过度仁慈、软弱。",
    },
    "ar06": {
        "meaning_up_zh": "吸引、爱、美、克服考验。",
        "meaning_rev_zh": "失败、愚蠢的图谋；另一说为，婚姻受挫及种种矛盾。",
    },
    "ar07": {
        "meaning_up_zh": "救助、天意；亦指战争、凯旋、僭越、复仇、麻烦。",
        "meaning_rev_zh": "骚乱、争吵、争端、诉讼、失败。",
    },
    "ar08": {
        "meaning_up_zh": "力量、能量、行动、勇气、宽宏；亦指完全的成功与荣誉。",
        "meaning_rev_zh": "专制、滥用权力、软弱、不和，有时甚至是耻辱。",
    },
    "ar09": {
        "meaning_up_zh": "审慎、警觉；尤其指背叛、掩饰、狡诈、腐败。",
        "meaning_rev_zh": "隐瞒、伪装、权谋、恐惧、无理性的谨慎。",
    },
    "ar10": {
        "meaning_up_zh": "命运、时运、成功、提升、幸运、福乐。",
        "meaning_rev_zh": "增长、丰裕、过剩。",
    },
    "ar11": {
        "meaning_up_zh": "公平、正直、廉正、执行力；法律上应得一方之胜诉。",
        "meaning_rev_zh": "法律诸部门、法律纠葛、偏执、偏见、过度严苛。",
    },
    "ar12": {
        "meaning_up_zh": "智慧、审慎、辨别力、考验、牺牲、直觉、占卜、预言。",
        "meaning_rev_zh": "自私、群众、政体。",
    },
    "ar13": {
        "meaning_up_zh": "终结、死亡、毁灭、腐败；对男人而言，失去恩人；对女人而言，诸多矛盾；对少女而言，婚姻计划失败。",
        "meaning_rev_zh": "惰性、昏睡、嗜睡、石化、梦游；希望破灭。",
    },
    "ar14": {
        "meaning_up_zh": "节俭、节制、节约、管理、调和。",
        "meaning_rev_zh": "与教会、宗教、教派、神职人员相关之事，有时亦指将为求问者证婚的神父；亦有分裂、不幸的组合、利益冲突。",
    },
    "ar15": {
        "meaning_up_zh": "蹂躏、暴力、激烈、非凡的努力、强力、宿命；命中注定之事，却未必因此为恶。",
        "meaning_rev_zh": "邪恶的宿命、软弱、狭隘、盲目。",
    },
    "ar16": {
        "meaning_up_zh": "苦难、困顿、贫乏、逆境、灾祸、耻辱、欺骗、毁灭；尤指突如其来的灾祸。",
        "meaning_rev_zh": "据一说，程度较轻时亦有压迫、监禁、暴政。",
    },
    "ar17": {
        "meaning_up_zh": "损失、失窃、匮乏、遗弃；另一说为，希望与光明前景。",
        "meaning_rev_zh": "傲慢、高傲、无能。",
    },
    "ar18": {
        "meaning_up_zh": "隐藏的敌人、危险、诽谤、黑暗、恐怖、欺骗、神秘力量、谬误。",
        "meaning_rev_zh": "不稳定、反复无常、沉默、较轻程度的欺骗与谬误。",
    },
    "ar19": {
        "meaning_up_zh": "物质幸福、美满婚姻、知足。",
        "meaning_rev_zh": "意义略减的同样含义。",
    },
    "ar20": {
        "meaning_up_zh": "地位改变、更新、结果。另一说为，诉讼导致的全然损失。",
        "meaning_rev_zh": "软弱、怯懦、单纯；亦指审议、决定、判决。",
    },
    "ar21": {
        "meaning_up_zh": "稳操胜券、报偿、旅程、路线、移民、远行、迁居。",
        "meaning_rev_zh": "惰性、固执、停滞、恒久不变。",
    },
}


def main() -> None:
    payload = {
        "reference": {
            "title": "韦特塔罗图像解读秘钥【新译完整版】",
            "original": "The Pictorial Key to the Tarot",
            "author": "A. E. Waite",
            "translator": "林侑青",
            "publisher": "地平线文化",
            "year": 2024,
            "isbn": "9786269821334",
            "urls": {
                "publisher": "https://www.andbooks.com.tw/book.php?book_sn=3782",
                "ebook": "https://www.bookwalker.com.tw/product/198978",
            },
            "note": "本书第三部分为占卜牌义参考；牌面描述与全文译出均据韦特英文原著。",
        },
        "glossary": {
            "Greater Arcana": "大阿卡纳",
            "Trumps Major": "大阿卡纳",
            "Minor Arcana": "小阿卡纳",
            "Querent": "求问者",
            "another reading": "另一说",
            "bewrayment": "泄密",
            "distribution": "分散",
            "nullity": "虚无",
        },
        "cards": MEANING_OVERRIDES,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(MEANING_OVERRIDES)} major-arcana meaning overrides)")


if __name__ == "__main__":
    main()
