"""角色设定文本标准化（纯函数，无副作用）。

目标：把用户在多行文本/富文本编辑器里填写的角色人设字段，统一为
「干净、可预期、对 LLM 友好的规范文本」，在**入库与进 prompt 之前**
自动执行，保证：

1. 空白统一：全角空格 → 半角、连续空白 → 单个空格、行首行尾空白去除；
2. 标点规范：ASCII 标点 → 中文标点、重复标点（“！！”“？？”）折叠、顿号归一；
3. 列表结构化：形如 "1) xx  2) yy" 的行内编号序列 → 换行编号列表
   （1. xx / 2. yy），提升 LLM 对行为准则/性格要点等字段的解析质量；
4. 空值收敛：全空白文本 → 空串，避免「看似填了实则空白」污染人设。

设计要点：
- 纯函数：不读文件、不依赖 app 内部模块，可独立单测；
- 字段感知：name 等短字段走轻量清理；长文本字段走完整列表化；
- 幂等：多次调用结果一致（normalize(normalize(x)) == normalize(x)）。
"""
from __future__ import annotations

import re
from typing import Callable, Final

# ── 空白统一 ──
# 全角空格（U+3000）与窄不换行空格等统一为半角空格
_RE_FULLWIDTH_SPACE: Final = re.compile(r"[\u3000\u00a0\u2007\u202f\u2060]")
# 行内连续空白（含 Tab、多个空格）→ 单个空格；\n 两侧的空白吸掉
_RE_INLINE_WS: Final = re.compile(r"[ \t]+")
_RE_WS_AROUND_NEWLINE: Final = re.compile(r"[ \t]*\n[ \t]*")

# ── 标点规范 ──
_RE_REPEAT_PUNCT: Final = re.compile(r"([！？!?])\1+")  # 连续叹/问号折叠
# 行尾分隔符清理：逗号/顿号/分号/冒号（句号叹号问号是语气标点，保留）
_RE_TRAILING_SEP: Final = re.compile(r"[，、；：,;:]+$")
# ASCII 逗号/分号 → 中文（带两侧空白吸附："a , b" → "a，b"）
_RE_ASCII_COMMA: Final = re.compile(r"\s*,\s*")
_RE_ASCII_SEMI: Final = re.compile(r"\s*;\s*")

# ── 列表结构化 ──
# 中文数字（一二三…）转阿拉伯数字（列表条目排序用）
_CN_NUM = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
           "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"}
_RE_CN_NUM = re.compile("|".join(sorted(_CN_NUM, key=len, reverse=True)))

# 行内编号：1)xx 2)yy 或 1.xx、2.xx（数字+右括号/点/顿号+内容），含中文数字
_RE_NUM_LIST: Final = re.compile(
    r"(?:^|[\s；;。])([0-9一二三四五六七八九十百]+)\s*[)）.、]\s*"
)

# 需要走「完整列表化」的长文本字段
LIST_FIELDS: Final[frozenset[str]] = frozenset(
    {"personality", "scenario", "background", "behavior_rules"}
)

# 需要走「轻量清理」的短字段
LIGHT_FIELDS: Final[frozenset[str]] = frozenset(
    {"name", "description", "tone", "first_mes", "mes_example",
     "post_history_instructions", "system_prompt"}
)

_ALL_FIELDS: Final[frozenset[str]] = LIST_FIELDS | LIGHT_FIELDS


def normalize_character_text(text: str | None, field: str = "") -> str:
    """统一入口：按字段类型规范化角色设定文本。

    - text 为 None / 全空白 → 返回空串（空值收敛）；
    - field 在 LIST_FIELDS 中 → 完整列表化清洗；
    - field 在 LIGHT_FIELDS 中 → 轻量清洗（空白+标点，不做列表化）；
    - 未知 field → 走完整清洗（行为保守，多清洗无害）。
    """
    if text is None:
        return ""
    # 1) 统一空白（先做，避免后续正则被全角空格干扰）
    text = _RE_FULLWIDTH_SPACE.sub(" ", text)
    text = _RE_WS_AROUND_NEWLINE.sub("\n", text)
    text = _RE_INLINE_WS.sub(" ", text)

    if field in LIST_FIELDS:
        text = _normalize_list_text(text)
    else:
        text = _normalize_light_text(text)
    return text.strip()


