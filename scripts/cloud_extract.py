# -*- coding: utf-8 -*-
"""云端强模型抽取桥（人工在环）：dump 批次 → 云端产出 → apply 入库。

为什么需要它
------------
本地 7B 抽取质量是灾难级的：``entity_precision 0.675`` /
``relation_precision 0.111`` / ``recall 0.15``——约 89% 的关系是错的。
代码注释里还记录它违反自己的提示词（把 you/she/we 当实体，污染 20 实体 + 186 边）。

本脚本**不调用任何模型**，只做两件事：把语料切批导出成给云端模型读的 md，
以及把云端模型的产出（jsonl）校验清洗后写进抽取缓存。抽取的执行者是
「对话里的云端强模型」，因此 ``.env`` 不需要动、也不需要第三方 API key。

产物链路
--------
    --dump  →  data/knowledge/_cloud/<cid>/batch_<N>.md        （给模型读）
                                   ↓ 云端强模型按规范产出
              data/knowledge/_cloud/<cid>/batch_<N>.jsonl      （模型写）
                                   ↓ --apply
              data/knowledge/plot_cache/<cid>/<hash>.json       （抽取缓存）
                                   ↓ build_plot_graph.py --build-graph（零 LLM 重放）

用法（项目根目录执行）
----------------------
    python -X utf8 scripts/cloud_extract.py --plan --size 40
    python -X utf8 scripts/cloud_extract.py --dump  --batch 0 --size 40
    python -X utf8 scripts/cloud_extract.py --apply --batch 0 --dry-run
    python -X utf8 scripts/cloud_extract.py --apply --batch 0
    python -X utf8 scripts/cloud_extract.py --status
    python -X utf8 scripts/cloud_extract.py --dump --batch 0 --title-contains 77号往事

规范版本：cloud-extract-v1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.plot_corpus import PlotCorpus  # noqa: E402
from roleplay.core.knowledge.plot_graph import (  # noqa: E402
    is_noise_entity,
    norm_name,
    rescue_noise_entity,
)
from roleplay.core.knowledge.relation_vocab import (  # noqa: E402
    CANONICAL_RELATIONS,
    canonicalize_relation,
)

SPEC_VERSION = "cloud-extract-v1"

# 类型白名单：优先取术语表（单一事实源），缺失时用内置兜底。
# 术语表里是 7 类（含「时间」），而 _JSON_SPEC 提示词只写了 6 类——这是已知的
# 待修项（M3），本脚本以术语表的 7 类为准，越界回落「概念」。
_FALLBACK_TYPES: tuple[str, ...] = (
    "角色", "组织", "地点", "概念", "物品", "事件", "时间",
)
_FALLBACK_TYPE = "概念"


def _paths(settings, character_id: str) -> tuple[Path, Path, Path]:
    """(语料文件, 云端工作目录, 抽取缓存目录)"""
    corpus = Path(settings.plot_corpus_dir) / f"plot_corpus_{character_id}.json"
    cloud = Path(settings.plot_cache_dir).parent / "_cloud" / character_id
    cache = Path(settings.plot_cache_dir) / character_id
    return corpus, cloud, cache


def _load_type_whitelist(character_id: str) -> tuple[str, ...]:
    """从 plot_glossary.json 读 type_whitelist；读不到就用内置兜底。"""
    g = ROOT / "data" / "lore" / character_id / "plot_glossary.json"
    try:
        data = json.loads(g.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _FALLBACK_TYPES
    wl = data.get("type_whitelist") if isinstance(data, dict) else None
    if isinstance(wl, list) and wl:
        return tuple(str(x) for x in wl)
    return _FALLBACK_TYPES


# ────────────────────────────── dump ──────────────────────────────

def _spec_section(types: tuple[str, ...]) -> list[str]:
    """给云端模型读的规范段（硬约束 + 受控词表 + 输出格式）。"""
    return [
        "## 硬约束（违反即被 `--apply` 丢弃，且**不报错**——产出即静默消失）",
        "",
        f"1. `type` 只能是以下 {len(types)} 类之一：{' / '.join(types)}。",
        f"   越界一律回落 `{_FALLBACK_TYPE}`。",
        f"2. `relation` 必须命中下方受控词表（{len(CANONICAL_RELATIONS)} 条）。",
        "   否定的、含拉丁字母的、超过 8 个字的谓语一律丢弃。",
        "3. `src` / `dst` 必须是**本块内某个实体的 name 或 alias**，",
        "   不能引用块外实体，不能用代词泛指。",
        "4. 禁止自环：`src` 与 `dst` 不能是同一个实体，**同一实体的正名与别名之间、"
        "别名与别名之间也算自环**。",
        "   例：若本块实体是「无名者」（别名含 凯拉 / Ms. Stranger），"
        "则 `凯拉 → Ms. Stranger` 会被建图判为自环静默丢弃。",
        "5. 禁止把 you / she / he / we / they / 她 / 他 / 我们 等代词当实体正名。",
        "6. 只抽取**文本里明确说了**的关系，不要脑补、不要补背景知识。",
        "   拿不准就留空 relations，宁缺毋滥。",
        "7. 机器转写有识别错误：同一角色的不同拼写（ASR 变体）请收进 `aliases`，",
        "   不要新建重复实体。",
        "",
        f"## 受控词表（{len(CANONICAL_RELATIONS)} 条）",
        "",
        "、".join(CANONICAL_RELATIONS),
        "",
        "## 输出格式",
        "",
        "写一个 `batch_<N>.jsonl`，**每行一个 JSON 对象**，顺序与下方 chunk 一致，",
        "并且**必须原样带回每个 chunk 的 hash**（写错 hash 会导致结果写进错误的缓存槽）。",
        "",
        "```json",
        '{"hash":"<16位hash>","entities":[{"name":"规范称呼","type":"角色",'
        '"aliases":["曾用名/代称/昵称"]}],'
        '"relations":[{"src":"A","dst":"B","relation":"隶属","confidence":0.9}]}',
        "```",
        "",
        "`confidence` 取值 0.0–1.0，只在你**确信**文本明确表达了该关系时给到 0.8 以上。",
        "低于 0.55 的边建图时会被 `min_confidence` 直接拒收。",
        "",
    ]


def _cmd_dump(
    settings,
    character_id: str,
    batch: int,
    size: int,
    title_contains: str | None,
    offset: int | None = None,
) -> int:
    cpath, cloud_dir, _cache = _paths(settings, character_id)
    if not cpath.exists():
        print(f"[error] 剧情语料不存在，请先 --build-corpus：{cpath}")
        return 1
    corpus = PlotCorpus(cpath, character_id=character_id)
    chunks = list(corpus.chunks)
    if title_contains:
        key = title_contains.strip()
        chunks = [c for c in chunks if key in str(c.title or "")]
        if not chunks:
            print(f"[error] 标题筛选「{key}」无匹配块")
            return 1
    # --offset：跳过筛选后的前 N 块。用「从 offset 起取 size 块」的语义，
    # 此时 --batch **只作输出文件标签**、不参与切片 —— 否则换了 --size 之后
    # 批号划分整体错位，已完成的批次会被重复抽取或漏抽。
    if offset is not None:
        chunks = chunks[max(0, offset):]
        if not chunks:
            print(f"[error] --offset {offset} 超出范围")
            return 1
        part = chunks[: max(1, size)]
        total_batches = 1
    else:
        total_batches = max(1, (len(chunks) + max(1, size) - 1) // max(1, size))
        if not 0 <= batch < total_batches:
            print(f"[error] 批次越界：--batch 需在 0..{total_batches - 1}（当前 {batch}）")
            return 1

        part = chunks[batch * size : (batch + 1) * size]
    cloud_dir.mkdir(parents=True, exist_ok=True)
    types = _load_type_whitelist(character_id)

    lines: list[str] = [
        f"# 剧情图谱抽取 · batch {batch:03d}",
        "",
        f"- 角色：`{character_id}`",
        f"- 批次：**{batch}** / 共 {total_batches} 批（每批 {size} 块）｜本批块数：**{len(part)}**",
        f"- 筛选：{('标题含「%s」' % title_contains) if title_contains else '无'}"
        f"｜offset {offset if offset is not None else '-'}",
        f"- 规范版本：{SPEC_VERSION}",
        f"- 输出：`{cloud_dir.name}/batch_{batch:03d}.jsonl`",
        "",
    ]
    lines += _spec_section(types)
    lines += ["## chunks", ""]
    for i, c in enumerate(part):
        lines += [
            f"### [{i}] hash=`{c.hash}`",
            "",
            f"- lang：`{c.lang}`｜version：`{c.version or '—'}`｜arc：`{c.arc or '—'}`",
            f"- doc：`{c.doc_id}`",
            f"- title：{c.title}",
            "",
            "```text",
            str(c.text or "").strip(),
            "```",
            "",
        ]

    md_path = cloud_dir / f"batch_{batch:03d}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    meta = {
        "spec": SPEC_VERSION,
        "character_id": character_id,
        "batch": batch,
        "size": size,
        "total_batches": total_batches,
        "title_contains": title_contains,
        "offset": offset,
        "chunks": [
            {"hash": c.hash, "doc_id": c.doc_id, "lang": c.lang,
             "title": c.title, "version": c.version}
            for c in part
        ],
    }
    (cloud_dir / f"batch_{batch:03d}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[dump] 批次 {batch}/{total_batches - 1}｜{len(part)} 块 → {md_path}")
    print(f"[dump] 待产出：{cloud_dir / f'batch_{batch:03d}.jsonl'}")
    return 0


# ────────────────────────────── apply ──────────────────────────────

def _coerce_str_list(v) -> list[str]:
    if isinstance(v, str):
        return [v.strip()] if v.strip() else []
    if isinstance(v, (list, tuple)):
        return [str(x).strip() for x in v if str(x).strip()]
    return []


def _clean_one(
    item: dict,
    allowed_hashes: set[str],
    types: tuple[str, ...],
) -> tuple[str, dict, dict]:
    """校验并清洗单行产出。返回 (hash, 清洗后 data, 丢弃统计)。"""
    stat = {
        "ent_noise": 0, "ent_rescued": 0, "ent_empty": 0, "ent_type_fallback": 0,
        "rel_no_canon": 0, "rel_endpoint": 0, "rel_selfloop": 0,
        "rel_conf": 0,
    }
    if not isinstance(item, dict):
        return "", {}, stat
    h = str(item.get("hash") or "").strip()
    if h not in allowed_hashes:
        return "", {}, stat  # hash 不在本批 / 写错 → 整条丢弃

    # ── 实体 ──
    entities: list[dict] = []
    names: set[str] = set()
    for e in item.get("entities") or []:
        if not isinstance(e, dict):
            continue
        name = str(e.get("name") or "").strip()
        if not name:
            stat["ent_empty"] += 1
            continue
        if is_noise_entity(name):
            # 5 类误杀打捞：有干净别名时升为正名（与建图侧 rescue 同一规则源）
            rescued = rescue_noise_entity(e)
            if rescued is None:
                stat["ent_noise"] += 1
                continue
            stat["ent_rescued"] += 1
            e = rescued
            name = str(e.get("name") or "").strip()
        etype = str(e.get("type") or "").strip()
        if etype not in types:
            etype = _FALLBACK_TYPE
            stat["ent_type_fallback"] += 1
        aliases = [a for a in _coerce_str_list(e.get("aliases")) if a != name]
        entities.append({"name": name, "type": etype, "aliases": aliases})
        names.add(norm_name(name))
        for a in aliases:
            names.add(norm_name(a))

    # ── 关系 ──
    relations: list[dict] = []
    for r in item.get("relations") or []:
        if not isinstance(r, dict):
            continue
        src = str(r.get("src") or "").strip()
        dst = str(r.get("dst") or "").strip()
        if not src or not dst:
            continue
        if src == dst:
            stat["rel_selfloop"] += 1
            continue
        # 端点必须落在本块实体（正名或别名）内
        if norm_name(src) not in names or norm_name(dst) not in names:
            stat["rel_endpoint"] += 1
            continue
        canon = canonicalize_relation(str(r.get("relation") or ""))
        if canon is None:
            stat["rel_no_canon"] += 1
            continue
        try:
            conf = float(r.get("confidence", 0.7) or 0.7)
        except (TypeError, ValueError):
            conf = 0.7
            stat["rel_conf"] += 1
        conf = max(0.0, min(1.0, conf))
        relations.append(
            {"src": src, "dst": dst, "relation": canon, "confidence": round(conf, 4)}
        )

    return h, {"entities": entities, "relations": relations}, stat


def _cmd_apply(
    settings, character_id: str, batch: int, dry_run: bool
) -> int:
    _cpath, cloud_dir, cache_dir = _paths(settings, character_id)
    meta_path = cloud_dir / f"batch_{batch:03d}.meta.json"
    jsonl_path = cloud_dir / f"batch_{batch:03d}.jsonl"
    if not meta_path.exists():
        print(f"[error] 缺少 meta（先跑 --dump）：{meta_path}")
        return 1
    if not jsonl_path.exists():
        print(f"[error] 缺少产出文件：{jsonl_path}")
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    allowed = {c["hash"] for c in meta.get("chunks") or []}
    types = _load_type_whitelist(character_id)

    rows: list[dict] = []
    bad_lines = 0
    for ln, line in enumerate(
        jsonl_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        try:
            rows.append(json.loads(s))
        except ValueError:
            bad_lines += 1
            print(f"[warn] 第 {ln} 行不是合法 JSON，已跳过")

    total = {k: 0 for k in (
        "ent_noise", "ent_rescued", "ent_empty", "ent_type_fallback",
        "rel_no_canon", "rel_endpoint", "rel_selfloop", "rel_conf",
    )}
    written = 0
    covered: set[str] = set()
    empty_blocks = 0
    dup = 0
    for item in rows:
        h, data, stat = _clean_one(item, allowed, types)
        for k, v in stat.items():
            total[k] += v
        if not h:
            continue
        if h in covered:
            dup += 1
            continue
        covered.add(h)
        if not data["entities"] and not data["relations"]:
            empty_blocks += 1
        if not dry_run:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / f"{h}.json").write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
        written += 1

    # 类型分布体检：概念类占比过高 = 把叙述里的普通抽象名词当实体抽了
    # （实测有一批抽出 597 实体 / 325 概念 = 54%，而正常批次是 3%~10%）。
    # 这类假节点会霸占别名索引（`truth` 被注册后含该词的查询会被误链接）。
    type_dist: dict[str, int] = {}
    ent_total = 0
    for item in rows:
        h, data, _st = _clean_one(item, allowed, types)
        if not h:
            continue
        for e in data["entities"]:
            t = e.get("type") or "未分类"
            type_dist[t] = type_dist.get(t, 0) + 1
            ent_total += 1

    missing = sorted(allowed - covered)
    tag = "[dry-run] " if dry_run else ""
    print(f"[apply] {tag}批次 {batch}｜产出 {len(rows)} 行｜写入 {written} 块"
          f"｜覆盖 {len(covered)}/{len(allowed)}")
    if type_dist:
        top = " / ".join(f"{k} {v}" for k, v in sorted(
            type_dist.items(), key=lambda kv: -kv[1]))
        print(f"[apply] 类型分布：{top}")
        con = type_dist.get("概念", 0)
        if ent_total and con / ent_total > 0.2:
            print(
                f"[apply][warn] 概念类占比 {con}/{ent_total} = {con / ent_total:.0%}，超过 20% 阈值。"
                "正常批次是 3%~15%——很可能是把叙述里的普通抽象名词"
                "（truth / ritual / side effects / research 之类）当实体抽了。"
                "这些假节点会霸占别名索引，建议退回清理后重新 --apply。"
            )
    if bad_lines:
        print(f"[apply] 非法 JSON 行：{bad_lines}")
    if dup:
        print(f"[apply] 重复 hash 行（已去重）：{dup}")
    print(
        "[apply] 丢弃：实体 噪声 {ent_noise} / 空名 {ent_empty}"
        "｜类型回落 {ent_type_fallback}"
        "｜关系 非受控 {rel_no_canon} / 端点越界 {rel_endpoint}"
        " / 自环 {rel_selfloop} / 置信度异常 {rel_conf}".format(**total)
    )
    if empty_blocks:
        print(f"[apply] 提示：{empty_blocks} 块实体与关系均为空（会被建图计为 skipped）")
    if missing:
        print(f"[apply] 未覆盖 {len(missing)} 块（前 5）：{missing[:5]}")
        print("[apply] 缺块会被 --build-graph 当作未抽取、转去调 LLM——务必补齐")
        return 1
    if dry_run:
        print("[apply] dry-run 未写盘")
        return 0
    print(f"[apply] 缓存目录 {cache_dir}")
    print(f"[apply] 下一步：python -X utf8 scripts/build_plot_graph.py "
          f"--character {character_id} --build-graph")
    return 0


# ────────────────────────────── 其它 ──────────────────────────────

def _cmd_plan(settings, character_id: str, size: int) -> int:
    cpath, cloud_dir, cache_dir = _paths(settings, character_id)
    if not cpath.exists():
        print(f"[error] 剧情语料不存在：{cpath}")
        return 1
    corpus = PlotCorpus(cpath, character_id=character_id)
    chunks = list(corpus.chunks)
    total_batches = max(1, (len(chunks) + size - 1) // size)
    done = 0
    if cache_dir.exists():
        done = len(list(cache_dir.glob("*.json")))
    print(f"[plan] 语料 {cpath.name}｜{len(chunks)} 块")
    print(f"[plan] 每批 {size} 块 → 共 {total_batches} 批")
    print(f"[plan] 已有抽取缓存 {done} 条（{cache_dir}）")
    print(f"[plan] 云端工作目录 {cloud_dir}")
    return 0


def _cmd_status(settings, character_id: str) -> int:
    _cpath, cloud_dir, cache_dir = _paths(settings, character_id)
    if not cloud_dir.exists():
        print(f"[status] 尚无云端批次目录：{cloud_dir}")
        return 0
    metas = sorted(cloud_dir.glob("batch_*.meta.json"))
    if not metas:
        print("[status] 尚无 --dump 批次")
        return 0
    print(f"[status] {'批次':<8}{'块数':>6}{'已产出':>9}{'已写入':>9}  状态")
    for m in metas:
        meta = json.loads(m.read_text(encoding="utf-8"))
        b = meta["batch"]
        n = len(meta.get("chunks") or [])
        jl = cloud_dir / f"batch_{b:03d}.jsonl"
        produced = 0
        if jl.exists():
            produced = sum(
                1 for s in jl.read_text(encoding="utf-8").splitlines() if s.strip()
            )
        written = 0
        for c in meta.get("chunks") or []:
            if (cache_dir / f"{c['hash']}.json").exists():
                written += 1
        if produced == 0:
            st = "待产出"
        elif written >= n:
            st = "已入库"
        else:
            st = "待 apply"
        print(f"[status] {b:<8}{n:>6}{produced:>9}{written:>9}  {st}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="云端强模型抽取桥（人工在环）：dump → 云端产出 → apply"
    )
    ap.add_argument("--character", default="wu_ming_zhe", help="角色 id")
    ap.add_argument("--dump", action="store_true", help="导出批次 md 供云端模型抽取")
    ap.add_argument("--apply", action="store_true", help="校验并写入云端产出 jsonl")
    ap.add_argument("--status", action="store_true", help="查看各批次进度")
    ap.add_argument("--plan", action="store_true", help="查看语料规模与批次数")
    ap.add_argument("--batch", type=int, default=0, help="批次号（从 0 开始）")
    ap.add_argument("--size", type=int, default=40, help="每批块数")
    ap.add_argument("--title-contains", help="dump 时只取标题包含该子串的块")
    ap.add_argument("--offset", type=int, default=None,
                    help="dump 时跳过筛选后的前 N 块（改 --size 后继续推进用，防批号错位重抽）")
    ap.add_argument("--dry-run", action="store_true", help="apply 时只校验不写盘")
    args = ap.parse_args()

    settings = get_settings()
    if args.plan:
        return _cmd_plan(settings, args.character, args.size)
    if args.dump:
        return _cmd_dump(
            settings, args.character, args.batch, args.size,
            args.title_contains, args.offset,
        )
    if args.apply:
        return _cmd_apply(settings, args.character, args.batch, args.dry_run)
    if args.status:
        return _cmd_status(settings, args.character)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
