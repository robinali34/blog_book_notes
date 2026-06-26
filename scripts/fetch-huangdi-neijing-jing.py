#!/usr/bin/env python3
"""Fetch 黄帝内经 素问81篇 + 灵枢81篇 from Wikisource into JSON (simplified, main text)."""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote

try:
    import opencc
except ImportError:
    opencc = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/data/huangdi-neijing-jing.json"

SUWEN_NAMES = [
    "上古天真论", "四气调神大论", "生气通天论", "金匮真言论", "阴阳应象大论", "阴阳离合论", "阴阳别论",
    "灵兰秘典论", "六节藏象论", "五脏生成论", "五脏别论", "异法方宜论", "移精变气论", "汤液醪醴论", "玉版论要论", "诊要经终论",
    "脉要精微论", "平人气象论", "玉机真藏论", "三部九候论", "经脉别论", "藏气法时论", "宣明五气论", "血气形志论", "宝命全形论",
    "八正神明论", "离合真邪论", "通评虚实论", "太阴阳明论", "阳明脉解", "热论", "刺热", "评热病论", "逆调论", "疟论", "刺疟",
    "气厥论", "咳论", "举痛论", "腹中论", "刺腰痛论", "风论", "痹论", "痿论", "厥论", "病能论", "奇病论", "大奇论", "脉解",
    "刺要论", "刺齐论", "刺禁论", "刺志论", "针解", "长刺节论", "皮部论", "经络论", "气穴论", "气府论", "骨空论", "水热穴论",
    "调经论", "缪刺论", "四时刺逆从论", "标本病传论", "天元纪大论", "五运行大论", "六微旨大论", "气交变大论", "五常政大论",
    "六元正纪大论", "刺法论", "本病论", "至真要大论", "著至教论", "示从容论", "疏五过论", "徵四失论", "阴阳类论", "方盛衰论", "解精微论",
]

LING_NAMES = [
    "九针十二原", "本输", "小针解", "邪气藏府病形", "根结", "寿天刚柔", "官针", "本神", "终始", "经脉",
    "经别", "经水", "经筋", "骨度", "五十营", "营气", "脉度", "营卫生会", "四时气", "五邪",
    "寒热病", "癫狂病", "热病", "厥病", "病本", "杂病", "周痹", "口问", "师传", "决气",
    "肠胃", "平人绝谷", "海论", "五乱", "胀论", "五癃精液别", "五阅五使", "逆顺肥瘦", "血络", "阴阳清浊",
    "阴阳系日月", "病传", "淫邪发梦", "顺气一日分为四时", "外揣", "五变", "本藏", "禁服", "五色", "论勇",
    "背输", "卫气", "论痛", "天年", "逆顺", "五味", "水胀", "贼风", "卫气失常", "玉版",
    "五禁", "动输", "五味论", "阴阳二十五人", "五音五味", "百病始生", "行针", "上膈", "忧恚无言", "寒热",
    "邪客", "通天", "官能", "论疾诠尺", "刺节真邪", "卫气行", "九宫八风", "九针论", "岁露论", "大惑论", "痈疽",
]

SUWEN_VOL_CN = [
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "二十一", "二十二", "二十三", "二十四",
]

LING_VOL_CN = [
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二",
]

CHAPTER_RE = re.compile(r"[\u4e00-\u9fff]{2,30}篇第[一二三四五六七八九十百]+")
LOST_SUWEN = {72, 73}
LOST_NOTE = "（王冰注本此篇亡。四库全书本仅存篇目；宋以来有补佚本流传。）"


def to_simplified(text: str) -> str:
    if opencc is None:
        return text
    return opencc.OpenCC("t2s").convert(text)


def cn_num(s: str) -> int:
    digits = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + (digits.get(s[1], 0) if len(s) > 1 else 0)
    if "十" in s:
        a, b = s.split("十", 1)
        tens = digits.get(a, 1) if a else 1
        ones = digits.get(b, 0) if b else 0
        return tens * 10 + ones
    total = 0
    for ch in s:
        total = total * 10 + digits[ch]
    return total


