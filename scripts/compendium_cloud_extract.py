# -*- coding: utf-8 -*-
"""Compendium 正典块的云端图谱抽取（补齐 plot_cache，使验收 R4/R10 转绿）。

为什么需要它
    新增的 compendium 正典块（5 226 块）没有抽取缓存，导致：
      - 验收 R4「语料切块合规」：缓存缺失 5 206
      - 验收 R10「抽取覆盖率」：empty 与 NOOP 差集 5 206
    补齐缓存后 R4/R10 即转绿，R11/R12 覆盖率亦上升。

为什么另写一个而不是直接用 ``cloud_extract.py --dump/--apply``
    那两个子命令是**按批号切片**的，会连带重抽该批内**已有缓存**的块，并用新结果
    **覆盖**它们——同一段文本两次抽取结果未必一致（LLM 非确定性），会平白改变
    既有图谱。本脚本只取**当前无缓存的**块，且**只写缺失的 hash**，
    绝不触碰任何既有缓存（与项目 P6 幂等、P1 先备份的原则一致）。

校验口径
    直接复用 ``cloud_extract._clean_one``：实体噪声/打捞、类型白名单回落、
    关系受控词表归一、端点越界、自环、置信度钳制——与既有 8 880 条缓存
    **同一套清洗逻辑**，不另立标准。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/compendium_cloud_extract.py --pilot
    .venv/Scripts/python.exe -X utf8 scripts/compendium_cloud_extract.py --limit 200
    .venv/Scripts/python.exe -X utf8 scripts/compendium_cloud_extract.py          # 全量
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
import cloud_extract as CE  # noqa: E402

CFG = get_settings()
CORPUS = Path(CFG.plot_corpus_dir) / "plot_corpus_wu_ming_zhe.json"
CACHE = Path(CFG.plot_cache_dir) / "wu_ming_zhe"
AUDIT_DIR = Path(CFG.plot_cache_dir).parent / "_audit"
CHARACTER = "wu_ming_zhe"

# 批量抽取的**串味**问题（实测，必须记录）
#   初版每批 10 块，速度尚可，但审计发现 602 块带 ``hallucinated_entity``：
#   逐条复算后 88% 是「该名字出现在**同批的其他块**里」——模型把兄弟块的实体
#   挂到了本块上。这违反「src/dst 必须出现在本块」的正典约束（清洗注意事项 C2），
#   且 R5 要求 hallucinated_entity == 0。
#   修复：``--repair`` 以 batch=1 单块重抽这些块（--workers 提供吞吐）。
BATCH_NOTE = "batch=1 单块抽取：消除跨块实体串味（见模块头 §批量串味）"

SYSTEM = """你是《重返未来：1999》剧情图谱的抽取器。对给定的每个文本块抽取实体与关系，\
**每个输入块输出一行 JSON**，顺序与输入一致，且必须原样带回该块的 hash。
只输出 JSONL（每行一个对象），不要任何解释、不要代码围栏。"""


def build_user(types: tuple[str, ...], part: list[dict]) -> str:
    lines = list(CE._spec_section(types))
    lines += ["## chunks", ""]
    for c in part:
        lines += [
            f"### hash=`{c['hash']}`",
            "",
            f"- lang：`{c.get('lang')}`｜doc：`{c.get('doc_id')}`",
            "",
            "```text",
            str(c.get("text") or "").strip(),
            "```",
            "",
        ]
    return "\n".join(lines)


def call(client: httpx.Client, types: tuple[str, ...], part: list[dict],
         *, retries: int = 4) -> str:
    """调用云端模型抽取一批块。

    429（限流）/ 5xx / 超时**必须重试**——实测 4 并发跑到尾声时网关开始限流，
    一次没重试就白丢 49 批（490 块）。指数退避即可稳定收敛。
    """
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = client.post(
                CFG.llm_base_url.rstrip("/") + "/chat/completions",
                headers={"Authorization": "Bearer " + (CFG.llm_api_key or "")},
                json={
                    "model": CFG.llm_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": build_user(types, part)},
                    ],
                    "temperature": 0,
                    # 推理模型：思维链会吃掉大部分 token，给小了正文会为空
                    "max_tokens": 32000,
                },
                timeout=900.0,
            )
            if r.status_code in (429, 500, 502, 503, 504):
                raise httpx.HTTPStatusError(
                    f"HTTP {r.status_code}", request=r.request, response=r)
            r.raise_for_status()
            return (r.json()["choices"][0]["message"].get("content") or "").strip()
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt >= retries:
                break
            time.sleep(min(60.0, 3.0 * (2 ** attempt)))
    raise last if last else RuntimeError("call failed")


def parse_rows(raw: str) -> list[dict]:
    """容错解析：剥围栏 → 逐行 json → 兜底抽所有 {...}。"""
    txt = raw.strip()
    if txt.startswith("```"):
        txt = txt.split("\n", 1)[1] if "\n" in txt else txt
        txt = txt.rsplit("```", 1)[0]
    rows: list[dict] = []
    for ln in txt.splitlines():
        s = ln.strip().rstrip(",")
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                rows.append(obj)
        except ValueError:
            continue
    if not rows:
        import re
        for m in re.finditer(r"\{.*?\}(?=\s*$|\s*\n)", txt, re.S):
            try:
                obj = json.loads(m.group(0))
                if isinstance(obj, dict):
                    rows.append(obj)
            except ValueError:
                continue
    return rows


def missing_chunks() -> list[dict]:
    have = {p.stem for p in CACHE.glob("*.json")} if CACHE.exists() else set()
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    return [c for c in data["chunks"] if c["hash"] not in have]


def chunks_by_hash(path: Path, only: set[str] | None = None) -> list[dict]:
    """从语料取出指定 hash 的块（--repair 用：强制重抽已存在但被判不合格的块）。"""
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    out = [c for c in data["chunks"] if only is None or c["hash"] in only]
    return out


def run(limit: int | None, batch_size: int, dry_run: bool, workers: int = 4,
        repair: bool = False) -> int:
    types = CE._load_type_whitelist(CHARACTER)
    if repair:
        # 修复模式：重抽「实体不在本块正文」的块。成因见 §批量串味说明。
        import audit_full_corpus as A
        rows = [json.loads(l) for l in (AUDIT_DIR / "full_issues.jsonl").read_text(
            encoding="utf-8").splitlines() if l.strip()]
        bad = {r["hash"] for r in rows if "hallucinated_entity" in r.get("flags", [])}
        # 只重抽**单块**抽取：批大小固定 1，从根上消除跨块串味
        batch_size = 1
        miss = chunks_by_hash(CORPUS, bad)
        print(f"[extract] 修复模式：重抽 {len(miss)} 块（单块抽取，batch=1）")
    else:
        miss = missing_chunks()
        print(f"[extract] 缺缓存块 {len(miss)}｜类型白名单 {len(types)} 类")
    if limit:
        miss = miss[:limit]
        print(f"[extract] --limit 生效，本轮只做 {len(miss)} 块")
    if not miss:
        print("[extract] 无可抽取块")
        return 0

    todo = [miss[i:i + batch_size] for i in range(0, len(miss), batch_size)]
    print(f"[extract] 批数 {len(todo)}（每批 {batch_size} 块）"
          f"｜并发 {workers}｜dry_run={dry_run}")
    if not dry_run:
        CACHE.mkdir(parents=True, exist_ok=True)

    agg = {k: 0 for k in (
        "ent_noise", "ent_rescued", "ent_empty", "ent_type_fallback",
        "rel_no_canon", "rel_endpoint", "rel_selfloop", "rel_conf")}
    lock = threading.Lock()
    state = {"written": 0, "empty": 0, "bad_hash": 0, "failed": 0, "done": 0}
    t_start = time.time()

    def work(part: list[dict]) -> None:
        """一个批次：调用 → 解析 → 校验 → 写缓存（只写本批新增，不覆盖他人）。"""
        allowed = {c["hash"] for c in part}
        try:
            rows = parse_rows(call(client, types, part))
        except Exception as e:  # noqa: BLE001
            with lock:
                state["failed"] += 1
            print(f"   [warn] 批次失败（{len(part)} 块将留待续跑）：{str(e)[:120]}")
            return
        local = {k: 0 for k in agg}
        w = e_ = bh = 0
        for item in rows:
            h, data, stat = CE._clean_one(item, allowed, types)
            for k, v in stat.items():
                local[k] += v
            if not h:
                bh += 1
                continue
            if not data["entities"] and not data["relations"]:
                e_ += 1
            if not dry_run:
                (CACHE / f"{h}.json").write_text(
                    json.dumps(data, ensure_ascii=False), encoding="utf-8")
            w += 1
        with lock:
            for k, v in local.items():
                agg[k] += v
            state["written"] += w
            state["empty"] += e_
            state["bad_hash"] += bh
            state["done"] += 1
            n, tot = state["done"], len(todo)
            if n % 10 == 0 or n == tot:
                el = time.time() - t_start
                rate = state["written"] / el if el else 0
                eta = (len(miss) - state["written"]) / rate / 60 if rate else 0
                print(f"   [{n}/{tot} 批] 累计 {state['written']}/{len(miss)} 块"
                      f"｜{rate:.2f} 块/秒｜ETA {eta:.0f} 分", flush=True)

    with httpx.Client() as client, ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, todo))

    written = state["written"]
    print(f"\n[extract] 写入 {written} 条缓存｜空块 {state['empty']}｜"
          f"hash 越界 {state['bad_hash']}｜调用失败 {state['failed']}")
    print(f"[extract] 丢弃：实体噪声 {agg['ent_noise']} / 打捞 {agg['ent_rescued']} / "
          f"空名 {agg['ent_empty']}｜类型回落 {agg['ent_type_fallback']}｜"
          f"关系 非受控 {agg['rel_no_canon']} / 端点越界 {agg['rel_endpoint']} / "
          f"自环 {agg['rel_selfloop']} / 置信度异常 {agg['rel_conf']}")
    print(f"[extract] 耗时 {(time.time()-t_start)/60:.1f} 分")
    if not dry_run:
        print(f"[extract] 剩余未覆盖 {len(missing_chunks())} 块")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="本轮最多抽取多少块")
    ap.add_argument("--batch-size", type=int, default=10, help="每次调用多少块")
    ap.add_argument("--workers", type=int, default=4, help="并发请求数")
    ap.add_argument("--repair", action="store_true",
                    help="重抽被判 hallucinated_entity 的块（batch=1 消除跨块串味）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", action="store_true", help="试跑：20 块")
    args = ap.parse_args()
    limit = 20 if args.pilot else args.limit
    return run(limit, args.batch_size, args.dry_run, args.workers, args.repair)


if __name__ == "__main__":
    sys.exit(main())
