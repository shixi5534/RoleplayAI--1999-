# -*- coding: utf-8 -*-
"""Compendium 简体中文剧情 → 结构化语料。

数据形态（``tmp_probe/scan_format.py`` 全量扫描 151 篇确认）：

    # 篇名
    ## 目录                      ← 目录区，丢弃
    ## Part 1 · 摇滚电台          ← H2 = Part
    ### 序章0-1 `script 100001`  ← H3 = 剧情单元（scene）
    **维尔汀**：台词              ← 对话（80,152 行，全角冒号）
    是雨声。                      ← 旁白（33,148 行）
    > 【标题卡】1966英国伦敦        ← 引用/标题卡（3,134 行）
    音效-掌声（热情的）             ← 制作备注（非正典，丢弃）

本模块只做**确定性解析**：不调用任何模型，不改写一个字台词。
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ── 行级正则 ──
RE_H1 = re.compile(r"^#\s+(?P<t>.+?)\s*$")
RE_H2 = re.compile(r"^##\s+(?P<t>.+?)\s*$")
RE_H3 = re.compile(r"^###\s+(?P<t>.+?)\s*$")
# 对话：**说话人**：正文（全角冒号为主，兼容半角）；允许 `- ` 列表前缀
RE_DIALOGUE = re.compile(
    r"^(?:[-*+]\s+)?\*\*(?P<sp>.+?)\*\*\s*[：:]\s*(?P<tx>.*)$")
RE_ANCHOR = re.compile(r"^\s*<a\s+id=[^>]*>\s*</a>\s*$", re.I)
RE_NAV_MARK = re.compile(r"reading-navigation:(start|end)")
RE_TOC_HEAD = re.compile(r"^##\s*目录\s*$")
RE_HR = re.compile(r"^-{3,}\s*$")
RE_QUOTE = re.compile(r"^\s*>\s?(?P<t>.*)$")
RE_TITLE_CARD = re.compile(r"^\s*[【\[]\s*标题卡\s*[】\]]\s*(?P<t>.*)$")
RE_SCRIPT_SUFFIX = re.compile(r"\s*`script\s*(?P<sid>\d+)`\s*$")
RE_COMMENT = re.compile(r"<!--.*?-->", re.S)

# ── 制作/美术备注（非剧情内容）──
# 这些行混在正文里，若不剔除会污染抽取与检索。但**判据必须是"形态"而非"含关键词"**：
# 实测存在大量以这些词开头的**真旁白**，例如
#   「镜头聚焦到字上，字逐渐淡去，画面只剩下淡黄色的纸张纹路。」（运镜描述）
#   「梁月从披风下掏出…将上面的界面展示给波蒂埃。」（关键词在句中）
#   「乔治橡树生长于七百年前…迎送了每一年学校的巡礼演出。」（演出在句尾）
# 因此下面每条规则都要求关键词处在**行首**且紧跟**序号/括号/分隔符/终止词**等
# 备注特有的形态；正文里的这些词一律不匹配（对应测试 test_production_notes_dropped
# 与 test_narration_with_keyword_kept）。
_NOTE_KW = (r"氛围图差分|氛围图|场景图|剧情场景|场景|特效|音效|镜头|差分|演出|"
            r"浮窗道具|浮窗|视频|美术|UI|界面|动画")
# A：`场景-黑屏` / `氛围图3：…` / `氛围图4（复用）：…` / `动画-6的…` / `音效、特效-…`
#    允许「关键词 + 任意个限定（序号/括号/加载切换）+ 可选并列符」重复出现，
#    再以分隔符引出内容——这样才能覆盖 `氛围图4（复用）：`（序号与括号并存）
#    和 `音效、特效-…`（两个关键词并列）这两种实测形态。
RE_PROD_NOTE = re.compile(
    rf"^\s*(?:(?:{_NOTE_KW})\s*(?:[0-9０-９]+|（[^）]{{0,10}}）|加载|切换|过渡)*"
    rf"\s*[、/／]?\s*)+[-－—：:]\s*.+$")
# B：整行就是一个关键词（`浮窗` / `特效` / `氛围图`）
RE_NOTE_BARE = re.compile(rf"^\s*(?:{_NOTE_KW})\s*$")
# C：关键词 + 终止词（`特效关闭` / `氛围图结束` / `视频开始`）
RE_NOTE_END = re.compile(
    rf"^\s*(?:{_NOTE_KW})\s*(?:结束|关闭|收起|开始|开启|恢复)\s*$")
# D：关键词打头的口语化备注（`浮窗，大一点…-世界地图…` / `黑屏，有海潮拍案的音效…`）
RE_NOTE_COMMA = re.compile(rf"^\s*(?:{_NOTE_KW}|黑屏)\s*[，,]\s*\S")
# E：`翻页特效-滤镜关闭` / `剧场场景-拉普拉斯科算中心-走廊`（关键词前还有 2~6 字定语）
RE_NOTE_VARIANT = re.compile(
    r"^\s*.{1,6}(?:音效|特效|氛围图|场景|镜头)\s*[-－—/／]\s*.+$")
# F：短行以 音效/特效 收尾（`接过小皮箱音效`）
RE_NOTE_TAIL = re.compile(r"^\s*.{2,20}(?:音效|特效)\s*$")
RE_PROD_NOTE2 = re.compile(r"^\s*[\u4e00-\u9fff·]{2,20}神秘术特效\s*$")
# G：纯演出转场标记，允许用顿号/逗号串起来（`特效关闭，氛围图结束`）
_CUE_TOK = (r"渐黑|渐白|渐入|长黑|黑屏|黑幕|淡入|淡出|切至|转场|地标|"
            r"消人|消回忆|浮窗道具收起|消浮窗|收起浮窗道具|替换浮窗|"
            r"特效关闭|特效开启|氛围图结束|氛围图开始|视频开始|视频结束|完")
RE_CUE = re.compile(rf"^\s*(?:{_CUE_TOK})(?:\s*[，,、]\s*(?:{_CUE_TOK}))*\s*$")


def is_production_note(s: str, *, in_dialogue: bool = False) -> bool:
    """该行是否为制作/美术备注（非正典台词）。

    ``in_dialogue=True``（该行是 ``**说话人**：内容`` 的**内容**部分）时，
    额外排除 ``RE_NOTE_COMMA``：实测存在**真台词本身以关键词+逗号开头**的情况——

        **马科尔**：镜头，看过来，这正是本次事件中的人类代表——

    这是台词而非备注，误删会丢掉一句真实对白（测试
    ``test_dialogue_starting_with_keyword_kept`` 锁住该行为）。
    而 ``**助理希曼**：场景-拉普拉斯科算中心-走廊`` 这类"台词内容整体就是备注"
    仍由规则 A 正确剔除。

    另：以 ``镜头`` 打头、后接白话长句的**运镜描述**（如「镜头向下滑，露出…」）
    **刻意不判为备注**——与真旁白形态不可区分，全语料仅约 5 行（<0.005%），
    误删代价远高于保留。参见 ``test_camera_direction_intentionally_kept``。
    """
    if (RE_PROD_NOTE.match(s) or RE_NOTE_BARE.match(s)
            or RE_NOTE_END.match(s) or RE_NOTE_VARIANT.match(s)
            or RE_NOTE_TAIL.match(s) or RE_PROD_NOTE2.match(s)
            or RE_CUE.match(s)):
        return True
    if not in_dialogue and RE_NOTE_COMMA.match(s):
        return True
    return False

# 泛称说话人：不构成可图谱化实体。
# 注意 `？？？` 是全角问号（U+FF1F），不是 ASCII `?`——早期只写 `\?` 导致
# 全语料出现 1,506 次的 `？？？` 未被识别（测试捕获）。
GENERIC_SPEAKER = re.compile(
    r"^(?:[?？]{2,}|未知|旁白|众人|人们|市民(?:观众)?[ⅠⅡⅢⅣ\d]*|路人[甲乙丙丁]?|"
    r"士兵[甲乙丙丁]?|守卫[甲乙丙丁]?|观众[甲乙丙丁]?|人群|所有人|大家|"
    r"广播|无线电|通讯|系统|画外音|声音|旁白者|门卫|服务员|女仆|侍者|"
    r"研究员[甲乙丙]?|工作人员[甲乙丙]?|学生[甲乙丙]?)$")


def is_generic_speaker(name: str) -> bool:
    """泛称/占位说话人：对话归属不可靠，抽取时降权但不丢弃。"""
    n = (name or "").strip()
    if not n:
        return True
    return bool(GENERIC_SPEAKER.match(n))


@dataclass
class Turn:
    """一行剧情内容。"""

    kind: str          # dialogue | narration | quote | title_card
    speaker: str       # dialogue 专用，其余为 ""
    text: str

    @property
    def is_dialogue(self) -> bool:
        return self.kind == "dialogue"


@dataclass
class Scene:
    """剧情单元（H3）。"""

    title: str
    script_id: str
    turns: list[Turn] = field(default_factory=list)


@dataclass
class Part:
    """Part（H2）。"""

    title: str
    scenes: list[Scene] = field(default_factory=list)


@dataclass
class Chapter:
    """一篇剧情（一个 .md 文件）。"""

    doc_id: str
    title: str
    category: str
    source_file: str
    chapter_id: str = ""
    units: str = ""
    parts: list[Part] = field(default_factory=list)

    @property
    def turns(self) -> list[Turn]:
        return [t for p in self.parts for s in p.scenes for t in s.turns]

    def n_turns(self) -> int:
        return sum(len(s.turns) for p in self.parts for s in p.scenes)


def _clean_line(line: str) -> str:
    """去 Markdown 行内标记，保留文本。"""
    t = line.strip()
    t = re.sub(r"\*\*(?P<x>.+?)\*\*", r"\g<x>", t)      # 残留加粗
    t = re.sub(r"(?<!\*)\*(?!\*)(?P<x>.+?)(?<!\*)\*(?!\*)", r"\g<x>", t)
    t = re.sub(r"`(?P<x>[^`]*)`", r"\g<x>", t)
    t = re.sub(r"\[(?P<x>[^\]]*)\]\([^)]*\)", r"\g<x>", t)  # 链接取文字
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"</?(?:div|p|span|em|strong|b|i|u|sup|sub)\b[^>]*>", "", t, flags=re.I)
    return t.strip()


def parse_chapter(path: Path, category: str, doc_id: str) -> Chapter | None:
    """解析单篇 .md → Chapter。"""
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if not lines or not RE_H1.match(lines[0]):
        return None
    title = RE_H1.match(lines[0]).group("t")
    ch = Chapter(doc_id=doc_id, title=title, category=category,
                 source_file=path.name)

    # 头部元信息（H1 到第一个 `---` 之间）
    head_end = next((i for i, l in enumerate(lines) if RE_HR.match(l.strip())), 0)
    for l in lines[1:head_end]:
        s = l.strip().lstrip("-").strip()
        if s.startswith("章节 ID"):
            ch.chapter_id = s.split("：", 1)[-1].strip().strip("`")
        elif s.startswith("剧情单元"):
            ch.units = s.split("：", 1)[-1].strip().strip("`")

    in_nav = False
    in_toc = False
    part: Part | None = None
    scene: Scene | None = None

    def ensure_part() -> Part:
        nonlocal part
        if part is None:
            part = Part(title="")
            ch.parts.append(part)
        return part

    def ensure_scene() -> Scene:
        nonlocal scene
        p = ensure_part()
        if scene is None:
            scene = Scene(title="", script_id="")
            p.scenes.append(scene)
        return scene

    for raw_line in lines[head_end:]:
        line = raw_line.rstrip()
        s = line.strip()

        # 导航块（成对跳过，避免中间的链接行漏进正文）
        if RE_NAV_MARK.search(s):
            in_nav = "start" in s
            continue
        if in_nav:
            continue

        if not s:
            continue
        if RE_ANCHOR.match(s):
            continue
        s = RE_COMMENT.sub("", s).strip()
        if not s:
            continue

        # 目录区：从 `## 目录` 到下一个 `##` 或 `---`
        if RE_TOC_HEAD.match(s):
            in_toc = True
            continue
        if in_toc:
            if RE_H2.match(s) or RE_HR.match(s):
                in_toc = False
            else:
                continue
        if RE_HR.match(s):
            continue

        m2 = RE_H2.match(s)
        if m2:
            part = Part(title=m2.group("t"))
            ch.parts.append(part)
            scene = None
            continue

        m3 = RE_H3.match(s)
        if m3:
            t = m3.group("t")
            sid = ""
            ms = RE_SCRIPT_SUFFIX.search(t)
            if ms:
                sid = ms.group("sid")
                t = RE_SCRIPT_SUFFIX.sub("", t)
            sc = Scene(title=t.strip(), script_id=sid)
            ensure_part().scenes.append(sc)
            scene = sc
            continue

        if RE_H1.match(s):          # 多余的 H1，忽略
            continue

        # 对话
        md = RE_DIALOGUE.match(s)
        if md:
            tx = _clean_line(md.group("tx"))
            sp = _clean_line(md.group("sp"))
            if sp:
                # 台词内容整体是制作备注的（`**助理希曼**：场景-…-走廊`）丢弃；
                # 但以关键词+逗号开头的**真台词**保留（in_dialogue=True）
                if tx and is_production_note(tx, in_dialogue=True):
                    continue
                ensure_scene().turns.append(Turn("dialogue", sp, tx))
                continue

        # 制作备注 / 转场标记：丢弃（非正典）
        if is_production_note(s):
            continue

        # 引用 / 标题卡
        mq = RE_QUOTE.match(s)
        if mq:
            t = _clean_line(mq.group("t"))
            if not t:
                continue
            mt = RE_TITLE_CARD.match(t)
            if mt:
                ensure_scene().turns.append(Turn("title_card", "", mt.group("t").strip()))
            else:
                ensure_scene().turns.append(Turn("quote", "", t))
            continue

        # 列表项兜底：`- xxx` / `1. xxx`
        s2 = re.sub(r"^(?:[-*+]\s+|\d+\.\s+)", "", s).strip()
        if not s2:
            continue
        ensure_scene().turns.append(Turn("narration", "", _clean_line(s2)))

    # 去掉空壳 scene / part
    kept: list[Part] = []
    for p in ch.parts:
        p.scenes = [s for s in p.scenes if s.turns]
        if p.scenes:
            kept.append(p)
    ch.parts = kept
    return ch if ch.parts else None


def doc_id_for(category: str, path: Path) -> str:
    """稳定 doc_id：``<category>__<文件名主干>``（不含扩展名）。"""
    stem = re.sub(r"[^\w\u4e00-\u9fff·]+", "_", path.stem).strip("_")
    return f"{category}__{stem}"


def load_corpus(source_dir: Path, categories: tuple[str, ...]) -> list[Chapter]:
    """按分类加载全部篇目。"""
    out: list[Chapter] = []
    for cat in categories:
        d = source_dir / cat
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            ch = parse_chapter(p, cat, doc_id_for(cat, p))
            if ch is not None:
                out.append(ch)
    return out


def corpus_stats(chapters: list[Chapter]) -> dict:
    """语料统计（用于报告与回归对比）。"""
    by_cat: dict[str, dict] = {}
    total_chars = 0
    total_turns = 0
    speakers: dict[str, int] = {}
    kinds: dict[str, int] = {}
    for ch in chapters:
        c = by_cat.setdefault(ch.category, {"chapters": 0, "turns": 0, "chars": 0})
        c["chapters"] += 1
        for p in ch.parts:
            for s in p.scenes:
                for t in s.turns:
                    c["turns"] += 1
                    total_turns += 1
                    n = len(t.text)
                    c["chars"] += n
                    total_chars += n
                    kinds[t.kind] = kinds.get(t.kind, 0) + 1
                    if t.is_dialogue and t.speaker:
                        speakers[t.speaker] = speakers.get(t.speaker, 0) + 1
    return {
        "chapters": len(chapters),
        "turns": total_turns,
        "chars": total_chars,
        "by_category": by_cat,
        "turn_kinds": kinds,
        "distinct_speakers": len(speakers),
        "top_speakers": sorted(speakers.items(), key=lambda kv: -kv[1])[:30],
    }


# ── 序列化（corpus.json 落盘 / 复现）──

def chapter_to_dict(ch: Chapter) -> dict:
    return {
        "doc_id": ch.doc_id,
        "title": ch.title,
        "category": ch.category,
        "source_file": ch.source_file,
        "chapter_id": ch.chapter_id,
        "units": ch.units,
        "parts": [
            {"title": p.title,
             "scenes": [{"title": s.title, "script_id": s.script_id,
                         "turns": [asdict(t) for t in s.turns]} for s in p.scenes]}
            for p in ch.parts
        ],
    }


def chapter_from_dict(d: dict) -> Chapter:
    ch = Chapter(doc_id=d["doc_id"], title=d["title"], category=d["category"],
                 source_file=d.get("source_file", ""),
                 chapter_id=d.get("chapter_id", ""), units=d.get("units", ""))
    for p in d.get("parts", []):
        pt = Part(title=p.get("title", ""))
        for s in p.get("scenes", []):
            sc = Scene(title=s.get("title", ""), script_id=s.get("script_id", ""))
            for t in s.get("turns", []):
                sc.turns.append(Turn(t.get("kind", "narration"),
                                     t.get("speaker", ""), t.get("text", "")))
            pt.scenes.append(sc)
        ch.parts.append(pt)
    return ch


def save_corpus(chapters: list[Chapter], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "compendium_rag.corpus/v1",
        "stats": corpus_stats(chapters),
        "chapters": [chapter_to_dict(c) for c in chapters],
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


def load_corpus_json(path: Path) -> list[Chapter]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return [chapter_from_dict(c) for c in d.get("chapters", [])]


def corpus_fingerprint(chapters: list[Chapter]) -> str:
    """语料内容指纹：用于判断图谱/索引是否与语料同源。"""
    h = hashlib.sha256()
    for ch in sorted(chapters, key=lambda c: c.doc_id):
        h.update(ch.doc_id.encode("utf-8"))
        for p in ch.parts:
            for s in p.scenes:
                for t in s.turns:
                    h.update(t.kind.encode("utf-8"))
                    h.update(t.speaker.encode("utf-8"))
                    h.update(t.text.encode("utf-8"))
    return h.hexdigest()[:16]