def parse_chapter_num(title: str) -> int | None:
    m = re.search(r"篇第([一二三四五六七八九十百]+)$", title)
    return cn_num(m.group(1)) if m else None


def clean_text(text: str) -> str:
    text = re.sub(r"〈[^〉]*〉", "", text)
    text = re.sub(r"新校正云[^。；]*[。；]", "", text)
    return re.sub(r" +", " ", text).strip()


def opening_phrase(text: str, max_len: int = 14) -> str:
    line = text.replace("\n", "").strip()
    for sep in "。；，：":
        if sep in line:
            line = line.split(sep)[0]
            break
    if len(line) > max_len:
        return line[:max_len] + "…"
    return line


def fetch_html(path: str) -> str:
    url = "https://zh.wikisource.org/wiki/" + quote(path)
    req = urllib.request.Request(url, headers={"User-Agent": "blog-book-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def paragraph_blob(html: str) -> str:
    parts: list[str] = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", html, re.S):
        t = to_simplified(re.sub(r"<[^>]+>", "", p).strip())
        if not t or t.startswith("此作品") or "Public domain" in t or t.startswith("@media"):
            continue
        parts.append(t)
    return "\n".join(parts)


def split_by_pian(blob: str) -> dict[int, str]:
    matches = list(CHAPTER_RE.finditer(blob))
    out: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = parse_chapter_num(m.group())
        if not num or num > 81:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(blob)
        body = clean_text(blob[m.end() : end])
        if len(body) > 80:
            out[num] = body
    return out


def fetch_clean_suwen_volume(vol_index: int) -> dict[int, str]:
    cn = SUWEN_VOL_CN[vol_index - 1]
    html = fetch_html(f"黃帝內經/素問第{cn}卷")
    pattern = (
        r'<div class="mw-heading mw-heading2">(.*?)</div>\s*'
        r"(.*?)(?=<div class=\"mw-heading mw-heading2\">|</div>\s*<div id=\"catlinks\")"
    )
    out: dict[int, str] = {}
    for heading, chunk in re.findall(pattern, html, re.S):
        raw = re.sub(r"\[编辑\]|\[編輯\]", "", re.sub(r"<[^>]+>", "", heading).strip())
        num = parse_chapter_num(raw)
        if not num:
            continue
        paras: list[str] = []
        for p in re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S):
            t = to_simplified(re.sub(r"<[^>]+>", "", p).strip())
            if t and "Public domain" not in t:
                paras.append(t)
        if paras:
            out[num] = "\n\n".join(paras)
    return out


def fetch_suwen() -> dict[int, str]:
    chapters: dict[int, str] = {}

    for vol in range(1, 25):
        path = f"黄帝内經素問 (四庫全書本)/卷{vol:02d}"
        try:
            chapters.update(split_by_pian(paragraph_blob(fetch_html(path))))
        except Exception as exc:
            print(f"warn: {path}: {exc}")
        time.sleep(0.08)

    for vol_name in ("第二十一", "第二十三", "第二十四"):
        path = f"重廣補注黃帝內經素問 (四部叢刊本)/卷{vol_name}"
        try:
            chapters.update(split_by_pian(paragraph_blob(fetch_html(path))))
        except Exception as exc:
            print(f"warn: {path}: {exc}")
        time.sleep(0.08)

    for vol in range(1, 25):
        try:
            chapters.update(fetch_clean_suwen_volume(vol))
        except Exception:
            pass
        time.sleep(0.05)

    blob8 = paragraph_blob(fetch_html("黄帝内經素問 (四庫全書本)/卷08"))
    m26 = CHAPTER_RE.search(blob8)
    if m26:
        pre = blob8[: m26.start()]
        m25 = re.search(r"第二十五", pre)
        if m25:
            body = clean_text(pre[m25.end() :])
            if len(body) > 200:
                chapters[25] = body

    blob11 = paragraph_blob(fetch_html("黄帝内經素問 (四庫全書本)/卷11"))
    blob12 = paragraph_blob(fetch_html("黄帝内經素問 (四庫全書本)/卷12"))
    m41 = re.search(r"刺.{0,2}痛篇第四十一", blob11)
    m42 = re.search(r"风论篇第四十二", blob12)
    if m41 and m42:
        chapters[41] = clean_text(blob11[m41.end() :] + blob12[: m42.start()])

    for num in LOST_SUWEN:
        chapters.setdefault(num, LOST_NOTE)

    missing = [n for n in range(1, 82) if n not in chapters]
    if missing:
        raise RuntimeError(f"素问 missing chapters: {missing}")
    return chapters


def parse_ling_title(raw: str) -> tuple[int, str] | None:
    raw = re.sub(r"\[编辑\]|\[編輯\]", "", raw).strip()
    if raw in ("附註", "附注"):
        return None
    m = re.match(r"(.+?)第([一二三四五六七八九十百]+)$", raw)
    if not m:
        return None
    name = to_simplified(m.group(1))
    return cn_num(m.group(2)), name


def fetch_lingshu() -> dict[int, str]:
    chapters: dict[int, str] = {}
    for cn in LING_VOL_CN:
        html = fetch_html(f"黃帝內經/靈樞第{cn}卷")
        pattern = (
            r'<div class="mw-heading mw-heading2">(.*?)</div>\s*'
            r"(.*?)(?=<div class=\"mw-heading mw-heading2\">|</div>\s*<div id=\"catlinks\")"
        )
        for heading, chunk in re.findall(pattern, html, re.S):
            raw = re.sub(r"<[^>]+>", "", heading).strip()
            parsed = parse_ling_title(raw)
            if not parsed:
                continue
            num, _name = parsed
            paras: list[str] = []
            for p in re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.S):
                t = to_simplified(re.sub(r"<[^>]+>", "", p).strip())
                if t and "Public domain" not in t and not t.startswith("@media"):
                    paras.append(t)
            if paras:
                chapters[num] = "\n\n".join(paras)
        time.sleep(0.08)

    missing = [n for n in range(1, 82) if n not in chapters]
    if missing:
        raise RuntimeError(f"灵枢 missing chapters: {missing}")
    return chapters


