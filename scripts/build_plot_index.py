# -*- coding: utf-8 -*-
"""剧情语料的**语义向量索引**（跨语言检索的底座）。

为什么需要它（承接分诊结论）
    剧情语料是**英文 B 站 ASR**（7964/9021 块），用户提问是**中文**，而图谱
    `fingerprint.embedder` 一直是 `none`——**没有任何跨语言兜底**。
    分诊实测：300 题失败里 **111 题 / 126 个缺失证据组是「别名桥缺失」**，
    即"实体在图里，但查询里根本没出现它的任何名字"（「海盗船上的歌手是谁」
    「雾中女巫」「自囚的医生」）。这类问题**补别名解决不了**，必须能按语义找块。

设计要点
    - 向量与语料**分离存放**：`plot_index_<cid>.npz`（向量）+ `.json`（指纹/元数据），
      删掉即回到纯词法世界（整层可回滚）；
    - **指纹校验**：换嵌入模型/维度变化/语料 hash 变化 → 索引判为过期，
      检索侧静默跳过（绝不拿旧向量配新模型，那会静默产出垃圾结果）；
    - **增量重建**：按 chunk 文本 hash 复用旧向量，只补新增块；
    - 实体名向量（可选）用于「查询→实体」的语义链接。

用法（项目根目录）
    .venv/Scripts/python.exe -X utf8 scripts/build_plot_index.py --build
    .venv/Scripts/python.exe -X utf8 scripts/build_plot_index.py --status
    .venv/Scripts/python.exe -X utf8 scripts/build_plot_index.py --probe "洞穴的囚徒篇里海盗船上的歌手是谁？"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.embedder import build_embedder  # noqa: E402
from roleplay.core.knowledge.plot_corpus import PlotCorpus  # noqa: E402

INDEX_SCHEMA = "plot-index-v1"


def paths(settings, cid: str) -> tuple[Path, Path, Path]:
    base = Path(settings.plot_corpus_dir)
    return (base / f"plot_index_{cid}.npz",
            base / f"plot_index_{cid}.json",
            base / f"plot_corpus_{cid}.json")


def corpus_sha16(cpath: Path) -> str:
    """语料文件指纹（前 16 位）：语料变了索引就必须重建。"""
    h = hashlib.sha256()
    with cpath.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def load_index(settings, cid: str):
    """返回 ``(vectors, hashes, meta)`` 或 ``(None, None, meta_or_None)``。"""
    npath, jpath, _ = paths(settings, cid)
    if not (npath.is_file() and jpath.is_file()):
        return None, None, None
    try:
        meta = json.loads(jpath.read_text(encoding="utf-8"))
        with np.load(npath, allow_pickle=False) as z:
            vecs = z["vectors"]
            hashes = z["hashes"]
    except Exception as exc:  # 半截文件/格式变更都要能被安全跳过
        return None, None, {"error": str(exc)}
    return vecs, hashes, meta


def check_fresh(meta: dict | None, *, embedder: str, dim: int, csha: str) -> tuple[bool, str]:
    """索引新鲜度：schema / 模型 / 维度 / 语料指纹 四项全对才算可用。"""
    if not meta:
        return False, "索引不存在"
    if meta.get("schema") != INDEX_SCHEMA:
        return False, f"schema 不符（{meta.get('schema')}）"
    if meta.get("embedder") != embedder:
        return False, f"嵌入模型不符（索引 {meta.get('embedder')} ≠ 当前 {embedder}）"
    if int(meta.get("dim") or 0) != int(dim):
        return False, f"维度不符（{meta.get('dim')} ≠ {dim}）"
    if meta.get("corpus_sha16") != csha:
        return False, "语料指纹不符（语料已变，需重建）"
    return True, "ok"


def _embed_all(embedder, texts: list[str], *, batch: int = 16,
               progress=None) -> np.ndarray:
    """分批嵌入并 L2 归一化（归一化后余弦=点积，检索更快也更稳）。"""
    out: list[np.ndarray] = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        vecs = np.asarray(embedder.embed(chunk), dtype=np.float32)
        out.append(vecs)
        if progress:
            progress(min(i + batch, len(texts)), len(texts))
    mat = np.vstack(out) if out else np.zeros((0, embedder.dim), dtype=np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def _plot_embedder(settings):
    """剧情层**实际使用**的嵌入器（``plot_embed_model`` 优先，缺失则跟随全局）。

    为什么必须用它、而不能用全局 ``build_embedder``（2026-09-16 实测踩到的坑）：
    全局 ``embed_model`` 常是英文单语的 ``nomic-embed-text``（768 维，还被 lore 向量库
    用着），而剧情层用 ``plot_embed_model=bge-m3``（1024 维）。索引由剧情层消费——
    用全局模型去建/校验，会得到两个错误结论：
      ① ``--status`` 永远报「模型不符」（其实索引是好的，只是校验对象错了）；
      ② 最严重：``--build`` 会用错模型**重建**，直接毁掉可用的 bge-m3 索引。
    """
    try:
        from roleplay.core.knowledge.factory import _build_plot_embedder
        return _build_plot_embedder(settings)
    except Exception:  # pragma: no cover - 工厂不可用时退回全局
        return build_embedder(settings)


def cmd_build(settings, cid: str, *, with_entities: bool, limit: int) -> int:
    _, _, cpath = paths(settings, cid)
    if not cpath.is_file():
        print(f"[FAIL] 语料不存在：{cpath}（先跑 build_plot_graph.py --build-corpus）")
        return 2
    corpus = PlotCorpus(cpath, character_id=cid)
    if not corpus.chunks:
        print("[FAIL] 语料为空")
        return 2
    chunks = corpus.chunks[:limit] if limit else corpus.chunks
    embedder = _plot_embedder(settings)
    print(f"[index] 模型 {embedder.name}｜维度 {embedder.dim}｜语料 {len(chunks)} 块")

    # ── 增量：复用旧索引里文本相同的向量 ──
    old_vecs, old_hashes, old_meta = load_index(settings, cid)
    reuse: dict[str, int] = {}
    if old_vecs is not None and old_meta and old_meta.get("embedder") == embedder.name:
        for row, h in enumerate(old_hashes):
            reuse.setdefault(str(h), row)
    todo = [i for i, c in enumerate(chunks) if str(c.hash) not in reuse]
    print(f"[index] 可复用 {len(chunks) - len(todo)} 块｜需嵌入 {len(todo)} 块")
    if limit:
        todo = [i for i in todo if i < limit]

    new_vecs = None
    if todo:
        t0 = time.time()

        def _p(done: int, total: int) -> None:
            if done % 160 == 0 or done == total:
                el = time.time() - t0
                rate = done / el if el else 0
                eta = (total - done) / rate if rate else 0
                print(f"    {done}/{total}（{rate:.1f} 块/s，剩 ~{eta / 60:.1f} min）", flush=True)

        new_vecs = _embed_all(embedder, [chunks[i].text for i in todo], progress=_p)

    dim = int(embedder.dim)
    mat = np.zeros((len(chunks), dim), dtype=np.float32)
    filled = np.zeros(len(chunks), dtype=bool)
    if old_vecs is not None:
        for i, c in enumerate(chunks):
            row = reuse.get(str(c.hash))
            if row is not None and row < len(old_vecs):
                mat[i] = old_vecs[row]
                filled[i] = True
    for k, i in enumerate(todo):
        if new_vecs is not None and k < len(new_vecs):
            mat[i] = new_vecs[k]
            filled[i] = True
    hashes = np.array([str(c.hash) for c in chunks], dtype="U16")

    npath, jpath, _ = paths(settings, cid)
    np.savez_compressed(npath, vectors=mat, hashes=hashes)

    ent_ids: list[str] = []
    ent_vecs = np.zeros((0, dim), dtype=np.float32)
    if with_entities:
        from roleplay.core.knowledge.graph_store import GraphStore

        gpath = Path(settings.plot_graph_dir) / f"plot_graph_{cid}.json"
        store = GraphStore(gpath)
        ents = store.entities()
        texts, ids = [], []
        for e in ents:
            nm = str(e.get("name") or "")
            if not nm:
                continue
            al = [str(a) for a in (e.get("aliases") or [])][:3]
            texts.append(" / ".join([nm] + al))
            ids.append(str(e.get("id")))
        if texts:
            print(f"[index] 实体名 {len(texts)} 条 …")
            ent_vecs = _embed_all(embedder, texts)
            ent_ids = ids
            np.savez_compressed(npath, vectors=mat, hashes=hashes,
                                ent_vectors=ent_vecs,
                                ent_ids=np.array(ent_ids, dtype="U32"))

    meta = {
        "schema": INDEX_SCHEMA,
        "character": cid,
        "embedder": embedder.name,
        "dim": dim,
        "count": len(chunks),
        "filled": int(filled.sum()),
        "corpus_sha16": corpus_sha16(cpath),
        "entity_count": len(ent_ids),
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    jpath.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[index] 落盘 {npath.name}（{npath.stat().st_size / 1e6:.1f} MB）+ {jpath.name}")
    print(f"[index] {json.dumps(meta, ensure_ascii=False)}")
    return 0


def cmd_status(settings, cid: str) -> int:
    _, _, cpath = paths(settings, cid)
    vecs, hashes, meta = load_index(settings, cid)
    if meta is None:
        print("[index] 未构建")
        return 0
    if vecs is None:
        print(f"[index] 读取失败：{meta.get('error')}")
        return 2
    embedder = _plot_embedder(settings)
    csha = corpus_sha16(cpath) if cpath.is_file() else ""
    ok, why = check_fresh(meta, embedder=embedder.name, dim=embedder.dim, csha=csha)
    print(f"[index] {json.dumps(meta, ensure_ascii=False)}")
    print(f"[index] 矩阵 {vecs.shape}｜当前模型 {embedder.name}({embedder.dim})"
          f"｜新鲜度 {'✅ ' + why if ok else '❌ ' + why}")
    return 0 if ok else 3


def cmd_probe(settings, cid: str, query: str, top: int) -> int:
    vecs, hashes, meta = load_index(settings, cid)
    if vecs is None:
        print("[FAIL] 索引不可用（先 --build）")
        return 2
    _, _, cpath = paths(settings, cid)
    corpus = PlotCorpus(cpath, character_id=cid)
    by_hash = {str(c.hash): c for c in corpus.chunks}
    embedder = _plot_embedder(settings)
    if meta.get("embedder") != embedder.name:
        print(f"[FAIL] 索引模型 {meta.get('embedder')} ≠ 当前 {embedder.name}")
        return 2
    qv = np.asarray(embedder.embed_query(query), dtype=np.float32)
    qv = qv / (np.linalg.norm(qv) or 1.0)
    sims = vecs @ qv
    order = np.argsort(-sims)[:top]
    print(f"[probe] {query}")
    for rank, i in enumerate(order, 1):
        c = by_hash.get(str(hashes[i]))
        print(f"   #{rank} cos={sims[i]:.3f} {str(hashes[i])} "
              f"{(c.source_kind if c else '?')} {(c.text[:66] if c else '')!r}")
    return 0


def cmd_crosslingual_check(settings, cid: str) -> int:
    """**跨语言就绪自检**：当前嵌入器到底能不能把中文问句对齐到英文语料？

    为什么单独做这一个检查：本层唯一的前提就是"跨语言"，而这一步**无法从配置看出**——
    `nomic-embed-text` 看起来是通用嵌入器，实测却是英文单语：中文问句的 top-4 命中的
    是 4 段毫不相关的中文块（匹配"这也是中文"，不是"意思相关"），开起来 300 题
    严格通过率直接 **−3.7pt**。所以换模型后**先跑这个检查**，再决定要不要开。
    """
    # 必须验**剧情层实际要用的那个**嵌入器（plot_embed_model），不是全局 embed_model：
    # 两者可以不同（全局还被 lore 向量库用着，常是 nomic-768）。
    # 早先版本验全局模型，在剧情层已切到 bge-m3 之后仍报"跨语言不可用"——闸门指错了对象。
    from roleplay.core.knowledge.embedder import build_embedder
    try:
        from roleplay.core.knowledge.factory import _build_plot_embedder  # noqa: PLC0415
        embedder = _build_plot_embedder(settings)
    except Exception:  # pragma: no cover - 工厂不可用时退回全局
        embedder = _plot_embedder(settings)
    print(f"[check] 嵌入器 {embedder.name}｜维度 {embedder.dim}"
          f"（plot_embed_model={getattr(settings, 'plot_embed_model', '') or '跟随全局'}）")
    # 每条 = (中文问句, 英文正确句, [干扰句…])
    #
    # ⚠️ 干扰句里**必须混入中文**——这正是本层真实失败模式的关键。
    #    只用英文干扰句时，nomic-embed-text 实测 4/4 全过（正确 0.46–0.53 vs 干扰 0.31–0.44），
    #    看起来"能跨语言"；但一放到真实语料（9021 块里有 1691 块中文）就崩：
    #    它匹配的是"这段也是中文"，不是"这段意思相关"——中文块无条件压过英文正确块。
    #    加入中文干扰后，这个弱点立刻暴露，检查才真的能当"上线闸门"用。
    cases = [
        ("海盗船上的歌手是谁？",
         "Sotheby is the singer on the pirate ship.",
         ["The train departed at dawn and nobody looked back.",
          "会议记录：今天的天气很好，大家都同意推迟到下周再讨论预算。"]),
        ("自囚在中央塔里的医生是谁？",
         "The physician imprisoned himself in the central tower.",
         ["The market opened early and the crowd was loud.",
          "厨房里的水壶已经烧开了，请记得关火并清洗灶台。"]),
        ("雾中的女巫真名是什么？",
         "The Fog Lady is a witch of London's Cross Street.",
         ["The library closes at six on weekdays.",
          "图书馆每天早上九点开门，周五下午提前一小时闭馆。"]),
        ("孩子们在森林里遇到了什么怪物？",
         "The children encountered a monster in the forest near Green Lake.",
         ["The recipe needs two eggs and a cup of flour.",
          "这份食谱需要两个鸡蛋、一杯面粉和少许食盐。"]),
    ]
    ok = 0
    for zh, right, wrongs in cases:
        qv = np.asarray(embedder.embed_query(zh), dtype=np.float32)
        qv = qv / (np.linalg.norm(qv) or 1.0)
        docs = [right] + wrongs
        dv = np.asarray(embedder.embed(docs), dtype=np.float32)
        dv = dv / np.maximum(np.linalg.norm(dv, axis=1, keepdims=True), 1e-9)
        sims = dv @ qv
        win = bool(np.argmax(sims) == 0)
        ok += int(win)
        print(f"  {'✅' if win else '❌'} {zh}")
        print(f"      正确 {sims[0]:.3f}｜干扰 {[round(float(s), 3) for s in sims[1:]]}")
    print()
    rate = ok / len(cases)
    if rate >= 0.75:
        print(f"[check] 跨语言可用（{ok}/{len(cases)}）→ 可 `--build` 后设 "
              f"ROLEPLAY_PLOT_SEMANTIC_ENABLED=true，并复跑 300 题消融确认。")
        return 0
    print(f"[check] ❌ 跨语言不可用（{ok}/{len(cases)}）：该嵌入器无法把中文问句对齐到"
          f"英文句子。\n         保持 ROLEPLAY_PLOT_SEMANTIC_ENABLED=false；"
          f"换多语言模型（bge-m3 / paraphrase-multilingual / qwen3-embedding）后重测。")
    return 4


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情语料语义向量索引")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--probe")
    ap.add_argument("--crosslingual-check", action="store_true",
                    help="自检：当前嵌入器能否做中文→英文跨语言检索")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 块（冒烟）")
    ap.add_argument("--no-entities", action="store_true", help="不建实体名向量")
    args = ap.parse_args()
    settings = get_settings()
    if args.crosslingual_check:
        return cmd_crosslingual_check(settings, args.character)
    if args.build:
        return cmd_build(settings, args.character, with_entities=not args.no_entities,
                         limit=args.limit)
    if args.probe:
        return cmd_probe(settings, args.character, args.probe, args.top)
    return cmd_status(settings, args.character)


if __name__ == "__main__":
    raise SystemExit(main())
