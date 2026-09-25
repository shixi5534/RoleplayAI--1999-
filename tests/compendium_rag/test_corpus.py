# -*- coding: utf-8 -*-
"""语料解析测试：Compendium 简体中文 Markdown → 结构化 Chapter。

覆盖真实数据形态（说话人标记 / 旁白 / 标题卡 / 制作备注 / 导航区）。
"""
from __future__ import annotations

import pytest

from compendium_rag import corpus as C


def test_parse_single_chapter_all_parts(readable_dir):
    p = readable_dir / "mainline" / "000-此即明日.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "mainline__000")
    assert ch is not None
    assert ch.title == "此即明日"
    assert ch.category == "mainline"
    assert ch.parts, "应当解析出至少一个 Part"
    assert ch.n_turns() > 50


def test_dialogue_speaker_attribution(readable_dir):
    """`**说话人**：台词` 必须被正确归属——这是图谱关系的依据。"""
    p = readable_dir / "mainline" / "000-此即明日.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    turns = [t for t in ch.turns if t.is_dialogue]
    assert turns, "应解析出对话行"
    assert all(t.speaker for t in turns), "对话行必须带说话人"
    assert all("**" not in t.speaker for t in turns), "说话人不应残留 markdown 标记"


def test_narration_has_no_speaker(readable_dir):
    p = readable_dir / "mainline" / "000-此即明日.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    narr = [t for t in ch.turns if t.kind == "narration"]
    assert narr, "应解析出旁白行"
    assert all(t.speaker == "" for t in narr)


def test_navigation_and_toc_excluded(readable_dir):
    """导航块与目录不应污染正文。"""
    p = readable_dir / "mainline" / "000-此即明日.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    joined = "\n".join(t.text for t in ch.turns)
    assert "reading-navigation" not in joined
    assert "返回目录" not in joined
    assert "#episode-" not in joined


def test_production_notes_dropped(readable_dir):
    """制作/美术备注非正典台词，必须剔除。"""
    p = readable_dir / "mainline" / "106-今夜星光灿烂.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    joined = "\n".join(t.text for t in ch.turns)
    assert "氛围图" not in joined
    assert not any(t.text.strip().startswith("音效-") for t in ch.turns)


@pytest.mark.parametrize("line", [
    "场景-黑屏",
    "场景-暴风雨中的船舷（复用序章星锑的船）",
    "氛围图1-电击椅子上的伊索尔德。伊索尔德不露出眼睛被束缚在椅子上。",
    "氛围图3：37面无表情，咬着星锑的头，星锑表情痛苦。（见右图）",
    "氛围图4（复用）：传道者神庙外矗立的正十二面体形状的真理之石。",
    "音效-掌声（热情的）",
    "音效、特效-有灵体出现的感觉",
    "音效/特效-那种纸上有标注的感觉",
    "翻页特效-滤镜关闭",
    "特效关闭，氛围图结束",
    "浮窗",
    "特效",
    "氛围图",
    "视频结束",
    "浮窗道具收起",
    "黑屏",
    "接过小皮箱音效",
    "鹭鸶剪神秘术特效",
    "浮窗，大一点（或许画大点直接当氛围图用？）-世界地图-临界点预测图。",
    "黑屏，有海潮拍案的音效，这一节前面为梦境，需要带一个回忆特效框",
    "场景加载-阅读状态。理想是有一个翻页的特效，然后场景变为线稿。",
    "动画-6的调和卷轴，一边摊开，一边升起，出现内部金色的几何图形。",
    "剧情场景-岛屿-沙滩-炮火轰炸版本",
    "剧场场景-拉普拉斯科算中心-走廊",
    "场景-拉普拉斯科算中心-走廊",
])
def test_production_note_forms_detected(line):
    """穷举实测到的备注形态（序号 / 括号 / 冒号 / 顿号 / 变体定语 / 裸词）。"""
    assert C.is_production_note(line) is True, f"应判为备注：{line}"


def test_dialogue_starting_with_keyword_kept():
    """真台词以「关键词+逗号」开头时必须保留（in_dialogue 语境）。

    实测 `**马科尔**：镜头，看过来，这正是本次事件中的人类代表——`
    是台词而非备注；早期规则只看行首关键词，会把这句真对白误删。
    """
    assert C.is_production_note("镜头，看过来，这正是本次事件中的人类代表——",
                                in_dialogue=True) is False
    # 同样的文本出现在旁白（独立行）位置时才判为备注
    assert C.is_production_note("镜头，看过来，这正是本次事件中的人类代表——",
                                in_dialogue=False) is True


def test_dialogue_note_content_dropped(readable_dir):
    """`**助理希曼**：场景-拉普拉斯科算中心-走廊` 这类"台词内容就是备注"应剔除。"""
    p = readable_dir / "mainline" / "107-孤独之歌.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    texts = [t.text for t in ch.turns]
    # 备注形态（带「场景-」前缀）全部剔除
    assert not [t for t in texts if t.startswith("场景-拉普拉斯科算中心-走廊")]
    assert not [t for t in texts if t.startswith("剧情场景-")]
    assert not [t for t in texts if t.startswith("剧场场景-")]
    # 但**裸地点名**「拉普拉斯科算中心-走廊」本身是合法地点，必须保留
    # （它与 `场景-<地点>` 形态不同，删掉它会丢失一个真实地名实体）
    assert [t for t in texts if t == "拉普拉斯科算中心-走廊"], \
        "裸地点名被误删"
    # 同篇真台词仍在
    assert len([t for t in ch.turns if t.is_dialogue]) > 100