def normalize_card_texts(data: dict, fields: tuple[str, ...] | None = None) -> dict:
    """批量规范化角色字段 dict（就地构建新 dict，不改入参）。

    用于 CharacterStore._build_card 保存前统一清洗所有文本字段；
    非文本字段（character_book / knowledge_scope / 语音参数）原样保留。
    """
    targets = tuple(fields) if fields else tuple(_ALL_FIELDS)
    out = dict(data)
    for f in targets:
        v = out.get(f)
        if isinstance(v, str):
            out[f] = normalize_character_text(v, field=f)
        # 其余类型（None / list / dict / float）不处理
    return out


# ── 内部实现 ──

def _normalize_light_text(text: str) -> str:
    """轻量清洗：标点规范 + 空行收敛（不做列表化）。"""
    text = _normalize_punct(text)
    # 折叠 3 个以上连续空行为至多 2 个（段落分隔保留一个空行）
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_list_text(text: str) -> str:
    """完整列表化：标点规范 + 行内编号序列 → 换行编号列表。"""
    text = _normalize_punct(text)
    text = _expand_inline_list(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_punct(text: str) -> str:
    """统一标点：ASCII 逗号/分号转中文、重复叹问号折叠、行尾标点清理。"""
    text = _RE_ASCII_COMMA.sub("，", text)
    text = _RE_ASCII_SEMI.sub("；", text)
    text = _RE_REPEAT_PUNCT.sub(r"\1", text)
    # 行尾多余分隔符（每个句子/条目的收尾逗号分号等）清理，保留句号等结束符
    text = re.sub(r"[，、；：]+([\n。！？；])", r"\1", text)
    text = _RE_TRAILING_SEP.sub("", text)
    return text


def _cn_num_to_arabic(num: str) -> str:
    """中文数字 → 阿拉伯数字（仅列表序号转换；单个汉字原文保留）。"""
    return _RE_CN_NUM.sub(lambda m: _CN_NUM[m.group(0)], num)


def _expand_inline_list(text: str) -> str:
    """把行内编号序列展开为换行编号列表。

    输入:  "1) 冷静  2) 果断  3) 话少"
    输出:  "1. 冷静\n2. 果断\n3. 话少"

    规则：
    - 数字/中文数字 + ) ）. 。、 起始的条目视为编号项；
    - 每项以「首个编号」为界切分；项内空白统一为单个空格；
    - 已存在换行时仅对同一行内的编号序列展开，不破坏已有段落。
    """
    if not _RE_NUM_LIST.search(text):
        return text

    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue
        # 只对行内出现 ≥2 个编号的序列展开；单个编号行保持原样
        matches = list(_RE_NUM_LIST.finditer(stripped))
        if len(matches) < 2:
            out.append(stripped)
            continue
        parts: list[str] = []
        for i, m in enumerate(matches):
            item = (
                stripped[m.end(): matches[i + 1].start()]  # type: ignore[index]
                if i + 1 < len(matches)
                else stripped[m.end():]
            )
            parts.append(f"{_cn_num_to_arabic(m.group(1))}. {item.strip()}")
        out.append("\n".join(parts))
    return "\n".join(out)


def normalize_single_line(text: str | None) -> str:
    """短字段（名称/简介/语气）专用：压成单行并清理标点。"""
    if text is None:
        return ""
    text = _RE_FULLWIDTH_SPACE.sub(" ", text)
    text = _RE_INLINE_WS.sub(" ", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = _normalize_punct(text)
    return text.strip()


# 便捷别名（语义化命名，供外部调用/测试阅读）
normalize_character = normalize_character_text
normalize_card = normalize_card_texts