def cn_title(num: int) -> str:
    if num <= 10:
        return ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"][num]
    if num < 20:
        return "十" + cn_title(num - 10)
    if num % 10 == 0:
        return cn_title(num // 10) + "十"
    tens, ones = divmod(num, 10)
    return cn_title(tens) + "十" + cn_title(ones)


def build_entries() -> list[dict]:
    suwen = fetch_suwen()
    print(f"素问: {len(suwen)} chapters")
    lingshu = fetch_lingshu()
    print(f"灵枢: {len(lingshu)} chapters")

    entries: list[dict] = []
    for num in range(1, 82):
        text = suwen[num]
        title = SUWEN_NAMES[num - 1]
        lost = num in LOST_SUWEN
        entries.append(
            {
                "id": num,
                "book": "素问",
                "chapter": num,
                "title": title,
                "full_title": f"{title}篇第{cn_title(num)}",
                "opening": title if lost else opening_phrase(text),
                "lost": lost,
                "text": text,
            }
        )

    for num in range(1, 82):
        text = lingshu[num]
        title = LING_NAMES[num - 1]
        entries.append(
            {
                "id": 81 + num,
                "book": "灵枢",
                "chapter": num,
                "title": title,
                "full_title": f"{title}第{cn_title(num)}",
                "opening": opening_phrase(text),
                "lost": False,
                "text": text,
            }
        )

    return entries


def main() -> None:
    if opencc is None:
        raise SystemExit("opencc required: use .venv/bin/python")
    entries = build_entries()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({len(entries)} entries)")
    suwen_chars = sum(len(e["text"]) for e in entries if e["book"] == "素问")
    ling_chars = sum(len(e["text"]) for e in entries if e["book"] == "灵枢")
    print(f"  素问 {suwen_chars} chars, 灵枢 {ling_chars} chars")


if __name__ == "__main__":
    main()
