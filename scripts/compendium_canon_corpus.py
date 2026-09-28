# -*- coding: utf-8 -*-
"""Reverse1999-Story-Compendium 官方中文剧情原文 → 正典语料层（``canon_zh``）。

为什么做这一层
    现有 ``canon_zh`` 只有 112 个灰机 ``小径/<篇名>`` 页（663 块 / 40.5 万字），
    实测与 compendium 正文**零重合**（同名词条正文 40 字窗口命中 0/6）——
    灰机页是「小径」支线读物，compendium 是**主线/活动/角色/轶事全本对话**。
    两者互补，因此本脚本**只新增、不覆盖**：
        ``canon_zh/<篇名>.md``            灰机小径（已有，保持原样）
        ``canon_zh/<篇名>.compendium.md`` 本脚本产出（文件名后缀隔离）
        ``doc_id`` 前缀 ``huiji_`` vs ``huiji_cmp_``（文档级隔离，见下）

三层防线（与项目约束 P1/P6 一致）
    ① 结构化清洗：确定性剥壳（导航/目录/锚点/HTML），**不改写正文一字**；
       正文是官方正典，任何模型润色都会违反 N1/S1「事实保真」约束。
    ② 元数据映射：chapter_metadata.json 解析 version/category；缺项交云端判定。
    ③ 云端质检：抽检异常块，产出报告供人工裁决，**不落正文**。

为什么 doc_id 要显式写在头部
    ``_parse_canon_file`` 默认用 H1 标题推导 ``huiji_<标题>``，而 ``绿湖噩梦``
    等 27 篇与灰机页同名 → doc_id 与文件名双冲突，且 H1 若加后缀会**破坏篇章路由**
    （``chapters_in`` 要求 arc 名出现在用户查询里，「绿湖噩梦_compendium」永不命中）。
    因此 H1 保持干净篇名，doc_id 显式独立。plot_corpus 侧已支持可选的 ``doc_id：`` 头。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/compendium_canon_corpus.py --convert
    .venv/Scripts/python.exe -X utf8 scripts/compendium_canon_corpus.py --status
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "Reverse1999-Story-Compendium"
READABLE = VENDOR / "readable" / "story_zh_CN_chapter_edition"
META_JSON = VENDOR / "exports" / "chapter_metadata.json"
OUTDIR = ROOT / "data" / "lore" / "wu_ming_zhe" / "canon_zh"

# 收录分类（用户确认：排除 appendix_unbound 未绑定旁支）
CATEGORIES = ("mainline", "activity", "character", "anecdote")
CAT_LABEL = {
    "mainline": "主线",
    "activity": "活动",
    "character": "角色剧情",
    "anecdote": "轶事",
}

REPO_URL = "https://github.com/VioletWilde/Reverse1999-Story-Compendium"
DOC_ID_PREFIX = "huiji_cmp_"
FETCH_DATE = "2026-09-17"

# ── 头部解析 ──
RE_CID = re.compile(r"^-?\s*章节 ID：\s*`?(\d+)`?\s*$", re.M)
RE_UNITS = re.compile(r"^-?\s*剧情单元：\s*`?(\d+)`?\s*$", re.M)
RE_CATLINE = re.compile(r"^-?\s*分类：\s*(\S+)\s*$", re.M)

# ── 结构清洗 ──
RE_COMMENT = re.compile(r"<!--.*?-->", re.S)
# 导航块必须**成对整段删除**：只删 <!-- --> 标记会把夹在中间的
# [← 上一篇…] · [返回目录] · [下一篇 →] 链接行漏进正文（实测 78 处）。
RE_NAV_BLOCK = re.compile(
    r"<!--\s*reading-navigation:start\s*-->.*?<!--\s*reading-navigation:end\s*-->",
    re.S | re.I)
# 兜底：任何残留的「上一篇/下一篇/返回目录」链接行
RE_NAV_LINE = re.compile(r"^\s*\[[^\]]*\]\([^)]*\)\s*(?:·\s*\[[^\]]*\]\([^)]*\)\s*)+$", re.M)
RE_ANCHOR = re.compile(r"^\s*<a\s+id=[^>]*>\s*</a>\s*$", re.M | re.I)
RE_TOC_HEAD = re.compile(r"^##\s*目录\s*$", re.M)
RE_HR = re.compile(r"^-{3,}\s*$", re.M)
RE_SCRIPT_H3 = re.compile(r"^###\s*(.+?)\s*`script\s*(\d+)`\s*$", re.M)
RE_BR = re.compile(r"(?:<br\s*/?>\s*){2,}", re.I)
RE_BR1 = re.compile(r"<br\s*/?>", re.I)
RE_TAG = re.compile(r"</?(?:div|p|span|em|strong|b|i|u|sup|sub)\b[^>]*>", re.I)
RE_MULTI_NL = re.compile(r"\n{3,}")
RE_TRAILING_WS = re.compile(r"[ \t]+$", re.M)
# 制作/美术备注：游戏脚本里夹带的**非剧情**行（实测 66 处 / 11.3 万行）。
# 例：「剧情场景-岛屿-沙滩-炮火轰炸版本」「氛围图差分-芭卡洛儿侧头低语」
# 「……问下美术能不能把洞穴中心那张的石头去掉」。属制作说明而非正典台词，
# 且会抢排名（实测把芭卡洛儿真实台词挤出 top-2）。只删**整行**为备注的情况，
# 行内出现（极少）不处理，避免误伤正文。
# 制作/美术备注：游戏脚本里夹带的**非剧情**行（云端质检 240 块抽样 + 全量量化定位）。
# 例：「剧情场景-岛屿-沙滩-炮火轰炸版本」「氛围图差分-芭卡洛儿侧头低语」
# 「音效-拍桌」「特效-由场景渐渐转变为星空」「镜头模拟主观视角晃动」。
# 判据：**行首**即命中关键词 + 连字符，确保不误伤正文里顺带提到这些词的行。
RE_PROD_NOTE = re.compile(
    r"^\s*(?:氛围图差分|剧情场景|氛围图|场景图|场景|特效|音效|镜头|差分|演出|选项|视频|浮窗道具)"
    r"\s*[-－—]\s*.+$", re.M)
# 无连字符的裸备注行（如「鹭鸶剪神秘术特效」）——只认「正文行」形态，行尾无句读
RE_PROD_NOTE2 = re.compile(r"^\s*[\u4e00-\u9fff·]{2,20}神秘术特效\s*$", re.M)
# 纯演出转场/分支标记：整行就是这一个词，夹在台词之间（云端质检定位 + 全量量化）。
# 刻意**只收无歧义的行话**，排除「结束/开始/恢复」这类在旁白里有正常语义的通用词，
# 也排除「移动/攻击/供能/鼓捣」这类可能作为正常叙述出现的通用动词（合计仅 56 处，
# 不值得为 0.05% 承担误删真实旁白的风险）。
RE_STANDALONE_CUE = re.compile(
    r"^\s*(?:渐黑|渐白|渐入|长黑|黑屏|黑幕|淡入|淡出|切至|转场|地标|浮窗|"
    r"消人|消回忆|浮窗道具收起|消浮窗|收起浮窗道具|替换浮窗|"
    r"特效关闭|氛围图结束|视频开始|视频结束)\s*$", re.M)
# 剧本编号行：`第八章8-11.2（script 100817）` / `【3.4】不老春20.1（script 203430）`。
# 纯内部 ID，对检索与阅读都无价值（标题信息已由 `##`/`###` 承载）。
# 不匹配以 # 开头的标题行——标题在 normalize_body 里单独处理（只剥后缀、保留标题）。
RE_SCRIPT_CUE = re.compile(r"^(?!#)\s*.{0,60}?（script\s*\d+）\s*$", re.M)
# 只剩 Markdown 标记的空壳行
RE_ONLY_MARKUP = re.compile(r"^\s*(?:\*+|#+|-{3,})\s*$", re.M)


def read_meta_map() -> dict[int, dict]:
    if not META_JSON.exists():
        return {}
    data = json.loads(META_JSON.read_text(encoding="utf-8"))
    return {c["chapter_id"]: c for c in data.get("chapters", [])}


def read_project_arc_versions() -> dict[str, str]:
    """从项目**既有语料**里harvest 篇名→版本（单一事实源，不硬编码）。

    B 站转写文档的 title 里带「x.y版本『篇名』」，是已验证过的版本映射，
    比任何模型推断都可靠（P2/N1）。
    """
    p = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    try:
        docs = json.loads(p.read_text(encoding="utf-8")).get("docs", {})
    except (OSError, ValueError):
        return {}
    for d in docs.values():
        a = (d.get("arc") or "").strip()
        v = (d.get("version") or "").strip()
        if a and v:
            out.setdefault(a, v)
    return out


def read_timeline_versions() -> dict[str, str]:
    """剧情时间轴里的 篇名→version（人工维护的锚点，可信度高于推断）。"""
    p = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_timeline.json"
    if not p.exists():
        return {}
    try:
        t = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out: dict[str, str] = {}
    for e in t.get("entries", []) or []:
        n = (e.get("name") or "").strip()
        v = (e.get("version") or "").strip()
        if n and v:
            out.setdefault(n, v)
    return out


def rule_chapter_id_version(cid: int | None) -> str | None:
    """5 位 chapter_id 确定性编码版本号：``11101 -> 1.1``。

    已验证（docs/plot-graph-rag/corpus/剧情文件清洗清单.md 同类口径）：
      - 对 16 个已知正确映射 14/14 命中，0 反例；
      - 与独立来源 ``story_canonical.json`` 交叉核对 59/59 一致，0 分歧。
    仅适用于活动/角色剧情的 5 位 id；6 位（联动版本）与主线/轶事 id 不适用——**不猜**。
    """
    if cid is None or not (10000 <= cid <= 99999):
        return None
    return f"{cid // 10000}.{(cid // 1000) % 10}"


def resolve_version(name: str, category: str, cid: int | None, meta_map: dict[int, dict],
                    arc_ver: dict[str, str], tl_ver: dict[str, str]) -> tuple[str, str]:
    """篇名 → (version, 依据)。依据为空串表示**未确认**，一律留空（TS2：禁止猜填）。"""
    entry = meta_map.get(cid) if cid is not None else None

    # ① chapter_metadata 直接命中
    if entry and entry.get("version"):
        return str(entry["version"]).strip(), "chapter_metadata"

    # ② mirror_of 链（同内容镜像章节，如「疯癫与文明」活动镜像指向主线 109）
    hops, cur, seen = 0, entry, set()
    while cur and cur.get("mirror_of") and hops < 4:
        nxt = meta_map.get(cur["mirror_of"])
        if not nxt or nxt["chapter_id"] in seen:
            break
        seen.add(nxt["chapter_id"])
        if nxt.get("version"):
            return str(nxt["version"]).strip(), f"mirror_of({hops + 1})"
        cur, hops = nxt, hops + 1

    # ③ chapter_id 确定性编码（活动 / 角色剧情）
    if category in ("activity", "character"):
        r = rule_chapter_id_version(cid)
        if r:
            return r, "chapter_id_rule"

    # ④ 项目既有语料 / 时间轴的已验证映射
    for src, table in (("project_corpus", arc_ver), ("plot_timeline", tl_ver)):
        v = table.get(name)
        if v:
            return v, src

    return "", ""


def strip_scaffolding(text: str) -> str:
    """确定性剥壳：导航 / 目录 / 锚点 / 注释 / 分隔线。正文一字不改。"""
    # 导航块先整段删（必须在 RE_COMMENT 之前，否则中间的链接行会漏网）
    out = RE_NAV_BLOCK.sub("", text)
    out = RE_COMMENT.sub("", out)

    # 去掉「## 目录」整段（到下一个 --- 或下一个 ## 为止）
    m = RE_TOC_HEAD.search(out)
    if m:
        tail = out[m.end():]
        nxt = re.search(r"^(?:---\s*$|##\s)", tail, re.M)
        out = out[:m.start()] + (tail[nxt.start():] if nxt else "")

    out = RE_ANCHOR.sub("", out)
    out = RE_HR.sub("", out)
    out = RE_NAV_LINE.sub("", out)
    out = RE_PROD_NOTE.sub("", out)
    return out


def normalize_body(body: str) -> str:
    """正文归一：HTML 换行/标签还原，剥掉演出标记。不触碰台词与旁白。"""
    out = RE_BR.sub("\n\n", body)
    out = RE_BR1.sub("\n", out)
    out = RE_TAG.sub("", out)
    # blockquote 前缀去掉（> 是阅读排版，不是内容），保留其后的标题卡/副标题文本
    out = re.sub(r"^>\s?", "", out, flags=re.M)
    # 先剥「剧本编号后缀」，再处理标题：`### 第八章8-11.2 \`script 100817\``
    #  → `### 第八章8-11.2`（标题保留，只去掉内部 ID）
    out = RE_SCRIPT_H3.sub(lambda m: f"{m.group(1)}", out)
    # 非标题的纯 script 编号行整行删除
    out = RE_SCRIPT_CUE.sub("", out)
    out = RE_PROD_NOTE.sub("", out)
    out = RE_PROD_NOTE2.sub("", out)
    out = RE_STANDALONE_CUE.sub("", out)
    out = RE_ONLY_MARKUP.sub("", out)
    out = RE_TRAILING_WS.sub("", out)
    out = RE_MULTI_NL.sub("\n\n", out)
    return out.strip()


def safe_doc_key(name: str) -> str:
    """篇名 → doc_id 主体（与 plot_corpus 的归一化同口径）。"""
    return re.sub(r"[^\w\u4e00-\u9fff]+", "_", name).strip("_")


def convert_file(path: Path, category: str, meta_map: dict[int, dict],
                 arc_ver: dict[str, str], tl_ver: dict[str, str]) -> dict | None:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if not lines or not lines[0].startswith("# "):
        return None
    name = lines[0][2:].strip()
    if not name:
        return None

    head = raw.split("\n---\n", 1)[0]
    m = RE_CID.search(head)
    cid = int(m.group(1)) if m else None
    units = RE_UNITS.search(head)
    entry = meta_map.get(cid) if cid is not None else None

    version, ver_source = resolve_version(name, category, cid, meta_map, arc_ver, tl_ver)
    cat_name = str((entry or {}).get("category") or "").strip() or category

    # ── 正文 ──
    body_raw = raw.split("\n---\n", 1)[1] if "\n---\n" in raw else raw
    body = normalize_body(strip_scaffolding(body_raw))

    doc_id = DOC_ID_PREFIX + safe_doc_key(name)
    provenance = f"{REPO_URL}/blob/main/readable/story_zh_CN_chapter_edition/{category}/{path.name}"

    header = [
        f"# {name}",
        f"版本：{version}",
        f"来源：{provenance}",
        f"抓取：{FETCH_DATE}",
        "提取方式：reverse1999-story-compendium（结构化清洗，正文保真未改写）",
        f"章节 ID：{cid if cid is not None else ''}",
        f"分类：{CAT_LABEL.get(category, category)}",
        f"剧情单元：{units.group(1) if units else ''}",
        f"doc_id：{doc_id}",
    ]
    text = "\n".join(header) + "\n\n---\n\n" + body + "\n"

    return {
        "name": name,
        "doc_id": doc_id,
        "chapter_id": cid,
        "category": category,
        "category_resolved": cat_name,
        "version": version,
        "version_source": ver_source,
        "units": units.group(1) if units else "",
        "src_bytes": len(raw.encode("utf-8")),
        "out_bytes": len(text.encode("utf-8")),
        "out_chars": len(body),
        "text": text,
    }


def do_convert(write: bool) -> int:
    meta_map = read_meta_map()
    arc_ver = read_project_arc_versions()
    tl_ver = read_timeline_versions()
    print(f"[meta] chapter_metadata entries={len(meta_map)} "
          f"project_corpus arcs={len(arc_ver)} timeline={len(tl_ver)}")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for category in CATEGORIES:
        for p in sorted((READABLE / category).glob("*.md")):
            r = convert_file(p, category, meta_map, arc_ver, tl_ver)
            if r is None:
                print(f"   [SKIP] {category}/{p.name}")
                continue
            rows.append(r)
            if write:
                (OUTDIR / f"{r['name']}.compendium.md").write_text(r["text"], encoding="utf-8")

    total_chars = sum(r["out_chars"] for r in rows)
    miss_ver = [r for r in rows if not r["version"]]
    by_src: dict[str, int] = {}
    for r in rows:
        k = r["version_source"] or "<unresolved>"
        by_src[k] = by_src.get(k, 0) + 1

    print(f"[convert] files={len(rows)} chars={total_chars:,} "
          f"({total_chars/10000:.1f}万字) write={write}")
    print(f"[convert] version resolved={len(rows)-len(miss_ver)}/{len(rows)} by_source={by_src}")
    for r in miss_ver:
        print(f"   [NO-VER] {r['name']} cat={r['category']} cid={r['chapter_id']}")

    # 命名冲突自检（P1：宁可报警不可静默覆盖）
    existing = {p.stem for p in OUTDIR.glob("*.md") if not p.name.endswith(".compendium.md")}
    clash = sorted({r["name"] for r in rows} & existing)
    print(f"[collision] 与灰机页同名（已用 doc_id 隔离）: {len(clash)} 篇")

    report = {
        "files": len(rows),
        "chars": total_chars,
        "version_by_source": by_src,
        "by_category": {},
        "missing_version": [r["name"] for r in miss_ver],
        "name_clash_with_huiji": clash,
        "rows": [{k: v for k, v in r.items() if k != "text"} for r in rows],
    }
    for r in rows:
        d = report["by_category"].setdefault(r["category"], {"files": 0, "chars": 0})
        d["files"] += 1
        d["chars"] += r["out_chars"]
    rep = ROOT / "data" / "lore" / "wu_ming_zhe" / "compendium_clean_report.json"
    rep.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[report] {rep}")
    return 0


def do_status() -> int:
    got = sorted(OUTDIR.glob("*.compendium.md"))
    chars = sum(len(p.read_text(encoding="utf-8")) for p in got)
    print(f"[status] compendium canon files={len(got)} chars={chars:,}")
    huiji = [p for p in OUTDIR.glob("*.md") if not p.name.endswith(".compendium.md")]
    print(f"[status] huiji canon files={len(huiji)}")
    return 0


def do_verify() -> int:
    """自检：``rule_chapter_id_version`` 对已知真值 + 独立来源的一致性。

    这是「不猜版本」这一决策的**可复现证据**，随管线一起保留（而非一次性脚本）：
      ① 对 chapter_metadata 里已有 version 的 5 位 cid，规则必须与之一致；
      ② 对独立来源 story_canonical.json 的 version，规则必须与之一致。
    两者都不一致就说明规律失效 → 应当停用该规则，而不是继续信任它。
    """
    meta_map = read_meta_map()
    bad = agree = 0
    for cid, e in meta_map.items():
        v = str(e.get("version") or "").strip()
        r = rule_chapter_id_version(cid)
        if not v or not r:
            continue
        if r == v:
            agree += 1
        else:
            bad += 1
            print(f"   [DISAGREE-meta] cid={cid} rule={r} meta={v} "
                  f"zh={e.get('name_zh_CN_archive')}")
    print(f"[verify] 规则 vs chapter_metadata: 一致={agree} 分歧={bad}")

    canon = VENDOR / "structured" / "story_rebuild" / "story_canonical.json"
    a2 = b2 = 0
    if canon.exists():
        data = json.loads(canon.read_text(encoding="utf-8"))
        for c in data.get("chapters", []):
            v = c.get("version")
            r = rule_chapter_id_version(c.get("chapter_id"))
            if not v or not r:
                continue
            if r == v:
                a2 += 1
            else:
                b2 += 1
                print(f"   [DISAGREE-canon] cid={c.get('chapter_id')} rule={r} canon={v}")
        print(f"[verify] 规则 vs story_canonical: 一致={a2} 分歧={b2}")
    return 0 if (bad == 0 and b2 == 0) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--convert", action="store_true", help="结构化清洗并落盘")
    ap.add_argument("--dry-run", action="store_true", help="只统计不落盘")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--verify", action="store_true", help="自检版本解析规则的一致性")
    args = ap.parse_args()
    if args.verify:
        return do_verify()
    if args.status:
        return do_status()
    return do_convert(write=not args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
