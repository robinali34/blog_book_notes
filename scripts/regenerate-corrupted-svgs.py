#!/usr/bin/env python3
"""Regenerate diagram SVGs that were corrupted by invalid control characters."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets/images"

FONT = "Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif"
BG = "#F5F7F3"
STROKE = "#C8D4C0"
GREEN = "#7A9078"
GREEN_DARK = "#2F3D2B"
GREEN_MID = "#4A5A45"
GREEN_LIGHT = "#D4E0D0"
GREEN_PALE = "#E8EDE5"
MUTED = "#7A8A75"
LINE = "#9CB098"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def header(w: int, h: int, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{esc(label)}">\n'
        f'  <rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{STROKE}"/>\n'
    )


def text_el(x, y, content, size=13, anchor="middle", bold=False, fill=GREEN_MID) -> str:
    weight = ' font-weight="bold"' if bold else ""
    return (
        f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
        f'font-size="{size}" fill="{fill}"{weight}>{esc(content)}</text>\n'
    )


def overview(title: str, subtitle: str, center: str, boxes: list[tuple[str, str]], footer: str) -> str:
    w, h = 900, 340
    parts = [header(w, h, title)]
    parts.append(text_el(450, 36, title, 20, bold=True))
    parts.append(text_el(450, 58, subtitle, 12, fill=MUTED))
    parts.append(
        f'  <rect x="350" y="80" width="200" height="56" rx="8" fill="{GREEN}" stroke="#5A6A58"/>\n'
    )
    parts.append(text_el(450, 115, center, 15, bold=True, fill=BG))
    parts.append(f'  <line x1="450" y1="136" x2="450" y2="158" stroke="{LINE}" stroke-width="2"/>\n')
    n = len(boxes)
    gap = 760 / n
    for i, (label, note) in enumerate(boxes):
        cx = 70 + gap * i + gap / 2
        x = cx - 70
        parts.append(
            f'  <rect x="{x:.0f}" y="178" width="140" height="90" rx="8" '
            f'fill="{GREEN_LIGHT}" stroke="{GREEN}"/>\n'
        )
        parts.append(text_el(cx, 212, label, 14, bold=True, fill=GREEN_DARK))
        parts.append(text_el(cx, 235, note, 10))
    parts.append(text_el(450, 310, footer, 11, fill=MUTED))
    parts.append("</svg>\n")
    return "".join(parts)


def chapter(title: str, left: str, right: str, left_note: str, right_note: str, footer: str) -> str:
    w, h = 800, 200
    parts = [header(w, h, title)]
    parts.append(text_el(400, 32, title, 18, bold=True))
    parts.append(
        f'  <rect x="280" y="55" width="240" height="120" rx="4" fill="{GREEN_PALE}" '
        f'stroke="{LINE}" stroke-width="2"/>\n'
    )
    parts.append(f'  <path d="M400 55 L400 175" stroke="{MUTED}" stroke-width="2"/>\n')
    parts.append(
        f'  <rect x="290" y="55" width="100" height="120" rx="4" fill="{GREEN_LIGHT}" '
        f'stroke="{GREEN}"/>\n'
    )
    parts.append(text_el(340, 115, left, 20, bold=True, fill=GREEN_DARK))
    parts.append(text_el(340, 138, left_note, 11))
    parts.append(
        f'  <rect x="410" y="55" width="100" height="120" rx="4" fill="{GREEN}" opacity="0.9"/>\n'
    )
    parts.append(text_el(460, 115, right, 20, bold=True, fill=BG))
    parts.append(text_el(460, 138, right_note, 11, fill=GREEN_PALE))
    parts.append(text_el(400, 190, footer, 11, fill=MUTED))
    parts.append("</svg>\n")
    return "".join(parts)


def flow(title: str, subtitle: str, steps: list[str], footer: str, w: int = 900, h: int = 280) -> str:
    parts = [header(w, h, title)]
    parts.append(text_el(w // 2, 36, title, 20, bold=True))
    parts.append(text_el(w // 2, 58, subtitle, 12, fill=MUTED))
    n = len(steps)
    box_w = min(120, (w - 80) // n - 10)
    start = (w - n * box_w - (n - 1) * 20) / 2
    for i, step in enumerate(steps):
        x = start + i * (box_w + 20)
        parts.append(
            f'  <rect x="{x:.0f}" y="110" width="{box_w:.0f}" height="50" rx="8" '
            f'fill="{GREEN_LIGHT}" stroke="{GREEN}"/>\n'
        )
        parts.append(text_el(x + box_w / 2, 140, step, 12, bold=True, fill=GREEN_DARK))
        if i < n - 1:
            x2 = x + box_w
            parts.append(
                f'  <line x1="{x2:.0f}" y1="135" x2="{x2 + 20:.0f}" y2="135" '
                f'stroke="{MUTED}" stroke-width="2" marker-end="url(#arr)"/>\n'
            )
    parts.insert(
        2,
        '  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        f'<path d="M0,0 L8,3 L0,6 Z" fill="{MUTED}"/></marker></defs>\n',
    )
    parts.append(text_el(w // 2, h - 20, footer, 11, fill=MUTED))
    parts.append("</svg>\n")
    return "".join(parts)


def cycle(title: str, subtitle: str, steps: list[str], footer: str) -> str:
    w, h = 900, 280
    parts = [header(w, h, title)]
    parts.append(text_el(450, 36, title, 20, bold=True))
    parts.append(text_el(450, 58, subtitle, 12, fill=MUTED))
    parts.append(
        f'  <circle cx="450" cy="155" r="88" fill="none" stroke="{LINE}" '
        'stroke-width="2" stroke-dasharray="8 5"/>\n'
    )
    positions = [(450, 68), (560, 128), (450, 198), (220, 128)]
    for (x, y), step in zip(positions, steps):
        parts.append(
            f'  <rect x="{x - 60}" y="{y - 22}" width="120" height="44" rx="8" '
            f'fill="{GREEN_LIGHT}" stroke="{GREEN}"/>\n'
        )
        parts.append(text_el(x, y + 5, step, 13, bold=True, fill=GREEN_DARK))
    parts.append(text_el(450, 268, footer, 11, fill=MUTED))
    parts.append("</svg>\n")
    return "".join(parts)


def write(rel: str, content: str) -> None:
    path = IMG / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


def main() -> None:
    write(
        "shangjunshu/shangjunshu-overview.svg",
        overview(
            "商君书 · 变法图强",
            "更法 · 垦令 · 赏刑 · 弱民 · 壹教",
            "富国强国",
            [
                ("废井田", "开阡陌"),
                ("重农战", "抑商贾"),
                ("信赏必罚", "壹赏壹刑"),
                ("连坐", "什伍互督"),
                ("壹教", "明法令"),
            ],
            "便国不法古 · 治世不一道",
        ),
    )
    write(
        "yangming/yangming-overview.svg",
        overview(
            "阳明心学 · 致良知",
            "心即理 · 知行合一 · 事上磨练",
            "此心光明",
            [
                ("心即理", "理不外求"),
                ("致良知", "扩充本体"),
                ("知行合一", "真知即行"),
                ("事上磨练", "在事体认"),
            ],
            "无善无恶心之体 · 为善去恶是格物",
        ),
    )
    write(
        "caigentan/caigentan-scenarios.svg",
        flow(
            "菜根谭 · 场景地图",
            "按场景选编阅读",
            ["职场", "情绪", "领导", "合伙", "线上", "家庭"],
            "修省养心 · 应酬不失 · 评议留余地",
            w=920,
        ),
    )
    write(
        "cognitive-neuroscience/split-brain.svg",
        chapter(
            "分裂脑实验示意",
            "左脑",
            "右脑",
            "语言解释",
            "感知处理",
            "胼胝体切断后：右知难言 · 左善解释",
        ),
    )
    write(
        "caigentan/caigentan-overview.svg",
        overview(
            "菜根谭 · 五编结构",
            "修省 · 应酬 · 评议 · 闲适 · 概论",
            "布衣菜根",
            [
                ("修省", "向内打磨"),
                ("应酬", "待人分寸"),
                ("评议", "观人不惑"),
                ("闲适", "与时间相处"),
                ("概论", "淡泊真味"),
            ],
            "宠辱不惊 · 事让三分 · 岁月本长",
        ),
    )
    write(
        "zhouyi/zhouyi-overview.svg",
        overview(
            "周易 · 观象系辞",
            "经传合一 · 象理占三位一体",
            "变易",
            [
                ("经", "64卦"),
                ("传", "十翼"),
                ("阴阳", "八卦"),
                ("时位", "当位中正"),
            ],
            "观象系辞 · 察势变通 · 慎言慎行",
        ),
    )
    write(
        "hanfeizi/hanfeizi-overview.svg",
        overview(
            "韩非子 · 法术势",
            "法立标准 · 术行驾驭 · 势保执行",
            "君主之术",
            [
                ("法", "公布标准"),
                ("术", "驾驭臣下"),
                ("势", "权威地位"),
                ("二柄", "赏罚二柄"),
            ],
            "以法为教 · 以吏为师 · 信赏必罚",
        ),
    )
    write(
        "sunzi/sunzi-overview.svg",
        flow(
            "孙子兵法 · 十三篇",
            "庙算 → 全胜 → 形势 → 虚实 → 地利 → 火攻与用间",
            ["庙算", "谋攻", "形势", "虚实", "地形", "用间"],
            "先胜后战 · 知彼知己 · 因敌制胜",
            w=920,
            h=300,
        ),
    )
    write(
        "guiguzi/guiguzi-overview.svg",
        flow(
            "鬼谷子 · 十二篇",
            "术六篇 → 用五篇 → 总符言",
            ["捭阖", "反应", "内揵", "抵巇", "飞钳", "忤合"],
            "揣情摩意 · 权谋决断 · 符言总纲",
            w=920,
            h=300,
        ),
    )
    write(
        "zizhi-tongjian/zizhi-overview.svg",
        overview(
            "资治通鉴 · 鉴往知来",
            "前403至后959 · 十六朝脉络",
            "读史四维度",
            [
                ("制度", "典章沿革"),
                ("人心", "君臣将相"),
                ("形势", "天下分合"),
                ("教训", "鉴往知来"),
            ],
            "以史为镜 · 察盛衰之理",
        ),
    )
    write(
        "management/interest-exchange.svg",
        overview(
            "管理的本质",
            "组织目标与个人目标汇合",
            "主动交换",
            [
                ("看得清", "目标对齐"),
                ("划得来", "利益合理"),
                ("做得到", "能力匹配"),
                ("愿持续", "长期交换"),
            ],
            "让人主动交换利益",
        ),
    )
    write(
        "management/active-four.svg",
        flow(
            "让人主动的四要素",
            "看得清 · 划得来 · 做得到 · 愿持续",
            ["看得清", "划得来", "做得到", "愿持续"],
            "交换区可持续",
        ),
    )
    write(
        "management/scenarios.svg",
        flow(
            "管理场景地图",
            "招人 · 授权 · 协作 · 变革 · 绩效 · 1:1",
            ["招人", "授权", "协作", "变革", "绩效", "1:1"],
            "按场景应用交换结构",
            w=920,
        ),
    )
    write(
        "fupan/fupan-loop.svg",
        cycle(
            "有效复盘四步闭环",
            "回顾目标 → 评估结果 → 分析原因 → 总结经验",
            ["回顾目标", "评估结果", "分析原因", "总结经验"],
            "行动项闭环 · 日课校正",
        ),
    )
    write(
        "fupan/fupan-scenarios.svg",
        flow(
            "复盘场景地图",
            "项目 · 团队 · 个人 · 决策 · 危机 · 学习",
            ["项目", "团队", "个人", "决策", "危机", "学习"],
            "按场景选模板",
            w=920,
        ),
    )
    write(
        "fupan/fupan-timeline.svg",
        flow(
            "复盘时间轴",
            "日 → 周 → 项目 T+1/T+7 → 月季年",
            ["日复盘", "周复盘", "项目复盘", "月季年"],
            "节奏递进 · 战略复盘",
        ),
    )
    write(
        "zizhi-tongjian/cases-timeline.svg",
        flow(
            "典型史案时间轴",
            "一案见制度 · 一案见人心",
            ["战国", "秦汉", "三国", "隋唐", "宋明"],
            "锚定专题 · 对照读史",
            w=920,
        ),
    )

    chapters = {
        "guiguzi/02-fanying.svg": ("反应篇", "观往", "察来", "反以观往", "覆以察来", "象比钓语"),
        "guiguzi/03-neijian.svg": ("内揵篇", "上", "下", "高层楔入", "基层渗透", "信任递进"),
        "guiguzi/04-dixi.svg": ("抵巇篇", "察隙", "击虚", "五类巇", "乘虚而入", "因隙成事"),
        "guiguzi/05-feiqian.svg": ("飞钳篇", "扬辞", "钳势", "先服其心", "再制其势", "飞钳并用"),
        "guiguzi/06-wuhe.svg": ("忤合篇", "合", "忤", "因势而合", "因势而忤", "苏张各得其时"),
        "guiguzi/07-chuai.svg": ("揣篇", "耳目", "内心", "观外在言行", "推度内隐情志", "揣情先导"),
        "guiguzi/08-mo.svg": ("摩篇", "微触", "试探", "如操钩临渊", "饵投察应", "摩意成事"),
        "guiguzi/09-quan.svg": ("权篇", "轻", "重", "权衡利害", "计寡者智", "计多者乱"),
        "guiguzi/10-mou.svg": ("谋篇", "阴谋", "阳成", "暗中策划", "公开成事", "商鞅变法"),
        "guiguzi/11-jue.svg": ("决篇", "疑", "断", "五机之中", "速断疑虑", "机不可失"),
        "sunzi/01-miaosuan.svg": ("始计篇", "五事", "七计", "道天地将法", "多算胜少算", "庙算在先"),
        "sunzi/02-mougong.svg": ("谋攻篇", "伐谋", "攻城", "上兵伐谋", "其次伐交", "攻城为下"),
        "sunzi/03-xushi.svg": ("虚实篇", "致人", "不致于人", "击虚", "避实", "因敌制胜"),
        "sunzi/04-dixing.svg": ("地形篇", "地利", "九地", "因地制宜", "知地形", "胜兵先胜"),
        "sunzi/05-yongjian.svg": ("用间篇", "五间", "明主", "因间", "内间反间", "慎战明主"),
        "caigentan/02-yingchou.svg": ("应酬篇", "侠气", "素心", "不失侠气", "常存素心", "事让三分"),
        "caigentan/03-pingyi.svg": ("评议篇", "观人", "论事", "不泥一端", "留有余地", "义利之辨"),
        "caigentan/04-xianshi.svg": ("闲适篇", "岁月", "忙者", "岁月本长", "忙者自促", "淡泊养心"),
        "caigentan/05-gailun.svg": ("概论", "儒", "释道", "融通三家", "淡泊真味", "菜根滋味"),
        "hanfeizi/fashu-shi.svg": ("法术势", "法", "术势", "法立标准", "术势并用", "三角支撑"),
    }
    for rel, args in chapters.items():
        write(rel, chapter(*args))

    zhouyi = {
        "zhouyi/01-yinyang-bagua.svg": flow(
            "阴阳八卦", "太极生两仪 · 两仪生四象 · 四象生八卦",
            ["太极", "两仪", "四象", "八卦"], "观象取义",
        ),
        "zhouyi/02-qian-kun.svg": chapter(
            "乾坤两卦", "乾", "坤", "自强不息", "厚德载物", "乾健坤顺",
        ),
        "zhouyi/03-shi-wei.svg": chapter(
            "时位", "得时", "得位", "待时而动", "中正当位", "君子藏器于身",
        ),
        "zhouyi/04-bian-yi.svg": chapter(
            "变易", "本卦", "变卦", "穷则变", "变则通", "通则久",
        ),
        "zhouyi/05-juece.svg": flow(
            "决策三问", "势在何处 · 时宜否 · 何者可变",
            ["察势", "问时", "择变"], "慎言慎行",
        ),
        "zhouyi/06-liuyao-structure.svg": chapter(
            "六爻结构", "内卦", "外卦", "下三爻", "上三爻", "动爻定变",
        ),
        "zhouyi/07-tongqian-steps.svg": flow(
            "铜钱起卦六步", "自下而上 · 每次摇出一爻",
            ["一爻", "二爻", "三爻", "四爻", "五爻", "上爻"],
            "记录动爻 · 成卦",
            w=920,
        ),
        "zhouyi/08-liuyao-parse.svg": flow(
            "六爻解析七步", "明问 → 摇卦 → 成卦 → 定名 → 动变 → 读辞 → 断语",
            ["明问", "摇卦", "成卦", "定名", "动变", "读辞", "断语"],
            "完整断卦流程",
            w=980,
            h=300,
        ),
    }
    for rel, content in zhouyi.items():
        write(rel, content)


if __name__ == "__main__":
    main()
