# -*- coding: utf-8 -*-
"""图谱修复落盘执行器（作战书 §2.4 Applier——脚本，非代理；单稿终版）。
用法:
  干跑(默认):  ./.venv/Scripts/python.exe scripts/_graph_apply_repairs.py --proposal data/compendium_rag/repairs_v1/proposal.json [--proposal .../repairs_v2/proposal.json]
  落盘:        同上 --apply --version-tag r1
双 schema 兼容:
  v1: target=属主字符串（merge 为 "A → B"；move_edge 的 target=新属主），alias/alias 列表顶层，entity=dict，edges=list
  v2: target=dict{alias,owner_eid,...}；keep_with_note/keep_node/flag_grounding_r4 为 no-op（只验引用）
规则:
  1) 预检(逐条) -> 模拟应用 -> 后检全图（悬空 eid/chunk、重名、eid!=name、边悬空 chunk）全绿才写；
  2) 写前备份 graph.json -> backups/graph.json.prev.<tag>；--apply 才写；
  3) move_edge 旧属主 = 同提案 remove_alias 属主的众数（数据驱动，不硬编码）；
  4) 退出码 0=干跑全绿 / 1=校验失败 / 2=文件缺失。
"""
import argparse, copy, json, shutil, sys, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag import pipeline as P        # noqa: E402

NOOP_TYPES = {"keep_with_note", "keep_node", "flag_grounding_r4", "keep", "flag"}

def _owner(entry):
    """remove_alias/add_alias/reassign_chunk 的属主：v1 target=字符串；v2 target.owner_eid。"""
    t = entry.get("target")
    if isinstance(t, dict):
        return t.get("owner_eid") or t.get("eid")
    return t

def _alias(entry):
    t = entry.get("target")
    if isinstance(t, dict):
        return t.get("alias")
    return entry.get("alias")

def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def chunk_texts():
    s = get_settings()
    kb = P.load_kb(s)
    out = {}
    for c in kb.chunks:
        cid = getattr(c, "chunk_id", None) or getattr(c, "id", None)
        out[cid] = getattr(c, "text", "")
    return out

def index_graph(g):
    ents = {e["eid"]: e for e in g["entities"]}
    names = {}
    for e in g["entities"]:
        names.setdefault(e["name"], []).append(e["eid"])
    return ents, names

def weld_owner_of(proposals):
    cnt = Counter()
    for prop in proposals:
        for e in prop.get("entries", []):
            if e.get("type") == "remove_alias":
                o = _owner(e)
                if o:
                    cnt[o] += 1
    return cnt.most_common(1)[0][0] if cnt else None

