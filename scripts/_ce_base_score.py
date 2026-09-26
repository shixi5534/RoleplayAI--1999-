# -*- coding: utf-8 -*-
"""交叉编码器基线打分桥（ce_base_score）——给离线重排实验室喂外部 CE 分。

为什么需要它
------------
``_rank_rerank_lab.py`` 的盲特征族里没有交叉编码器分（实验室本身零模型依赖）。
本脚本作为**桥**：用仓库本地已有的 bge-reranker-base ONNX 交叉编码器（无需下载、
零网络），把 ``_rank_collect.py`` 采集文件里 full 模式每题证据池逐对
(query, chunk_text) 打分，落盘成实验室可直接消费的外部分数文件：

    {"qid": {"<rank>": score, ...}, ...,
     "_meta": {...}}

  - 键为证据名次（1 基字符串化整数，与采集文件 evidence[].rank 一致）；
  - 值为 ``sigmoid(原始 logit)``：bge-reranker 输出是未归一化 logit（可正可负、
    无界），sigmoid 映射到 (0,1) 只影响单调仿射尺度，不改变池内次序；
    实验室做逐题 z 分数归一，故此变换是安全的、且对可读性友好。

口径选择（逐字对齐既有脚本，不自创新口径）
------------------------------------------
  - 加载方式：镜像 ``roleplay.core.knowledge.plot_rerank.CrossEncoderReranker``
    的既有模式（tokenizer.json + onnxruntime CPUExecutionProvider，
    输入 input_ids / attention_mask / 可选 token_type_ids）。
  - 块文本：**只用 chunk.text，不拼篇名/章名/场景名**。这是刻意的：生产精排
    （``ab_ce_rerank.py``）与 ``CrossEncoderReranker.rerank`` 打的就是纯 text；
    评测命中判定虽然用 text+titles 的 blob，但 CE 输入口径跟随生产而非评测。
  - 查询文本：默认用采集行的 ``q_used``（检索实际用的查询，与实验室
    ``FeatureBuilder.question`` 的入参一致）；``--query-field query`` 可切回原始
    query。未做补名映射时两者相同。
  - 文本预处理与生产一致：空白折叠 + 截 1200 字符 + tokenizer 截 512 token。
  - 打分批次按题内分批（每题 pool 对独立成批），保证确定性复检与首遍
    批组成完全一致（int8 动态量化的激活 scale 依赖批内容，跨题混批会让
    同一对的分数随批组成漂移）。

只读承诺：不修改任何库文件、不写任何产物之外的东西、零网关（不 import
requests/httpx/openai/socket，唯一的"网络"是无——模型在本地 models/ 下）。

用法（项目根目录）：
  ./.venv/Scripts/python.exe scripts/_ce_base_score.py \
      --collect data/compendium_rag/reports/rank_collect_smoke_f_top20.json \
      --pool 20 --out data/compendium_rag/reports/ce_base_score_smoke_f.json
  冒烟/debug：
  ./.venv/Scripts/python.exe scripts/_ce_base_score.py --collect <collect.json> \
      --pool 30 --limit 3

退出码：0=成功（个别块缺失只警告并计数）｜1=输入/数据/确定性问题
        （collect 缺失或格式不对、qid 重复、一对待都没打上、确定性复检失败）
        ｜2=模型不可用（onnx/tokenizer 加载失败）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

MODEL_DIR = ROOT / "models" / "bge-reranker-base-onnx"
ONNX_FILE = "onnx/model_int8.onnx"   # 与 ab_ce_rerank.py / CrossEncoderReranker 默认一致
MAX_LEN = 512                        # token 截断（同 CrossEncoderReranker.max_len）
MAX_CHARS = 1200                     # 字符截断（同 CrossEncoderReranker.max_chars）
AUTO_BATCH = 32                      # --batch-size 0 时的自动批大小（≈一题 30 对一批）
INTRA_THREADS = 8                    # 批式离线打分实测（2026-09-26）：8 线程在与其他
                                     # 负载（Ollama 评测链）共存时最稳（~3.5 pairs/s，
                                     # 空闲时可到 ~9）；默认 20 线程受争抢抖动大
DET_TOL = 1e-6                       # 确定性复检容差


def log(msg: str) -> None:
    print(msg, flush=True)


def sigmoid(x: float) -> float:
    """数值稳定版 sigmoid：bge-reranker 原始 logit → (0,1) 相关度分。"""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


class CrossEncoder:
    """最小化 CE 封装：加载一次，批式打分（口径与 CrossEncoderReranker 一致）。"""

    def __init__(self, model_dir: Path, onnx_file: str) -> None:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        tok_path = model_dir / "tokenizer.json"
        onnx_path = model_dir / onnx_file
        if not tok_path.is_file():
            raise FileNotFoundError(f"tokenizer.json 不在 {model_dir}")
        if not onnx_path.is_file():
            raise FileNotFoundError(f"{onnx_file} 不在 {model_dir}")
        self.tokenizer = Tokenizer.from_file(str(tok_path))
        self.pad_id = self.tokenizer.token_to_id("<pad>") or 0
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = INTRA_THREADS
        self.session = ort.InferenceSession(
            str(onnx_path), opts, providers=["CPUExecutionProvider"])
        self.input_names = [i.name for i in self.session.get_inputs()]

    def score_logits(self, pairs: list[tuple[str, str]], batch_size: int) -> list[float]:
        """批式打分，返回原始 logit 列表（顺序与 pairs 一致）。

        与单对路径（CrossEncoderReranker.score_pair）同构：先 pair 编码、
        截 512 token，再手动 padding（attention_mask 屏蔽 pad 位）。
        """
        import numpy as np

        out: list[float] = []
        for i in range(0, len(pairs), batch_size):
            sub = pairs[i:i + batch_size]
            encs = self.tokenizer.encode_batch(sub)
            ids_list = [list(e.ids)[:MAX_LEN] for e in encs]
            tid_list = [list(e.type_ids)[:MAX_LEN] for e in encs]
            length = max(len(x) for x in ids_list)
            input_ids = np.full((len(sub), length), self.pad_id, dtype=np.int64)
            attn = np.zeros((len(sub), length), dtype=np.int64)
            ttype = np.zeros((len(sub), length), dtype=np.int64)
            for j, ids in enumerate(ids_list):
                input_ids[j, :len(ids)] = ids
                attn[j, :len(ids)] = 1
                ttype[j, :len(ids)] = tid_list[j]
            feed = {"input_ids": input_ids, "attention_mask": attn,
                    "token_type_ids": ttype}
            feed = {k: v for k, v in feed.items() if k in self.input_names}
            logits = np.asarray(self.session.run(None, feed)[0]).reshape(len(sub), -1)
            out.extend(float(v) for v in logits[:, 0])
        return out


def build_pairs(row: dict, chunks: dict, pool: int,
                query_field: str) -> tuple[list[tuple[str, str]], list[int], int]:
    """一题的 (pairs, ranks, n_missing)：按证据名次 1..pool 组 CE 输入对。

    块文本只取 chunk.text（不含篇名），缺失块跳过并计数。"""
    q = str(row.get(query_field) or row.get("query") or "").strip()
    pairs: list[tuple[str, str]] = []
    ranks: list[int] = []
    n_missing = 0
    for e in row.get("evidence", []):
        rank = int(e.get("rank") or 0)
        if rank <= 0 or rank > pool:
            continue
        c = chunks.get(e["chunk_id"])
        if c is None:
            n_missing += 1
            continue
        text = " ".join(str(getattr(c, "text", "") or "").split())[:MAX_CHARS]
        pairs.append((q, text))
        ranks.append(rank)
    return pairs, ranks, n_missing


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="bge-reranker 基线打分桥（离线重排实验用）")
    ap.add_argument("--collect", required=True,
                    help="_rank_collect.py 产物 json（需含 full 模式行与 evidence）")
    ap.add_argument("--pool", type=int, default=30,
                    help="给证据名次 1..pool 打分（超过采集窗自动截断）")
    ap.add_argument("--out", default="",
                    help="输出 json（默认 data/compendium_rag/reports/ce_base_score_<stem>.json）")
    ap.add_argument("--batch-size", type=int, default=0,
                    help="题内打分批大小；0=自动（默认 16）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（debug）")
    ap.add_argument("--query-field", default="q_used", choices=["q_used", "query"],
                    help="CE 查询文本字段（默认 q_used，与实验室特征一致）")
    args = ap.parse_args()

    collect_path = Path(args.collect)
    if not collect_path.is_absolute():
        collect_path = ROOT / collect_path
    if not collect_path.is_file():
        log(f"[FAIL] 采集文件不存在：{collect_path}")
        return 1
    try:
        data = json.loads(collect_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        log(f"[FAIL] 采集文件解析失败：{exc!r}")
        return 1
    rows = [r for r in (data.get("rows") or []) if r.get("mode") == "full"]
    if not rows:
        log("[FAIL] 采集文件里没有 full 模式行（本脚本只服务 full 模式证据）")
        return 1
    seen_qids: set[str] = set()
    for r in rows:
        if r["qid"] in seen_qids:
            log(f"[FAIL] full 模式 qid 重复：{r['qid']}（输出格式无法表示）")
            return 1
        seen_qids.add(r["qid"])
    if args.limit:
        rows = rows[:args.limit]

    top_k = int(data.get("top_k") or 0)
    pool = min(int(args.pool), top_k) if top_k else int(args.pool)
    if top_k and args.pool > top_k:
        log(f"[note] --pool={args.pool} > 采集窗 top_k={top_k}，按 {pool} 截断")

    # ── 模型加载（一次）──
    t0 = time.time()
    try:
        ce = CrossEncoder(MODEL_DIR, ONNX_FILE)
    except Exception as exc:  # noqa: BLE001
        log(f"[FAIL] 交叉编码器加载失败：{type(exc).__name__}: {exc}")
        return 2
    batch_size = int(args.batch_size) if args.batch_size > 0 else AUTO_BATCH
    log(f"[CE] {MODEL_DIR.name}/{ONNX_FILE} 加载 {time.time()-t0:.1f}s｜"
        f"输入 {','.join(ce.input_names)}｜batch={batch_size}")

    # ── 库块文本（只读，零网关）──
    kb = P.load_kb(get_settings())
    chunks = kb.retriever.chunks
    log(f"[KB] 块={len(chunks)}（只读，不含篇名拼接口径：CE 输入=纯 chunk.text）")

    # ── 组对 + 打分 ──
    scores: dict[str, dict[str, float]] = {}
    n_pairs = n_missing = 0
    first_pairs: list[tuple[str, str]] = []
    t_start = time.time()
    for i, row in enumerate(rows, 1):
        pairs, ranks, n_miss = build_pairs(row, chunks, pool, args.query_field)
        n_missing += n_miss
        if not pairs:
            log(f"  [warn] {row['qid']} 池内无可打分对，跳过")
            continue
        if i == 1:
            first_pairs = list(pairs)
        logits = ce.score_logits(pairs, batch_size)
        scores[row["qid"]] = {str(rank): sigmoid(lg)
                              for rank, lg in zip(ranks, logits)}
        n_pairs += len(pairs)
        if i % 10 == 0 or i == len(rows):
            log(f"  {i}/{len(rows)}  pairs={n_pairs}  ({time.time()-t_start:.0f}s)")
    total_seconds = time.time() - t_start
    if n_pairs == 0:
        log("[FAIL] 没有任何一对被打分（证据池全空或块全部缺失）")
        return 1
    if n_missing:
        log(f"[warn] 缺失块 {n_missing} 个（对应名次无分数，已在 _meta 计数）")

    # ── 确定性复检：第一题原样重打两遍，max abs diff < 1e-6 ──
    det_a = ce.score_logits(first_pairs, batch_size)
    det_b = ce.score_logits(first_pairs, batch_size)
    det_diff = max(abs(a - b) for a, b in zip(det_a, det_b))
    det_ok = det_diff < DET_TOL
    log(f"[det] 确定性复检：max|Δlogit|={det_diff:.2e} → "
        f"{'PASS' if det_ok else 'FAIL'}（容差 {DET_TOL:g}）")
    if not det_ok:
        log("[FAIL] 确定性复检未通过，不落盘")
        return 1

    # ── 分数分布摘要 ──
    all_scores = [s for m in scores.values() for s in m.values()]
    all_scores.sort()
    n = len(all_scores)
    q = lambda p: all_scores[min(n - 1, int(p * n))]  # noqa: E731
    log(f"[range] 分数 min={all_scores[0]:.6f} p25={q(0.25):.4f} "
        f"中位={q(0.5):.4f} p75={q(0.75):.4f} max={all_scores[-1]:.6f}")

    # ── 落盘 ──
    precision = "int8" if "int8" in ONNX_FILE else "fp32"
    out_path = (Path(args.out) if args.out else
                ROOT / "data" / "compendium_rag" / "reports"
                / f"ce_base_score_{collect_path.stem}.json")
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "_meta": {
            "kind": "ce_base_score",
            "model_dir": str(MODEL_DIR),
            "onnx_file": ONNX_FILE,
            "precision": precision,
            "sigmoid": "score = sigmoid(原始 logit)，bge-reranker 输出为未归一化 logit",
            "ce_input": "纯 chunk.text（空白折叠+截1200字符+截512token），不含篇名/章名",
            "query_field": args.query_field,
            "pool": pool,
            "collect_top_k": top_k,
            "batch_size": batch_size,
            "n_questions": len(scores),
            "n_pairs": n_pairs,
            "n_missing_chunks": n_missing,
            "total_seconds": round(total_seconds, 2),
            "pairs_per_sec": round(n_pairs / total_seconds, 2) if total_seconds else 0.0,
            "determinism_check": {
                "method": "第一题同批组成重打一遍，比较 logit",
                "max_abs_diff": det_diff,
                "tolerance": DET_TOL,
                "pass": det_ok,
            },
            "source_collect": str(collect_path),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        **scores,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    log(f"[out] → {out_path}  ({out_path.stat().st_size / 1024:.0f} KB, "
        f"{n_pairs} pairs, {n_pairs / max(total_seconds, 1e-9):.1f} pairs/s)")

    eta = 9000 / (n_pairs / max(total_seconds, 1e-9))
    log(f"[eta] 按 9000 对（300题×30池）估算 ≈ {eta / 60:.1f} 分钟")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"[CRASH] {exc!r}", flush=True)
        sys.exit(1)