@pytest.mark.parametrize("line", [
    # 运镜描述：与真旁白形态不可区分，刻意保留（保守取舍，见 is_production_note 文档）
    "镜头向下滑，露出阿夫西维的手和他的画纸，他在画粗略的简笔画",
    "镜头聚焦到字上，字逐渐淡去，画面只剩下淡黄色的纸张纹路。",
    "镜头逐渐拉近，聚焦在雕塑上，抱着矿锄的北极熊塑像伸着爪子",
])
def test_camera_direction_intentionally_kept(line):
    """运镜描述是**有意识的保留**，不是漏判——这条测试锁住该设计决策。"""
    assert C.is_production_note(line) is False


@pytest.mark.parametrize("line", [
    # 真旁白：关键词在句中或句尾，绝不能误删
    "乔治橡树生长于七百年前，它以一个长辈的身份，迎送了每一年学校的巡礼演出。",
    "茫然的乐手抬起头来。高台上的身影陌生而冷冽，这显然无关任何一场精心彩排的演出。",
    "梁月从披风下掏出自己的SPF-Ⅰ型便携联络装置，简单操作两下后，将上面的界面展示给波蒂埃。",
    "孤立无援地走在危机四伏的迷宫里，并不是探险家想象中的科考场景。",
    "**维尔汀**：我好像见过这个场景……就在……我——",
    "所有人像电影慢镜头一样转身，睁大了双眼。",
    "我们在其中演出，塑造接近无重力的、充满想象的、不可捉摸的世界。",
])
def test_narration_with_keyword_kept(line):
    """含关键词的**真旁白/台词**必须保留——防止规则过度删除正文。"""
    assert C.is_production_note(line) is False, f"误判正文为备注：{line}"


def test_no_production_notes_leak_in_full_corpus(readable_dir):
    """全量语料抽检：解析结果里不应残留备注形态的行（对话语境用 in_dialogue）。"""
    chapters = C.load_corpus(readable_dir, ("mainline", "activity"))
    leaked = []
    for ch in chapters:
        for t in ch.turns:
            s = t.text.strip()
            if t.is_dialogue:
                continue          # 台词内容已被 parse 阶段按 in_dialogue 规则过滤
            if C.is_production_note(s):
                leaked.append(f"{ch.doc_id}: {s[:60]}")
    assert not leaked, f"残留备注 {len(leaked)} 行，例如：{leaked[:5]}"


def test_script_id_extracted(readable_dir):
    """H3 尾部 `script NNNNNN` 应成为 scene 的 script_id。"""
    p = readable_dir / "mainline" / "000-此即明日.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    ids = [s.script_id for pt in ch.parts for s in pt.scenes]
    assert any(ids), "应至少解析出一个 script_id"
    assert all(i.isdigit() for i in ids if i)


def test_title_card_kind(readable_dir):
    p = readable_dir / "mainline" / "000-此即明日.md"
    if not p.exists():
        pytest.skip("样例篇目不存在")
    ch = C.parse_chapter(p, "mainline", "d")
    cards = [t for t in ch.turns if t.kind == "title_card"]
    assert cards, "应识别出【标题卡】为 title_card"
    assert all("【标题卡】" not in t.text for t in cards), "标记应被剥离"


def test_metadata_header_parsed(readable_dir):
    ch = C.parse_chapter(readable_dir / "mainline" / "000-此即明日.md",
                         "mainline", "d")
    assert ch.chapter_id == "000"
    assert ch.units == "6"


def test_all_chapters_parse(readable_dir):
    """全量语料必须全部可解析（不允许静默丢篇）。"""
    chapters = C.load_corpus(readable_dir, ("mainline", "activity", "character",
                                            "anecdote", "appendix_unbound"))
    assert len(chapters) == 151, f"期望 151 篇，实际 {len(chapters)}"
    assert all(c.n_turns() > 0 for c in chapters)
    assert all(c.doc_id for c in chapters)


def test_doc_id_unique(readable_dir):
    chapters = C.load_corpus(readable_dir, ("mainline", "activity", "character",
                                            "anecdote", "appendix_unbound"))
    ids = [c.doc_id for c in chapters]
    assert len(ids) == len(set(ids)), "doc_id 必须唯一"


def test_corpus_stats_shape(readable_dir):
    chapters = C.load_corpus(readable_dir, ("mainline",))
    st = C.corpus_stats(chapters)
    assert st["chapters"] == 14
    assert st["turns"] > 20_000
    assert st["distinct_speakers"] > 100
    assert st["turn_kinds"]["dialogue"] > 0


def test_fingerprint_deterministic(readable_dir):
    a = C.load_corpus(readable_dir, ("mainline",))
    b = C.load_corpus(readable_dir, ("mainline",))
    assert C.corpus_fingerprint(a) == C.corpus_fingerprint(b)


def test_fingerprint_changes_with_content(mini_chapters):
    fp1 = C.corpus_fingerprint(mini_chapters)
    mini_chapters[0].parts[0].scenes[0].turns[0].text += "（改动）"
    assert C.corpus_fingerprint(mini_chapters) != fp1


def test_corpus_roundtrip(mini_chapters, tmp_path):
    p = tmp_path / "corpus.json"
    C.save_corpus(mini_chapters, p)
    back = C.load_corpus_json(p)
    assert len(back) == len(mini_chapters)
    assert C.corpus_fingerprint(back) == C.corpus_fingerprint(mini_chapters)


@pytest.mark.parametrize("name,expected", [
    ("？？？", True), ("众人", True), ("市民观众Ⅰ", True),
    ("维尔汀", False), ("星锑", False), ("十四行诗", False),
])
def test_generic_speaker_detection(name, expected):
    assert C.is_generic_speaker(name) is expected