def validate_entry(entry, ents, names, ctexts, warnings, edges, weld_owner, removed_pairs=None):
    removed_pairs = removed_pairs or set()
    et = entry.get("type")
    errs = []
    tgt = entry.get("target")
    if et in NOOP_TYPES:
        ref = tgt.get("owner_eid") or tgt.get("eid") if isinstance(tgt, dict) else tgt
        if ref and ref not in ents:
            errs.append(f"no-op 引用实体不存在: {ref}")
        return errs
    if et == "remove_alias":
        owner, alias = _owner(entry), _alias(entry)
        if owner not in ents:
            errs.append(f"属主不存在: {owner}")
        elif alias not in ents[owner].get("aliases", []):
            if (owner, alias) in removed_pairs:
                pass  # 已由前版删除：跨版本幂等重叠，警告由外层记
            else:
                errs.append(f"alias 不在属主别名表: {alias}@{owner}")
    elif et == "add_alias":
        owner, alias = _owner(entry), _alias(entry)
        if owner not in ents:
            errs.append(f"属主不存在: {owner}")
        elif alias in ents[owner].get("aliases", []):
            errs.append(f"alias 已存在: {alias}@{owner}")
        elif not any(alias in t for t in ctexts.values()):
            warnings.append(f"add_alias 语料无逐字（inferred?）: {alias}@{owner}")
    elif et == "add_entity":
        payload = entry.get("entity") if isinstance(entry.get("entity"), dict) else (tgt if isinstance(tgt, dict) else {})
        eid = payload.get("eid") or entry.get("eid")
        name = payload.get("name") or eid
        if not eid:
            errs.append("add_entity 缺 eid")
        else:
            if eid in ents:
                errs.append(f"eid 已存在: {eid}")
            if name and eid != name:
                errs.append(f"eid != name: {eid} vs {name}")
            for a in (payload.get("aliases") or []):
                if not any(a in t for t in ctexts.values()):
                    warnings.append(f"新实体 alias 语料无逐字（inferred?）: {a}@{eid}")
            for cid in (payload.get("chunk_ids") or []):
                if cid not in ctexts:
                    errs.append(f"add_entity 悬空 chunk: {cid}@{eid}")
    elif et == "merge_entities":
        t = entry.get("target")
        if not (isinstance(t, str) and "→" in t):
            errs.append(f"merge target 需 'A → B': {t!r}")
            return errs
        src, dst = [x.strip() for x in t.split("→", 1)]
        if src not in ents:
            errs.append(f"merge 源不存在: {src}")
        if dst not in ents and dst != (entry.get("new_eid")):
            errs.append(f"merge 目标不存在: {dst}")
        for cid in (entry.get("moved_chunks") or []):
            if cid not in ctexts:
                errs.append(f"merge 悬空 chunk: {cid}")
    elif et == "reassign_chunk":
        owner = _owner(entry)
        if owner not in ents:
            errs.append(f"属主不存在: {owner}")
            return errs
        cur = set(ents[owner].get("chunk_ids", []))
        for cid in (entry.get("add_chunk_ids") or []):
            if cid not in ctexts:
                errs.append(f"add chunk 不存在: {cid}")
            elif cid in cur:
                errs.append(f"add chunk 已在属主名下: {cid}@{owner}")
        for cid in (entry.get("removed_weld_chunks") or []):
            if cid not in ctexts:
                errs.append(f"removed chunk 不存在: {cid}")
            elif cid not in cur:
                errs.append(f"removed chunk 不在属主名下: {cid}@{owner}")
    elif et == "move_edge":
        to = entry.get("target")
        if to not in ents:
            errs.append(f"move 目标实体不存在: {to}")
        for item in (entry.get("edges") or []):
            triple = item.get("edge") if isinstance(item, dict) else item
            if not (isinstance(triple, (list, tuple)) and len(triple) == 3):
                errs.append(f"move 边三元组非法: {item}")
                continue
            src, rel, dst = triple
            hit = [e for e in edges if e["src"] == src and e["relation"] == rel and e["dst"] == dst]
            if not hit:
                errs.append(f"move 边不存在: {src}-[{rel}]->{dst}")
            elif weld_owner and weld_owner not in (src, dst):
                errs.append(f"move 边不含焊主端点: {src}-[{rel}]->{dst} (焊主={weld_owner})")
    elif et == "delete_edge":
        for item in (entry.get("edges") or []):
            triple = item.get("edge") if isinstance(item, dict) else item
            if not (isinstance(triple, (list, tuple)) and len(triple) == 3):
                errs.append(f"delete 边三元组非法: {item}")
                continue
            src, rel, dst = triple
            if not any(e["src"] == src and e["relation"] == rel and e["dst"] == dst for e in edges):
                errs.append(f"delete 边不存在: {src}-[{rel}]->{dst}")
    else:
        errs.append(f"未知条目类型: {et}")
    return errs

