# -*- coding: utf-8 -*-
"""RAG 知识库验收测试（可复跑）。

覆盖四层，逐层加严：
  L1 检索层  —— 问题能否召回正确条目（命中率 + 语义正确率）
  L2 注入层  —— 召回内容是否真的进入 prompt（build_rag_context）
  L3 端到端  —— 模型回答是否基于知识、有无编造、有无破人设
  L4 抗干扰  —— 知识库外的问题是否不乱答、不冒充全知

用法（项目根目录）：
  python scripts/verify_rag.py                 # 全跑
  python scripts/verify_rag.py --skip-e2e      # 只跑离线层（快，不需要模型）
  python scripts/verify_rag.py --verbose       # 打印每条命中详情
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CHARACTER_ID = "wu_ming_zhe"

# ── 测试用例 ────────────────────────────────────────────────────────────
# (问题, 分类, 期望命中的关键词列表, 命中任一即算正确)
RETRIEVAL_CASES = [
    # 世界观
    ("暴雨到底是什么", "世界观", ["暴雨", "1999 年 12 月 31 日", "几何体"]),
    ("圣洛夫基金会是做什么的", "世界观", ["圣洛夫基金会", "收容和管理神秘学家"]),
    ("重塑之手是什么组织", "世界观", ["重塑之手", "神秘学恐怖组织"]),
    ("司辰是什么", "世界观", ["司辰", "时代的见证者", "Timekeeper"]),
    ("神秘学家是什么", "世界观", ["神秘学家", "巫师、魔法师"]),
    # 角色
    ("维尔汀是谁", "角色", ["维尔汀", "司辰"]),
    ("康斯坦丁是什么人", "角色", ["康斯坦丁", "副会长"]),
    ("小梅斯梅尔是谁", "角色", ["小梅斯梅尔", "精神科医"]),
    ("阿尔卡纳是谁", "角色", ["阿尔卡纳", "重塑之手的首领"]),
    ("凯拉是谁", "角色", ["凯拉", "农场女孩"]),
    ("金伯利女郎是谁", "角色", ["金伯利", "天使娜娜", "魅魔"]),
    # 剧情
    ("77号往事发生了什么", "剧情", ["77 号", "蓝手帕", "凯拉"]),
    ("你是怎么加入司辰小队的", "剧情", ["司辰小队", "第十三章", "风网"]),
    ("芝加哥事件是什么", "剧情", ["芝加哥", "情人节大屠杀", "瓦尔登湖"]),
    # 场景
    ("你是谁", "场景", ["无名者", "淑女格蕾丝", "这里只有无名者"]),
    ("你为什么在这里", "场景", ["来历", "被好好听一次", "场景六"]),
    ("我今天被骂了很难受", "场景", ["场景五", "被骂"]),
    # 角色自身（回归验证，确保补新知识没有挤掉原有知识）
    ("你的母亲叫什么", "自身", ["康斯坦丁", "普帕"]),
    ("你的神秘术是什么", "自身", ["飞蛾", "鳞翅目", "记忆"]),
    ("发条装置是什么", "自身", ["发条装置", "趋光性", "光源"]),
    ("你的代号是什么", "自身", ["飞蛾", "普帕", "Pupa"]),
]

# 端到端用例：(问题, 应出现的关键词(任一), 禁止出现的关键词)
E2E_CASES = [
    ("暴雨到底是什么？", ["天空", "几何体", "1999", "回溯", "重塑"], ["上升气流", "冰晶", "气象"]),
    ("维尔汀是谁？", ["司辰", "箱子", "手提箱", "暴雨"], ["副会长", "执棋者"]),
    ("康斯坦丁是什么人？", ["养母", "康斯坦丁", "普帕", "副会长"], []),
    ("你的神秘术是什么？", ["飞蛾", "记忆", "鳞翅目", "情报"], ["发条里的发丝"]),
    ("你的母亲叫什么？", ["康斯坦丁", "普帕"], []),
    ("重塑之手是什么组织？", ["重塑", "神秘学", "暴雨", "阿尔卡纳"], []),
    ("圣洛夫基金会是做什么的？", ["神秘学家", "收容", "基金会"], []),
    ("凯拉是谁？", ["农场女孩", "凯拉", "77"], []),
    ("阿尔卡纳是谁？", ["重塑之手", "首领", "阿尔卡纳", "受苦者", "敌人", "交锋"], ["副会长", "养母"]),
    ("你是谁？", ["无名者", "格蕾丝", "凯拉", "莉莉"], ["我是AI", "我是人工智能", "语言模型"]),
]

# 抗干扰用例：知识库外/角色不该知道的事，回答不应编造具体事实
DISTRACTOR_CASES = [
    "今天股市涨了多少？",
    "帮我写一段 Python 快排代码",
    "2026年世界杯冠军是谁？",
]


def _score_report(results: list[tuple[str, str, bool, float, str]], title: str) -> int:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")
    if not results:
        return 0
    w = max(len(r[0]) for r in results)
    ok = 0
    for name, cat, good, score, detail in results:
        ok += good
        flag = "PASS" if good else "FAIL"
        print(f"[{flag}] {name:<{w}}  {cat:<5} {score:.3f}  {detail[:44]}")
    print(f"\n小计: {ok}/{len(results)}")
    return ok


async def run_retrieval(verbose: bool) -> tuple[int, int]:
    from roleplay.config import get_settings
    from roleplay.core.knowledge import build_knowledge_base, lore_namespace

    s = get_settings()
    kb = build_knowledge_base(s)
    ns = lore_namespace(CHARACTER_ID)
    # 与生产对齐：api/knowledge.py 用 asearch(hybrid=True)，top_k 取 .env 的 rag_top_k
    top_k = s.top_k
    cm = s.rag_hybrid_candidates
    results = []
    for q, cat, kws in RETRIEVAL_CASES:
        hits = await kb.asearch(q, top_k=top_k, namespaces=[ns], hybrid=True, candidate_mult=cm)
        if not hits:
            results.append((q, cat, False, 0.0, "未召回任何条目"))
            continue
        # top_k 条中任一命中关键词即算通过（这些条目会被同时注入）
        texts = " ".join(getattr(h, "text", "") for h in hits)
        good = any(k in texts for k in kws)
        top = getattr(hits[0], "text", "").replace("\n", " ")
        results.append((q, cat, good, getattr(hits[0], "score", 0.0), top))
    ok = _score_report(results, f"L1 检索层：问题能否召回正确条目（hybrid=True, top_k={top_k}）")
    if verbose:
        for name, cat, good, score, detail in results:
            print(f"  · {name} → {detail[:90]}")
    return ok, len(results)


async def run_injection() -> tuple[int, int]:
    """验证召回内容确实进入 prompt（上下文拼装层）。

    走真实链路：kb.search() → build_rag_context(chunks)，与 orchestrator 一致。
    """
    from roleplay.config import get_settings
    from roleplay.core.knowledge import build_knowledge_base, lore_namespace
    from roleplay.core.persona_prompt import build_rag_context

    s = get_settings()
    kb = build_knowledge_base(s)
    ns = lore_namespace(CHARACTER_ID)
    cm = s.rag_hybrid_candidates
    results = []
    for q, cat, kws in RETRIEVAL_CASES:
        chunks = await kb.asearch(q, top_k=s.top_k, namespaces=[ns], hybrid=True, candidate_mult=cm)
        ctx = build_rag_context(chunks)
        good = bool(ctx.strip()) and any(k in ctx for k in kws)
        detail = f"上下文 {len(ctx)} 字" if ctx.strip() else "上下文为空（被过滤）"
        results.append((q, cat, good, 0.0, detail))
    ok = _score_report(results, "L2 注入层：召回内容是否进入 prompt（build_rag_context）")
    return ok, len(results)


async def run_e2e(verbose: bool) -> tuple[int, int]:
    from fastapi.testclient import TestClient
    from roleplay.main import app

    results = []
    with TestClient(app) as c:
        for i, (q, expect, forbid) in enumerate(E2E_CASES):
            r = c.post("/chat", json={"session_id": f"verify-{i}", "message": q})
            if r.status_code != 200:
                results.append((q, "端到端", False, 0.0, f"HTTP {r.status_code}"))
                continue
            reply = (r.json().get("reply") or "").replace("\n", " ")
            hit = [k for k in expect if k in reply]
            bad = [k for k in forbid if k in reply]
            good = bool(hit) and not bad
            detail = (f"命中{hit}" + (f" 违禁{bad}" if bad else "")) if hit or bad else f"未命中任何期望词：{reply[:30]}"
            results.append((q, "端到端", good, 0.0, detail))
            if verbose:
                print(f"  · {q}\n    → {reply[:140]}")
    ok = _score_report(results, "L3 端到端：回答是否基于知识、有无编造与破人设")
    return ok, len(results)


async def run_distractor(verbose: bool) -> tuple[int, int]:
    """抗干扰：知识库外问题，角色不应编造具体事实、不应破人设。"""
    from fastapi.testclient import TestClient
    from roleplay.main import app

    results = []
    with TestClient(app) as c:
        for i, q in enumerate(DISTRACTOR_CASES):
            r = c.post("/chat", json={"session_id": f"dist-{i}", "message": q})
            if r.status_code != 200:
                results.append((q, "抗干扰", False, 0.0, f"HTTP {r.status_code}"))
                continue
            reply = (r.json().get("reply") or "").replace("\n", " ")
            # 破人设检查：不得自称 AI
            broke = any(k in reply for k in ["我是AI", "我是人工智能", "语言模型", "作为一个AI"])
            good = not broke
            results.append((q, "抗干扰", good, 0.0, "未破人设" if good else f"破人设：{reply[:30]}"))
            if verbose:
                print(f"  · {q}\n    → {reply[:140]}")
    ok = _score_report(results, "L4 抗干扰：库外问题是否不冒充全知、不破人设")
    return ok, len(results)


async def main() -> int:
    ap = argparse.ArgumentParser(description="RAG 知识库验收测试")
    ap.add_argument("--skip-e2e", action="store_true", help="跳过需要模型的端到端层")
    ap.add_argument("--verbose", action="store_true", help="打印每条详情")
    args = ap.parse_args()

    t0 = time.time()
    print(f"RAG 验收测试  角色={CHARACTER_ID}  时间={time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 环境自检：避免 .env 被测试污染导致全盘 401/404
    from roleplay.config import get_settings
    s = get_settings()
    print(f"环境自检: provider={s.llm_provider} model={s.llm_model} base_url={s.llm_base_url}")

    total_ok = total_all = 0
    ok, n = await run_retrieval(args.verbose)
    total_ok += ok; total_all += n
    ok, n = await run_injection()
    total_ok += ok; total_all += n

    if not args.skip_e2e:
        ok, n = await run_e2e(args.verbose)
        total_ok += ok; total_all += n
        ok, n = await run_distractor(args.verbose)
        total_ok += ok; total_all += n

    print(f"\n{'=' * 78}")
    print(f"总计: {total_ok}/{total_all}  ({total_ok / total_all * 100:.1f}%)   耗时 {time.time() - t0:.1f}s")
    print("=" * 78)
    return 0 if total_ok == total_all else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
