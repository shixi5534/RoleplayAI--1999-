# -*- coding: utf-8 -*-
"""交叉编码器 v2 打分桥（ce_v2_score）——torch fp32 版大模型 CE 外部分数。

为什么需要它
------------
``_ce_base_score.py`` 走的是 bge-reranker-base 的 ONNX int8 路线（生产同款、
零 torch 依赖）。本脚本是它的 **torch fp32 兄弟版**：加载 ``models/`` 下
transformers 格式的交叉编码器整权重（bge-reranker-large / bge-reranker-v2-m3，
ModelScope 快照已落盘），对 ``_rank_collect.py`` 采集文件的 full 模式证据池
逐对 (query, chunk_text) 打分，输出契约与 ``_ce_base_score.py`` 完全一致：

    {"qid": {"<rank>": score, ...}, ..., "_meta": {...}}

  - 键为证据名次（1 基字符串化整数，与采集文件 evidence[].rank 一致）；
  - 值为 ``sigmoid(原始 logit)``：bge-reranker 输出是未归一化 logit（可正可负、
    无界），sigmoid 映射到 (0,1) 只影响单调仿射尺度，不改变池内次序；
    实验室做逐题 z 分数归一，故此变换是安全的、且对可读性友好。

口径（逐字对齐 ``_ce_base_score.py`` / 生产 CrossEncoderReranker）
------------------------------------------------------------------
  - 块文本：**只用 chunk.text，不拼篇名/章名/场景名**。空白折叠 + 截 1200
    字符 + tokenizer 截 --max-length（默认 512）token；
  - 查询文本：默认用采集行的 ``q_used``（检索实际用的查询）；``--query-field
    query`` 可切回原始 query；
  - 批次按题内分批：每题池对独立成批，确定性复检与首遍批组成完全一致
    （同批同线程数下 CPU fp32 前向是确定的，跨题混批无必要也无好处）；
  - fp32 / CPU / ``torch.set_num_threads(--threads)``（默认 4）：后台常有
    评测链在跑，4 线程是"忙机"让步档；基准数据见 _meta.torch_threads。

确定性：同一批（首题池对）原样重打两遍，max|Δlogit| < 1e-6 才落盘。

只读承诺：不修改任何库文件、不写产物之外的文件、零网关（不 import
requests/httpx/openai/socket，唯一的"网络"是无——模型在本地 models/ 下）。

用法（项目根目录）：
  ./.venv/Scripts/python.exe scripts/_ce_v2_score.py \
      --model bge-reranker-large \
      --collect data/compendium_rag/reports/rank_collect_smoke_f_top20.json \
      --pool 20 --out data/compendium_rag/reports/ce_v2large_smoke_f.json
  全量（300 题 × 30 池 ≈ 9000 对）：
  ./.venv/Scripts/python.exe scripts/_ce_v2_score.py \
      --model bge-reranker-large \
      --collect data/compendium_rag/reports/rank_collect_300_cn_top30.json \
      --pool 30 --out data/compendium_rag/reports/ce_large_300_cn.json
  冒烟/debug：
  ./.venv/Scripts/python.exe scripts/_ce_v2_score.py --model <dir> \
      --collect <collect.json> --pool 30 --limit 3

退出码：0=成功（个别块缺失只警告并计数）｜1=输入/数据/确定性问题
        （collect 缺失或格式不对、qid 重复、一对待都没打上、确定性复检失败）
        ｜2=模型不可用（tokenizer/model 加载失败）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

MAX_LEN = 512                        # token 截断默认值（同 CrossEncoderReranker.max_len）
MAX_CHARS = 1200                     # 字符截断（同 CrossEncoderReranker.max_chars）
DET_TOL = 1e-6                       # 确定性复检容差
ETA_PAIRS = 9000                     # ETA 基准对数（300 题 × 30 池）


def log(msg: str) -> None:
    print(msg, flush=True)


def sigmoid(x: float) -> float:
    """数值稳定版 sigmoid：bge-reranker 原始 logit → (0,1) 相关度分。"""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def resolve_model_dir(spec: str) -> Path:
    """--model 解析：绝对路径直用；裸名先找 models/<名>，再退仓库根相对。"""
    p = Path(spec)
    if p.is_absolute():
        return p
    cand = ROOT / "models" / spec
    if cand.is_dir():
        return cand
    return ROOT / spec


class TorchCrossEncoder:
    """最小化 torch CE 封装：加载一次，fp32 CPU，批式打分。

    与 ``_ce_base_score.py`` 的 ONNX 路径同构：pair 编码 → 截 max_length
    token → 动态 padding（attention_mask 屏蔽 pad 位）→ 取 [CLS] logit。
    """

    def __init__(self, model_dir: Path, max_length: int) -> None:
        try:
            from transformers.utils import logging as hf_logging
            hf_logging.disable_progress_bar()
        except Exception:  # noqa: BLE001
            pass
        if not (model_dir / "config.json").is_file():
            raise FileNotFoundError(f"config.json 不在 {model_dir}")
        if not list(model_dir.glob("*.safetensors")):
            raise FileNotFoundError(f"{model_dir} 下没有 *.safetensors")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(
            str(model_dir), dtype=torch.float32)
        self.model.eval()
        self.max_length = int(max_length)

    def score_logits(self, pairs: list[tuple[str, str]],
                     batch_size: int) -> list[float]:
        """批式打分，返回原始 logit 列表（顺序与 pairs 一致）。"""
        out: list[float] = []
        for i in range(0, len(pairs), batch_size):
            sub = pairs[i:i + batch_size]
            enc = self.tokenizer(
                list(sub), truncation=True, max_length=self.max_length,
                padding=True, return_tensors="pt")
            with torch.inference_mode():
                logits = self.model(**enc).logits
            out.extend(float(v) for v in logits[:, 0].tolist())
        return out


def build_pairs(row: dict, chunks: dict, pool: int,
                query_field: str) -> tuple[list[tuple[str, str]], list[int], int]:
    """一题的 (pairs, ranks, n_missing)：按证据名次 1..pool 组 CE 输入对。

    块文本只取 chunk.text（不含篇名），缺失块跳过并计数。与
    ``_ce_base_score.py`` 逐字同口径。"""
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

    ap = argparse.ArgumentParser(
        description="bge-reranker torch fp32 打分桥（输出契约同 _ce_base_score.py）")
    ap.add_argument("--model", required=True,
                    help="模型目录（models/ 下裸名如 bge-reranker-large，或任意路径）")
    ap.add_argument("--collect", required=True,
                    help="_rank_collect.py 产物 json（需含 full 模式行与 evidence）")
    ap.add_argument("--pool", type=int, default=30,
                    help="给证据名次 1..pool 打分（超过采集窗自动截断）")
    ap.add_argument("--out", default="",
                    help="输出 json（默认 data/compendium_rag/reports/ce_v2_<模型>_<collect>.json）")
    ap.add_argument("--batch-size", type=int, default=16,
                    help="题内打分批大小（默认 16）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（debug）")
    ap.add_argument("--max-length", type=int, default=MAX_LEN,
                    help=f"tokenizer 截断长度（默认 {MAX_LEN}）")
    ap.add_argument("--threads", type=int, default=4,
                    help="torch CPU 线程数（默认 4，忙机让步档；0=torch 默认）")
    ap.add_argument("--query-field", default="q_used", choices=["q_used", "query"],
                    help="CE 查询文本字段（默认 q_used，与实验室特征一致）")
    args = ap.parse_args()

    threads = int(args.threads)
    if threads > 0:
        torch.set_num_threads(threads)
    threads_used = torch.get_num_threads()

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

    # ── 模型加载（一次，fp32 CPU）──
    model_dir = resolve_model_dir(args.model)
    if not model_dir.is_dir():
        log(f"[FAIL] 模型目录不存在：{model_dir}")
        return 2
    t0 = time.time()
    try:
        ce = TorchCrossEncoder(model_dir, args.max_length)
    except Exception as exc:  # noqa: BLE001
        log(f"[FAIL] 交叉编码器加载失败：{type(exc).__name__}: {exc}")
        return 2
    batch_size = int(args.batch_size)
    log(f"[CE] {model_dir.name} (torch {torch.__version__} cpu fp32) "
        f"加载 {time.time()-t0:.1f}s｜threads={threads_used}｜"
        f"batch={batch_size}｜max_length={args.max_length}")

    # ── 库块文本（只读，零网关）──
    kb = P.load_kb(get_settings())
    chunks = kb.retriever.chunks
    log(f"[KB] 块={len(chunks)}（只读，纯 chunk.text 口径：不含篇名/章名）")

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

    # ── 确定性复检：首题同批组成原样重打两遍，max abs diff < 1e-6 ──
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
    out_path = (Path(args.out) if args.out else
                ROOT / "data" / "compendium_rag" / "reports"
                / f"ce_v2_{model_dir.name}_{collect_path.stem}.json")
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "_meta": {
            "kind": "ce_v2_score",
            "model": model_dir.name,
            "model_dir": str(model_dir),
            "precision": "fp32",
            "backend": f"torch {torch.__version__} (cpu)",
            "torch_threads": threads_used,
            "sigmoid": "score = sigmoid(原始 logit)，bge-reranker 输出为未归一化 logit",
            "ce_input": (f"纯 chunk.text（空白折叠+截{MAX_CHARS}字符"
                         f"+截{args.max_length}token），不含篇名/章名"),
            "query_field": args.query_field,
            "pool": pool,
            "collect_top_k": top_k,
            "batch_size": batch_size,
            "max_length": int(args.max_length),
            "n_questions": len(scores),
            "n_pairs": n_pairs,
            "n_missing_chunks": n_missing,
            "total_seconds": round(total_seconds, 2),
            "pairs_per_sec": round(n_pairs / total_seconds, 2) if total_seconds else 0.0,
            "determinism_check": {
                "method": "第一题同批组成重打一遍，比较 logit（torch fp32 CPU）",
                "max_abs_diff": det_diff,
                "tolerance": DET_TOL,
                "pass": det_ok,
            },
            "source_collect": str(collect_path),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "note": "torch fp32 CPU 版 CE 打分桥；输出契约与 _ce_base_score.py 一致"
                    "（键=证据名次 1 基字符串，值=sigmoid(logit)）；"
                    "按题内分批保证确定性复检与首遍批组成一致",
        },
        **scores,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    log(f"[out] → {out_path}  ({out_path.stat().st_size / 1024:.0f} KB, "
        f"{n_pairs} pairs, {n_pairs / max(total_seconds, 1e-9):.1f} pairs/s)")

    eta = ETA_PAIRS / (n_pairs / max(total_seconds, 1e-9))
    log(f"[eta] 按 {ETA_PAIRS} 对（300题×30池）估算 ≈ {eta / 60:.1f} 分钟")
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