def apply_entry(entry, g, ents, names, weld_owner):
    et = entry.get("type")
    if et in NOOP_TYPES:
        return
    if et == "remove_alias":
        owner, alias = _owner(entry), _alias(entry)
        ents[owner]["aliases"] = [a for a in ents[owner].get("aliases", []) if a != alias]
    elif et == "add_alias":
        owner, alias = _owner(entry), _alias(entry)
        ents[owner].setdefault("aliases", []).append(alias)
    elif et == "add_entity":
        payload = entry.get("entity") if isinstance(entry.get("entity"), dict) else (entry.get("target") if isinstance(entry.get("target"), dict) else {})
        eid = payload.get("eid") or entry.get("eid")
        ents[eid] = {"eid": eid, "name": payload.get("name") or eid,
                     "type": payload.get("type", "角色"),
                     "aliases": list(payload.get("aliases") or []),
                     "desc": payload.get("desc", ""),
                     "mentions": payload.get("mentions", len(payload.get("chunk_ids") or [])),
                     "chunk_ids": list(payload.get("chunk_ids") or [])}
        g["entities"].append(ents[eid])
    elif et == "merge_entities":
        src, dst = [x.strip() for x in entry["target"].split("→", 1)]
        ents[dst]["aliases"] += [a for a in ents[src].get("aliases", []) if a not in ents[dst].get("aliases", [])]
        ents[dst]["chunk_ids"] += ents[src].get("chunk_ids", [])
        ents[dst]["mentions"] = ents[dst].get("mentions", 0) + ents[src].get("mentions", 0)
        for e in g["edges"]:
            if e["src"] == src:
                e["src"] = dst
            if e["dst"] == src:
                e["dst"] = dst
        g["entities"] = [e for e in g["entities"] if e["eid"] != src]
        del ents[src]
    elif et == "reassign_chunk":
        owner = _owner(entry)
        cur = ents[owner].setdefault("chunk_ids", [])
        for cid in (entry.get("removed_weld_chunks") or []):
            if cid in cur:
                cur.remove(cid)
        for cid in (entry.get("add_chunk_ids") or []):
            if cid not in cur:
                cur.append(cid)
        ents[owner]["mentions"] = len(cur)
    elif et == "move_edge":
        to = entry.get("target")
        for item in (entry.get("edges") or []):
            triple = item.get("edge") if isinstance(item, dict) else item
            src, rel, dst = triple
            for e in g["edges"]:
                if e["src"] == src and e["relation"] == rel and e["dst"] == dst:
                    if e["src"] == weld_owner:
                        e["src"] = to
                    if e["dst"] == weld_owner:
                        e["dst"] = to
    elif et == "delete_edge":
        drop = set()
        for item in (entry.get("edges") or []):
            triple = item.get("edge") if isinstance(item, dict) else item
            drop.add((triple[0], triple[1], triple[2]))
        g["edges"] = [e for e in g["edges"]
                      if (e["src"], e["relation"], e["dst"]) not in drop]

def post_validate(g, ctexts):
    ents, names = index_graph(g)
    errs = []
    if len(ents) != len(g["entities"]):
        errs.append("eid 重复")
    dups = sorted(n for n, ids in names.items() if len(ids) > 1)
    if dups:
        errs.append(f"重名规范节点: {dups[:5]}")
    for e in g["entities"]:
        if e["eid"] != e["name"]:
            errs.append(f"eid!=name: {e['eid']}")
        for cid in e.get("chunk_ids", []):
            if cid not in ctexts:
                errs.append(f"悬空 chunk: {cid}@{e['eid']}")
    for ed in g["edges"]:
        if ed["src"] not in ents:
            errs.append(f"悬空 src: {ed['src']}")
        if ed["dst"] not in ents:
            errs.append(f"悬空 dst: {ed['dst']}")
        for cid in ed.get("chunk_ids", []):
            if cid not in ctexts:
                errs.append(f"边悬空 chunk: {cid}")
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposal", action="append", required=True)
    ap.add_argument("--graph", default=str(ROOT / "data/compendium_rag/graph.json"))
    ap.add_argument("--version-tag", default=time.strftime("v%Y%m%d%H%M"))
    ap.add_argument("--apply", action="store_true", help="默认干跑；加此参数才写盘")
    args = ap.parse_args()

    proposals = []
    for p in args.proposal:
        fp = Path(p)
        if not fp.exists():
            print(f"[FAIL] 提案缺失: {p}"); sys.exit(2)
        proposals.append(load_json(fp))
    gpath = Path(args.graph)
    if not gpath.exists():
        print(f"[FAIL] 图缺失: {gpath}"); sys.exit(2)
    g = load_json(gpath)

    print("加载 chunk 文本（管线同源分块）…")
    ctexts = chunk_texts()
    print(f"chunks: {len(ctexts)}")

    ents, names = index_graph(g)
    weld_owner = weld_owner_of(proposals)
    print(f"焊主（数据驱动推断）: {weld_owner}")

    all_errs, warnings = [], []
    n_entries = 0
    removed_pairs = set()
    g2 = copy.deepcopy(g)
    for prop in proposals:
        for entry in prop.get("entries", []):
            n_entries += 1
            ents2, names2 = index_graph(g2)
            if entry.get("type") == "remove_alias":
                pair = (_owner(entry), _alias(entry))
                if pair in removed_pairs:
                    warnings.append(f"[{entry.get('id', '?')}] 已由前版删除（跨版本幂等重叠）: {pair[1]}@{pair[0]}")
                removed_pairs.add(pair)
            errs = validate_entry(entry, ents2, names2, ctexts, warnings, g2["edges"], weld_owner, removed_pairs)
            if errs:
                all_errs += [f"[{entry.get('id', '?')}] {m}" for m in errs]
                continue  # 该条校验失败：不应用（级联影响如实报）
            apply_entry(entry, g2, ents2, names2, weld_owner)

    # 边去重：merge/move 可能产生同 (src,relation,dst) 重复——图规范零重复（质检结构项基线）
    seen, deduped = {}, []
    for e in g2["edges"]:
        key = (e["src"], e["relation"], e["dst"])
        if key in seen:
            base = seen[key]
            for cid in e.get("chunk_ids", []):
                if cid not in base["chunk_ids"]:
                    base["chunk_ids"].append(cid)
            ev_new = e.get("evidence")
            if ev_new and str(ev_new) not in str(base.get("evidence") or ""):
                base["evidence"] = ((base.get("evidence") or "") + "／" + str(ev_new)).strip("／")
            if isinstance(e.get("confidence"), (int, float)) and isinstance(base.get("confidence"), (int, float)):
                base["confidence"] = max(base["confidence"], e["confidence"])
            if isinstance(e.get("count"), int):
                base["count"] = e["count"] if not isinstance(base.get("count"), int) else max(base["count"], e["count"])
        else:
            seen[key] = e
            deduped.append(e)
    g2["edges"] = deduped

    post_errs = post_validate(g2, ctexts)
    print(f"\n条目: {n_entries} | 预检错误: {len(all_errs)} | 警告: {len(warnings)} | 后检错误: {len(post_errs)}")
    for m in all_errs[:20]:
        print("  [预检]", m)
    for w in warnings[:10]:
        print("  [警告]", w)
    for m in post_errs[:20]:
        print("  [后检]", m)
    print(f"实体: {len(g['entities'])} -> {len(g2['entities'])} | 边: {len(g['edges'])} -> {len(g2['edges'])}")

    if all_errs or post_errs:
        print("[FAIL] 校验未全绿，不写盘。")
        sys.exit(1)
    if not args.apply:
        print("[DRY-RUN] 全绿。加 --apply 才写盘。")
        sys.exit(0)

    bdir = gpath.parent / "backups"
    bdir.mkdir(exist_ok=True)
    bpath = bdir / f"graph.json.prev.{args.version_tag}"
    shutil.copy2(gpath, bpath)
    tmp = gpath.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(g2, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(gpath)
    print(f"[APPLIED] 备份 -> {bpath}；新图 -> {gpath}")

if __name__ == "__main__":
    main()
