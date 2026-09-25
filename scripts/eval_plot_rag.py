# -*- coding: utf-8 -*-
"""剧情 RAG（PlotGraph）离线检索评测台（非 pytest，直接跑真实图谱 + 300 题集）。

与 ``scripts/eval_rag_huiji.py``（14 题灰机标准）的分工：
  - 灰机 14 题：人工核对的标准答案，用于**正确性**回归（并集子串命中，宽松）；
  - 本脚本 300 题：``data/knowledge/_audit/rag_testset_300.json``，用于**可复现的检索指标**
    （严格通过率 / 块精度 / 答案块率 / oracle recall / MRR / 延迟 / 路径归因 / 负样本）。

关键设计（为什么指标要这么定）：
  1. **oracle 天花板**：题集的 evidence 组并不保证"存在单块覆盖全部组"的语料块
     （实测 27/300 题不存在）。这类题只能靠多块并集命中，因此除 ``strict_pass`` 外
     单独报 ``ceiling_pass``（只在天花板内的题上算），避免把"语料缺口"记到检索头上。
  2. **严格口径与灰机评测一致**：证据组内任一关键词出现在**返回块并集**里即算覆盖，
     全部组覆盖才算 PASS。口径一致才能与 13/14 的历史结论横向比较。
  3. **路径归因**：``via`` 只有 plot_graph / plot_lexical 两个值，无法区分"边证据路"
     与"种子提及路"。本脚本按 ``meta["path"]`` 归因，缺失时回落到结构推断，
     让"图谱结构到底有没有起作用"第一次可测。
  4. **负样本**：通用问句（天气/写诗/算术）必须**零注入**。这是"图内泛词实体当种子"
     这类精度缺陷唯一稳定的护栏。
  5. **可复现**：报告记录 argv、配置快照、数据文件 SHA256、抽样参数；
     同参数复跑逐位可比。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py                    # 全量 300 题
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --sample 60 --seed 7 # 分层抽样快跑
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --baseline data/knowledge/_audit/plot_rag_eval_report.json
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --check-targets     # 验收线自检
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --no-trace          # 跳过埋点轮（快跑）
  # M-12 消融（AC-1：同题集配对 + McNemar）：
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py \
      --ablate-flag plot_ppr_node_specificity --ablate-on true --ablate-off false \
      --ablate-reference data/knowledge/_audit/plot_rag_eval_report_r0.json \
      --out data/knowledge/_audit/ablation/d1_off.json --check-targets

M-12：报告新增四段（契约 §7.6.4 / 表 7.6.4-a / 7.6.4-b，字段名一字不改）
  - ``trace_agg``：六通道跨题瀑布（hit_rate / kept_in_final_avg / kept_rate / squeezed_avg）；
  - ``ablation``：消融模式下的配对比较（m/b/c/delta_pt/mcnemar_p/method/case_ids_flipped/
    cases_executed/cases_total/feature_flag/trace_schema），非消融运行**显式 null**；
  - ``diff_vs_baseline``：逐题 diff，数据源统一取 ``ablation.case_ids_flipped``（不另建口径）；
  - ``bucket_attribution``：按架构 §4e 五桶归因（规则显式落盘，未命中进 unattributed）。

口径纪律（§7.6.6 阴性证据通则）——每个"零值/无变化"读数必须与其**执行计数**同段输出：
  ``squeezed_total`` ↔ ``graph_hit_total``｜``kept_rate`` 分母 0 → ``null``（不是 0）｜
  ``ablation.delta_pt≈0`` ↔ ``cases_executed``｜``m == 0`` → ``mcnemar_p = null``（不给 1.0 假值）｜
  ``fallback_counts`` 全 0 ↔ ``cases`` + ``total_ms``。
埋点轮**不计延迟**：p95 一律取无埋点首轮 —— 否则 A1 的 ≤100ms 增量判据会被评测自身的
开销污染（首轮与埋点轮的逐题判定还互为"埋点不改结果"的不变量检验）。

退出码：0 正常（或与基线相比未回退）｜1 环境/数据缺失｜2 缺少必要的基线｜3 相对基线回退｜4 验收线未达标
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from math import comb, erfc, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_corpus import chunk_hash, detect_lang  # noqa: E402
from roleplay.core.knowledge.retrieval_trace import (  # noqa: E402
    ABLATION_SCHEMA,
    CHANNEL_ORDER,
    PATH_TO_CHANNEL,
)

DEFAULT_CHARACTER = "wu_ming_zhe"
TESTSET_PATH = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_eval_report.json"
# 证据组 override 清单（2026-09-16 逐题复核产出）：
#   题集的 evidence 里混有「同场景共现」的冗余辅助组（章节名/载具/共现角色），
#   严格「全组覆盖」口径下这些题无论检索多好都必然 FAIL（实例：R003「海盗船上的
#   歌手」，辅助组 Sotheby 来自船上点唱机歌名《Please Please Sotheby》）。
#   本文件不改题集，只提供第二口径「主组覆盖」。缺失则主组口径 == 全组口径。
OVERRIDES_PATH = ROOT / "data" / "knowledge" / "_audit" / "evidence_overrides.json"
EVIDENCE_OVERRIDES: dict[str, dict] = {}

# ── 验收线（A1/A5 来自审计报告 §2；A2–A4 是相对基线的增量，见 --baseline）────────
TARGET_LATENCY_P95_MS = 300.0  # 历史目标线：**仅用于消歧与打印，不作合入判据**
# 唯一延迟合入判据（Spec AC-5 / 架构 §1.4.1 延迟三口径）：
#   ① 基线事实 = 现状 p95 实测值（不是允许上限）；
#   ② 合入判据 = 新增在线组件 p95 **增量 ≤ 100ms**（相对**同条件**基线）；
#   ③ 历史 300ms 线：**不作判据**。三口径不可混用（跨轮绝对差比较已被坑过：
#      同一版本两次测得 487ms vs 682ms，受 OS 文件缓存影响）。
TARGET_LATENCY_INCREMENT_MS = 100.0
TARGET_NEGATIVE_INJECTION = 0

# ── M-12：eval_run_complete 事件（架构 §7.6.4 顶层表）────────────────────────
EVAL_EVENT = "eval_run_complete"
# margin 直方图**桶边界显式落盘**（§7.6.4-a 明文要求）：看板不得自行造桶，否则
# "阈值标定证据"会随看板实现漂移。右端开区间，末桶含上界（>=0.50）。
MARGIN_BUCKET_EDGES = [0.0, 0.02, 0.05, 0.10, 0.20, 0.35, 0.50]
# 消融开关 → 执行计数键（§7.6.6 的「是否被测到」）：flag 名与 activation 键的
# 唯一映射表。新增 P0 开关时必须在此登记，否则 `cases_executed` 永远为 0——
# 而 0 会被误读成"功能无效"，正是通则禁止的误读。
ACTIVATION_KEYS = {
    "plot_weak_exempt_sources": "c4_candidates",       # P0-1 / C4
    "plot_ppr_node_specificity": "d1_seeds_downweighted",  # P0-4 / D1
    "plot_semantic_rerank_enabled": "b3_reranked",     # P0-2 / B3（待实现）
    "plot_semantic_zh_enabled": "a1_zh_hits",          # P1-1 / A1（待实现）
    "plot_trace_enabled": None,                        # P0-5 / F8a：埋点不改检索结果
}

# ── 负样本：通用问句 / 元问题 / 与剧情无关的请求，必须零注入 ────────────────────
# 覆盖三类失效模式：① 图内泛词实体（天气/故事）；② 纯闲聊；③ 系统元问题。
# ── 负样本集（R3 护栏 / AC-2 证据）：扩充至 50+ 并**分类** ──────────────────────
# 为什么必须扩充到 50+（Spec §4e 桶 2 的残余项，PRD §11 R2）：
#   B3 的安全间隔阈值 `plot_semantic_rerank_min`（默认 0.5）要**基于 margin 分布标定**，
#   而 10 条样本量不足以支撑阈值标定——样本太少的阈值不是标定，是拍脑袋。
# 为什么要分类：负样本失守时，"是哪一类问法漏进来的"决定了修法完全不同
#   （泛词实体 -> 扩泛词表；跨域专名 -> 查别名表误收；元问题 -> 加前缀拦截）。
#   旧版只有一串平铺问句，失守后无法定位成因。
# 判据不变：**任何一条注入 > 0 块即 R3 失守**（不是"平均注入少"）。
NEGATIVE_CASES = [
    # ① 世界常识泛词：图内存在"天气/经济/故事"这类与作品同名词条，旧实现靠它们蹭进上下文
    ("泛词实体", "今天天气怎么样"),
    ("泛词实体", "明天的天气预报是什么"),
    ("泛词实体", "最近经济形势如何"),
    ("泛词实体", "股市今天涨了吗"),
    ("泛词实体", "给我讲个故事"),
    ("泛词实体", "这个故事讲了什么"),
    ("泛词实体", "时间是什么"),
    ("泛词实体", "介绍几个历史事件"),
    ("泛词实体", "什么是哲学"),
    ("泛词实体", "解释一下相对论"),
    # ② 纯闲聊 / 问候（无任何实体指代）
    ("闲聊", "你好呀，在吗"),
    ("闲聊", "在干嘛呢"),
    ("闲聊", "陪我聊聊天吧"),
    ("闲聊", "我今天心情不太好"),
    ("闲聊", "你觉得我这个人怎么样"),
    ("闲聊", "晚安，早点休息"),
    ("闲聊", "谢谢你"),
    ("闲聊", "哈哈哈"),
    # ③ 工具型请求：算术 / 编程 / 写作
    ("工具型", "1+1 等于几"),
    ("工具型", "123 乘以 456 是多少"),
    ("工具型", "用 Python 写一个快速排序"),
    ("工具型", "帮我写一个 SQL 查询"),
    ("工具型", "帮我把这段话翻译成英文"),
    ("工具型", "帮我写一首关于春天的诗"),
    ("工具型", "总结一下这篇文章的要点"),
    ("工具型", "正则表达式怎么匹配邮箱"),
    ("工具型", "Excel 怎么做透视表"),
    # ④ 生活服务 / 日程
    ("生活服务", "推荐几家附近的餐厅"),
    ("生活服务", "明天几点开会"),
    ("生活服务", "这个软件怎么安装"),
    ("生活服务", "帮我订一张去北京的机票"),
    ("生活服务", "附近有充电桩吗"),
    ("生活服务", "快递什么时候到"),
    ("生活服务", "外卖有什么优惠"),
    # ⑤ 元问题：问 AI 自身，与被扮演角色无关
    ("元问题", "你是谁"),
    ("元问题", "你是什么模型"),
    ("元问题", "你和 ChatGPT 有什么区别"),
    ("元问题", "你有意识吗"),
    ("元问题", "你能帮我做什么"),
    # ⑥ 跨域专名：**别的作品/领域**的专有名词（最容易误链的一类——
    #    它们形状像作品内实体，若别名表或泛词表误收，就会被当种子）
    ("跨域专名", "哈利波特是谁"),
    ("跨域专名", "红楼梦的作者是谁"),
    ("跨域专名", "复仇者联盟有几部电影"),
    ("跨域专名", "苹果公司的 CEO 是谁"),
    ("跨域专名", "巴黎在哪个国家"),
    ("跨域专名", "泰坦尼克号是哪一年沉没的"),
    # ⑦ 英文闲聊（验证跨语言语义层不会把英文离题句拉进来）
    ("英文闲聊", "what is the weather like today"),
    ("英文闲聊", "tell me a joke"),
    ("英文闲聊", "how do i install this software"),
    ("英文闲聊", "who is the president of the united states"),
    # ⑧ 退化输入：空 / 纯符号 / 极短（边界值，Spec §10 边界条件）
    ("退化输入", "。。。"),
    ("退化输入", "？？？"),
    ("退化输入", "asdfghjkl"),
    ("退化输入", "1234567890"),
]
NEGATIVE_QUERIES = [q for _cat, q in NEGATIVE_CASES]

# 已知残余（有界技术债）：这 5 条离题问句**当前仍会注入**，且已被单测登记在案
# （tests/test_plotrag_optimization.py::TestP3SeedGate.KNOWN_RESIDUAL_NEGATIVES）。
# 为什么不是"改松判据"：它们的种子（苹果 度2 / Paris 度31 / President 度6 /
# our nation / 泰坦尼克号）都是**作品内真实实体**，仅凭结构判据无法与"离题引用"
# 区分——必须靠 B3（reranker 安全间隔）的语义相关度。两条被数据否决的粗暴修法：
#   ① 要求"至少一个锚定种子" → 短路 111/300 正样本（别名桥缺失主战场）；
#   ② 孤立实体（度 0）不做种子 → 短路 23/288（真实体只是零度节点，提及块仍有价值）。
# A5 验收线据此**如实判为未达标**，并把残余单列——不得静默当作通过。
KNOWN_RESIDUAL_NEGATIVES = {
    "哈利波特是谁",
    "苹果公司的 CEO 是谁",
    "巴黎在哪个国家",
    "泰坦尼克号是哪一年沉没的",
    "who is the president of the united states",
}

# 与基线对比时的回退判定：这些指标「越大越好」
HIGHER_IS_BETTER = ("strict_pass", "chunk_precision", "answer_chunk_rate", "mrr")
# 这些指标「越小越好」
LOWER_IS_BETTER = ("latency_p95_ms", "negative_injection_total")
# 回退容忍（比率类指标允许 0.005 的浮点/抽样抖动）
TOLERANCE = 0.005


def sha256_head(path: Path, n: int = 16) -> str:
    """文件指纹前 n 位（数据资产可复现标识；缺失返回空串）。"""
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        return h.hexdigest()[:n]
    except OSError:
        return ""


def percentile(values: list[float], q: float) -> float:
    """线性插值分位数（不引第三方依赖；values 需非空）。"""
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    frac = pos - lo
    return float(xs[lo] * (1 - frac) + xs[hi] * frac)


def stratified_sample(items: list[dict], n: int, seed: int) -> list[dict]:
    """按 ``dims.type`` 比例分层抽样（确定性：同 n/seed 必得同一子集）。"""
    if n <= 0 or n >= len(items):
        return list(items)
    pools: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        pools[str(it.get("dims", {}).get("type") or "unknown")].append(it)
    rng = random.Random(seed)
    picked: list[dict] = []
    for key in sorted(pools):
        pool = sorted(pools[key], key=lambda x: x.get("id", ""))
        want = max(1, round(n * len(pool) / len(items)))
        picked.extend(rng.sample(pool, min(want, len(pool))))
    picked = picked[:n] if len(picked) > n else picked
    picked.sort(key=lambda x: x.get("id", ""))
    return picked


def load_testset(path: Path | None = None) -> list[dict]:
    """读题库。``path`` 可指定别的题集版本（默认现行基准 TESTSET_PATH）。

    为什么需要可指定（2026-09-16）：修正题集生成器的 SCENARIO_ADD 误标后，
    要拿**新生成的干净题集**与现行基准做对照评测——基准不能被覆盖，故两条路并行。
    """
    p = path or TESTSET_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit(f"[FAIL] 题集为空或结构非法：{p}")
    return [it for it in data if isinstance(it, dict) and it.get("q") and it.get("evidence")]


def build_oracle(corpus, items: list[dict]) -> dict[str, dict]:
    """每题预计算 oracle 命中块（单块覆盖全部证据组 = full，覆盖任一 = any）。

    返回 ``{item_id: {"full": set[hash], "any": set[hash], "ceiling": bool}}``。
    语料 8358 块 × 300 题实测约 2s，一次性成本。
    """
    out: dict[str, dict] = {}
    for it in items:
        groups = it["evidence"]
        full: set[str] = set()
        anyhit: set[str] = set()
        for chunk in corpus.chunks:
            text = chunk.text
            hits = [any(kw in text for kw in g) for g in groups]
            if all(hits):
                full.add(chunk.hash)
            if any(hits):
                anyhit.add(chunk.hash)
        out[str(it.get("id"))] = {
            "full": full,
            "any": anyhit,
            "ceiling": bool(full),  # 天花板：存在可单块作答的语料块
        }
    return out


def infer_path(meta: dict) -> str:
    """区块路径归因：优先新字段 ``path``，缺失时按旧字段结构推断（兼容优化前代码）。"""
    path = str(meta.get("path") or "")
    if path:
        return path
    if str(meta.get("via") or "") == "plot_lexical":
        return "lexical"
    if meta.get("seed_mention"):
        return "mention"
    if meta.get("edge"):
        return "edge"
    return "unknown"


def load_evidence_overrides(path: Path | None = None) -> int:
    """加载证据组 override 清单（不改题集，仅供「主组口径」判定）。"""
    global EVIDENCE_OVERRIDES
    p = path or OVERRIDES_PATH
    if not p.is_file():
        EVIDENCE_OVERRIDES = {}
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        EVIDENCE_OVERRIDES = {}
        return 0
    EVIDENCE_OVERRIDES = dict(data.get("overrides") or {})
    return len(EVIDENCE_OVERRIDES)


def _primary_pass(item: dict, missing: list[int]) -> bool:
    """主组口径：只要求 override 指定的 keep_groups 被覆盖（无 override 时等同全组）。"""
    qid = str(item.get("id") or "")
    ov = EVIDENCE_OVERRIDES.get(qid)
    if not ov:
        return not missing
    ng = len(item.get("evidence") or [])
    missing_set = set(missing)
    keeps = [g for g in (ov.get("keep_groups") or []) if 0 <= g < ng]
    if not keeps:
        return not missing
    return all(g not in missing_set for g in keeps)


def evaluate_case(retr, item: dict, oracle: dict, top: int, lexical_fallback: int,
                  inject_max_chars: int = 0, chunks_transform=None) -> dict:
    """单题检索 + 打分（严格口径与灰机评测一致：并集子串命中）。

    ``inject_max_chars`` > 0 时额外算**注入口径**：把检索结果按
    ``persona_prompt.build_plot_context`` 的真实装配规则（按名次填、超预算即停）
    压成提示词块，再在该文本上判证据覆盖。

    为什么必须单列这一口径（M7 审计发现）：``strict_pass`` 统计的是**返回块并集**，
    而产品真正交给模型的是 ``plot_context_max_chars``（默认 1000 字符）以内的文本。
    语料块约 600 字/块 ⇒ 实际只装得下 1–2 块，两者口径相差甚远。
    只看 strict_pass 会把"多返回块"当成质量提升（实测 top 3→8 能把 strict 从
    47% 拉到 57%，但注入文本一个字都没变）——那是**指标灌水**，不是产品变好。
    """
    t0 = time.perf_counter()
    chunks = retr.retrieve(item["q"], top_chunks=top, lexical_fallback=lexical_fallback)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    # 可选重排钩子（2026-09-16 新增，供 reranker 实验用）：默认 None ⇒ 与改动前逐位一致。
    # 之所以做成钩子而不是让实验脚本自造判定：实验脚本一旦自建 strict/inject 口径，
    # 基准就与主评测对不上（实测 ab 脚本 strict 72.67% vs 主评测 67.67%），结论不可比。
    if chunks_transform is not None:
        chunks = chunks_transform(item["q"], chunks)

    groups = item["evidence"]
    union = "\n".join(c.text for c in chunks)
    covered = [any(kw in union for kw in g) for g in groups]
    missing = [i for i, ok in enumerate(covered) if not ok]

    inject_missing: list[int] = []
    injected_chars = 0
    if inject_max_chars > 0:
        try:
            from roleplay.core.persona_prompt import build_plot_context  # noqa: PLC0415
            injected = build_plot_context(chunks, max_chars=inject_max_chars)
        except Exception:  # pragma: no cover - 装配失败不应让评测崩掉
            injected = ""
        injected_chars = len(injected)
        inject_missing = [i for i, g in enumerate(groups) if not any(kw in injected for kw in g)]

    # RetrievedChunk 不带 hash 字段（只有 text/score/metadata）：用语料同一套文本指纹
    # 还原，保证与 oracle 命中集、图谱 evidence.hash 三处同口径。
    hashes = [chunk_hash(c.text) for c in chunks]
    full = oracle["full"]
    anyhit = oracle["any"]
    n_full = sum(1 for h in hashes if h in full)
    n_rel = sum(1 for h in hashes if h in anyhit)
    total = len(hashes)

    # MRR：第一个「全证据组覆盖块」的名次（1 基）；无则 0
    mrr = 0.0
    for rank, h in enumerate(hashes, start=1):
        if h in full:
            mrr = 1.0 / rank
            break
    # oracle recall@k：返回里命中的 full 块占「可命中上限」的比例
    denom = min(top, len(full)) if full else 0
    recall = (min(n_full, denom) / denom) if denom else 0.0

    paths = Counter(infer_path(c.metadata or {}) for c in chunks)
    # ── 抗灌水口径（2026-09-17 新增）──────────────────────────────────────
    # 为什么必须单列：``strict_pass`` 判的是「返回块**并集的证据词覆盖**」，
    # 于是往结果里追加一个「实体名列表」合成块就能**无条件**满足判定。
    # 实测（T5 摘要节点）：把与题目毫无关系的全局 top-40 名表追加进结果，
    # strict 195→214（+19），而 inject **完全不动**——纯灌水。
    # 本口径只统计**检索通道返回的真实语料块**（排除 metadata.synthetic=True
    # 的注入块），用来区分「检索真改善」与「往上下文里塞名词表」。
    # 约定：任何实验/生产注入的合成块必须打 ``metadata["synthetic"] = True``。
    real_chunks = [c for c in chunks if not (c.metadata or {}).get("synthetic")]
    real_union = "\n".join(c.text for c in real_chunks)
    covered_real = [any(kw in real_union for kw in g) for g in groups]
    missing_real = [i for i, ok in enumerate(covered_real) if not ok]
    # 桶 5（跨语言底座）的判据：中文查询 vs 英文 ASR 正文不可词法比对。
    # 逐题记"返回块里 CJK 占比"，使该桶可**由数据**判定，而不是靠题目元数据自报。
    try:
        zh_ratio = (
            sum(1 for c in chunks if detect_lang(c.text) == "zh") / len(chunks)
            if chunks else 0.0
        )
    except Exception:  # pragma: no cover - 语言判定失败不影响主指标
        zh_ratio = 0.0
    return {
        "id": item.get("id"),
        "q": item["q"],
        "dims": item.get("dims") or {},
        "strict_pass": not missing,
        # 抗灌水口径：只算真实语料块（排除合成注入块）。无合成块时与 strict_pass 相等。
        "strict_pass_retrieved": not missing_real,
        "retrieved_covered": f"{len(groups) - len(missing_real)}/{len(groups)}",
        "covered": f"{len(groups) - len(missing)}/{len(groups)}",
        "missing_groups": missing,
        # 主组口径（证据组 override）：只要求 override 指定的 keep_groups 被覆盖。
        # 无 override 的题与 strict_pass 完全一致。用于与「全组口径」并列报告，
        # 把「题集标注缺陷导致的假失败」与「真实检索失败」区分开。
        "primary_pass": _primary_pass(item, missing),
        "inject_pass": (not inject_missing) if inject_max_chars > 0 else None,
        "inject_missing": inject_missing,
        "injected_chars": injected_chars,
        "ceiling": oracle["ceiling"],
        "n_chunks": total,
        "n_relevant": n_rel,
        "n_full_match": n_full,
        "recall": round(recall, 4),
        "mrr": round(mrr, 4),
        "paths": dict(paths),
        "zh_ratio": round(zh_ratio, 3),
        "latency_ms": round(elapsed_ms, 2),
        # P0 消融执行计数（§7.6.6）：本轮各功能**实际起作用**的次数。
        # 随 items 落盘，使任何一轮报告都能直接充当消融的 `cases_executed` 来源，
        # 不必重跑参照轮（R0 只跑一次的内存/时间约束）。
        "activation": dict(getattr(retr, "last_activation", None) or {}),
    }


def aggregate(rows: list[dict]) -> dict:
    """总体指标（strict_pass 等为比率，latency 为毫秒分位）。"""
    n = max(1, len(rows))
    ceiling_rows = [r for r in rows if r["ceiling"]]
    lat = [r["latency_ms"] for r in rows]
    n_chunks = sum(r["n_chunks"] for r in rows)
    paths: Counter = Counter()
    for r in rows:
        paths.update(r["paths"])
    return {
        "cases": len(rows),
        "ceiling_cases": len(ceiling_rows),
        "strict_pass": round(sum(1 for r in rows if r["strict_pass"]) / n, 4),
        "strict_pass_n": sum(1 for r in rows if r["strict_pass"]),
        # 抗灌水口径（只算真实语料块）。与 strict_pass 的差 = 合成块贡献的"虚假通过"。
        "strict_pass_retrieved": round(
            sum(1 for r in rows if r.get("strict_pass_retrieved", r["strict_pass"])) / n, 4
        ),
        "strict_pass_retrieved_n": sum(
            1 for r in rows if r.get("strict_pass_retrieved", r["strict_pass"])
        ),
        # 主组口径（同一批检索结果，只换「要求覆盖哪些证据组」的判定）。
        # 两口径并列报告，用于把题集标注缺陷导致的假失败与真实检索失败分开。
        "primary_pass": round(
            sum(1 for r in rows if r.get("primary_pass", r["strict_pass"])) / n, 4
        ),
        "primary_pass_n": sum(1 for r in rows if r.get("primary_pass", r["strict_pass"])),
        "ceiling_pass": round(
            sum(1 for r in ceiling_rows if r["strict_pass"]) / max(1, len(ceiling_rows)), 4
        ),
        "chunk_precision": round(sum(r["n_relevant"] for r in rows) / max(1, n_chunks), 4),
        "answer_chunk_rate": round(sum(r["n_full_match"] for r in rows) / max(1, n_chunks), 4),
        "mrr": round(sum(r["mrr"] for r in rows) / n, 4),
        "recall": round(statistics.mean([r["recall"] for r in rows]) if rows else 0.0, 4),
        "avg_returned_chunks": round(n_chunks / n, 2),
        "latency_p50_ms": round(percentile(lat, 0.50), 1),
        "latency_p90_ms": round(percentile(lat, 0.90), 1),
        "latency_p95_ms": round(percentile(lat, 0.95), 1),
        "latency_max_ms": round(max(lat) if lat else 0.0, 1),
        "path_counts": dict(paths),
        "empty_rate": round(sum(1 for r in rows if r["n_chunks"] == 0) / n, 4),
        # 注入口径（与产品一致的那一半）：None 表示本次未启用
        "inject_pass": (
            round(sum(1 for r in rows if r.get("inject_pass")) / n, 4)
            if rows and rows[0].get("inject_pass") is not None else None
        ),
        "inject_pass_n": (
            sum(1 for r in rows if r.get("inject_pass"))
            if rows and rows[0].get("inject_pass") is not None else None
        ),
        "injected_chars_avg": (
            round(sum(r.get("injected_chars") or 0 for r in rows) / n, 1)
            if rows and rows[0].get("inject_pass") is not None else None
        ),
    }


def by_dimension(rows: list[dict], dim: str) -> dict:
    """按 ``dims`` 某一维度分层聚合（定位"哪类题在拖后腿"）。"""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        buckets[str((r.get("dims") or {}).get(dim) or "unknown")].append(r)
    out: dict[str, dict] = {}
    for key in sorted(buckets):
        sub = buckets[key]
        out[key] = {
            "cases": len(sub),
            "strict_pass": round(sum(1 for r in sub if r["strict_pass"]) / len(sub), 4),
            "chunk_precision": round(
                sum(r["n_relevant"] for r in sub) / max(1, sum(r["n_chunks"] for r in sub)), 4
            ),
            "latency_p50_ms": round(percentile([r["latency_ms"] for r in sub], 0.5), 1),
        }
    return out


def evaluate_negatives(retr, top: int, lexical_fallback: int) -> dict:
    """负样本：通用问句必须零注入。注入即列出块首句，便于定位是哪类泛词种子。

    判据是**逐条零注入**（`injected == 0`），不是"平均注入少"——护栏只有 0 与 1 之分。
    按类聚合 `by_category`，失守时直接看出是哪一类问法漏进来的（修法因类而异）。
    """
    rows = []
    by_cat: dict[str, dict] = {}
    _t0_all = time.perf_counter()
    for cat, q in NEGATIVE_CASES:
        t0 = time.perf_counter()
        chunks = retr.retrieve(q, top_chunks=top, lexical_fallback=lexical_fallback)
        ms = (time.perf_counter() - t0) * 1000.0
        rows.append(
            {
                "q": q,
                "category": cat,
                "injected": len(chunks),
                "paths": dict(Counter(infer_path(c.metadata or {}) for c in chunks)),
                "samples": [c.text[:60] for c in chunks[:2]],
                "latency_ms": round(ms, 2),
            }
        )
        agg = by_cat.setdefault(cat, {"cases": 0, "injected": 0, "cases_with_injection": 0})
        agg["cases"] += 1
        agg["injected"] += len(chunks)
        agg["cases_with_injection"] += int(len(chunks) > 0)
    dirty = [r["q"] for r in rows if r["injected"] > 0]
    new_leaks = [q for q in dirty if q not in KNOWN_RESIDUAL_NEGATIVES]
    return {
        "cases": len(rows),
        "negative_injection_total": sum(r["injected"] for r in rows),
        "negative_clean": not dirty,
        # 失守清单：R3 的**证据**，直接列出题面（旧版只给一个总数，定位要自己翻 rows）
        "violations": dirty,
        # 已知残余（有界技术债，待 B3 修复）与**新增**泄漏必须分开报：
        # 混在一起会让"新增泄漏"看起来也是"早就知道的"，从而失去报警价值。
        "known_residual": [q for q in dirty if q in KNOWN_RESIDUAL_NEGATIVES],
        "new_leaks": new_leaks,
        "clear": not new_leaks,
        "by_category": by_cat,
        "elapsed_s": round(time.perf_counter() - _t0_all, 1),
        "rows": rows,
    }


def _safe_div(num: float, den: float) -> float | None:
    """分母 0 → ``None``（**不是** 0）。§7.6.6 硬条文的唯一实现点："""
    return round(num / den, 4) if den else None


def chan_of(agg: dict, name: str, key: str = "hit_total"):
    """取 ``trace_agg.channels[]`` 某通道的某个聚合键（缺失 → None，不静默填 0）。"""
    for c in agg.get("channels") or []:
        if c.get("channel") == name:
            return c.get(key)
    return None


def _lat(rec: dict, key: str = "total_ms") -> float:
    return float(((rec.get("latency") or {}).get(key)) or 0.0)


def _margin_histogram(margins: list[float], single: int, thresholds: Counter,
                      triggered: int, linked: int) -> dict:
    """``margin`` 直方图（桶边界**显式落盘**，看板不得自造桶）。"""
    edges = MARGIN_BUCKET_EDGES
    labels = [f"[{edges[i]:.2f},{edges[i + 1]:.2f})" for i in range(len(edges) - 1)]
    labels.append(f">={edges[-1]:.2f}")
    counts = {lb: 0 for lb in labels}
    for v in margins:
        for i in range(len(edges) - 1):
            if edges[i] <= v < edges[i + 1]:
                counts[labels[i]] += 1
                break
        else:
            counts[labels[-1]] += 1
    return {
        "edges": list(edges),
        "labels": labels,
        "counts": counts,
        # 单候选时 margin 无定义（不是 0——0 表示"两候选分数相同"，语义完全不同）
        "n_single_candidate": single,
        "n_with_margin": len(margins),
        # 阴性读数成对产出：直方图全 0 时必须能看出"本轮压根没触发"
        "n_triggered": triggered,
        "n_linked": linked,
        "thresholds": {str(k): v for k, v in sorted(thresholds.items())},
    }


def aggregate_traces(traces: list[dict], *, cases: int | None = None,
                     label: str = "positives") -> dict:
    """聚合 ``RetrievalTrace`` 列表 → ``trace_agg``（架构表 7.6.4-a 逐字段）。

    设计侧硬要求：``kept_in_final`` 必须在**聚合层**同样保留（瀑布图每通道并列显示
    ``hit_count`` 与 ``kept_in_final``），否则只能看单查询、看不到跨题趋势。
    分母纪律：``cases_executed`` 是该通道 executed=True 的题数，
    ``hit_rate``/``hit_avg``/``kept_*``/``squeezed_avg`` 一律以它为分母；
    **分母为 0 时一律 null，绝不填 0**（"未跑"不得被污染成"跑了但没产出"）。
    """
    total_cases = int(cases if cases is not None else len(traces))
    chan: dict[str, dict] = {}
    for name in CHANNEL_ORDER:
        chan[name] = {
            "channel": name, "cases_executed": 0, "hit_cases": 0, "hit_sum": 0,
            "blk_sum": 0, "kept_sum": 0, "squeezed_sum": 0, "skip_dist": Counter(),
            "lat": [], "edge_items_sum": 0, "mention_items_sum": 0,
        }
    skip_dist: Counter = Counter()
    fallback_counts: Counter = Counter()
    total_lat: list[float] = []
    margins: list[float] = []
    single_candidate = 0
    triggered = linked = 0
    thresholds: Counter = Counter()
    seeds_sum = 0
    raw_final_paths: Counter = Counter()
    for t in traces:
        if not t:
            continue
        seeds_sum += int(t.get("seeds_total") or 0)
        raw_final_paths.update(t.get("final_paths") or {})
        for r in t.get("fallbacks") or []:
            fallback_counts[str(r)] += 1
        total_lat.append(_lat(t))
        m = t.get("entity_link_margin") or {}
        if m.get("triggered"):
            triggered += 1
            linked += int(bool(m.get("linked")))
            thresholds[m.get("threshold")] += 1
            if m.get("margin") is None:
                single_candidate += 1
            else:
                margins.append(float(m["margin"]))
        for rec in t.get("channels") or []:
            name = str(rec.get("channel") or "")
            c = chan.get(name)
            if c is None:
                # 未知通道名不静默丢（schema 违反证据）：另立一条，看板能立刻看出契约破了
                c = chan.setdefault(name, {
                    "channel": name, "cases_executed": 0, "hit_cases": 0, "hit_sum": 0,
                    "kept_sum": 0, "squeezed_sum": 0, "skip_dist": Counter(), "lat": [],
                    "edge_items_sum": 0, "mention_items_sum": 0, "unknown_channel": True,
                })
            hits = int(rec.get("hit_count") or 0)
            kept = int(rec.get("kept_in_final") or 0)
            # 块级命中数：缺 hit_blocks（旧报告）时按 hit_count 兜底
            blk = int(rec.get("hit_blocks") if rec.get("hit_blocks") is not None else hits)
            if rec.get("executed"):
                c["cases_executed"] += 1
                c["hit_cases"] += int(hits > 0)
                c["hit_sum"] += hits
                c["blk_sum"] += blk
                c["kept_sum"] += kept
                c["squeezed_sum"] += max(0, blk - kept)
                c["lat"].append(float(rec.get("latency_ms") or 0.0))
                det = rec.get("detail") or {}
                c["edge_items_sum"] += int(det.get("edge_items") or 0)
                c["mention_items_sum"] += int(det.get("mention_items") or 0)
            if hits == 0:
                # §7.6.4-a：`skip_reason_dist` 仅统计 hit_count == 0 的题（空态数据源）
                reason = str(rec.get("skip_reason") or "MISSING_SKIP_REASON")
                c["skip_dist"][reason] += 1
                skip_dist[reason] += 1
    total_kept = sum(c["kept_sum"] for c in chan.values())
    channels: list[dict] = []
    for name in CHANNEL_ORDER:
        c = chan[name]
        ex = c["cases_executed"]
        channels.append({
            "channel": name,
            # 量纲显式落盘：看板把「别名精确」的 hit_avg 与 kept_avg 并列排时
            # 必须知道前者是种子数、后者是块数，否则会像人一样误读成保留率
            "unit": "seed" if name == "别名精确" else "block",
            "unit_note": ("「别名精确」是**种子来源维度**（架构 §7.6.1：exact 是种子来源，"
                          "非块通道），hit_* 为种子数；块级口径看 hit_blocks_* 与 kept_*"
                          if name == "别名精确" else "hit_* 与 hit_blocks_* 同为单位（块/路径条目）"),
            "cases_executed": ex,
            "hit_rate": _safe_div(c["hit_cases"], ex),
            "hit_avg": _safe_div(c["hit_sum"], ex),
            "kept_in_final_avg": _safe_div(c["kept_sum"], ex),
            # kept_rate 的分母是**块级候选数之和**（= hit_blocks，与 kept_in_final 同量纲）：
            # 「别名精确」的 hit_count 是**种子数**，拿它当分母会算出 >100% 的不可能
            # 读数（实测 229%）——故分母一律用 blk_sum。分母 0 → null（"未跑"不得
            # 显示成 0% 保留率）。
            "kept_rate": _safe_div(c["kept_sum"], c["blk_sum"]),
            "kept_rate_basis": "kept_in_final / hit_blocks（同量纲：块级路径条目）",
            "hit_blocks_avg": _safe_div(c["blk_sum"], ex),
            "squeezed_avg": _safe_div(c["squeezed_sum"], ex),
            "contribution_share": _safe_div(c["kept_sum"], total_kept),
            "skip_reason_dist": dict(c["skip_dist"]),
            "latency": {
                "p50": round(percentile(c["lat"], 0.50), 1) if c["lat"] else None,
                "p95": round(percentile(c["lat"], 0.95), 1) if c["lat"] else None,
            },
            "hit_total": c["hit_sum"],
            "hit_blocks_total": c["blk_sum"],
            "kept_total": c["kept_sum"],
        })
    # 桶 4 的全局量化只**在块量纲上**求和：混入「别名精确」（种子量纲）会把
    # "1 个种子 - 1 个块"这种减法算进来，得到的数既不是块数也不是种子数。
    # 块通道 = 6 通道去掉「别名精确」（种子来源维度）。
    BLOCK_CHANNELS = tuple(n for n in CHANNEL_ORDER if n != "别名精确")
    squeezed_total = sum(chan[n]["squeezed_sum"] for n in BLOCK_CHANNELS)
    squeezed_literal = sum(c["squeezed_sum"] for c in chan.values())
    g_prop = chan["图传播"]["blk_sum"]
    g_chap = chan["篇章路由"]["blk_sum"]
    return {
        "label": label,
        "cases": total_cases,
        "traced_cases": len([t for t in traces if t]),
        "channels": channels,
        "skip_reason_dist": dict(skip_dist),
        # 桶 4「融合层稀释」的全局量化 + **其适用性前提**（§7.6.6 强制成对）
        "squeezed_total": squeezed_total,
        "squeezed_total_basis": ("Σ over 块通道（6 通道去「别名精确」）× max(0, hit_blocks − "
                                 "kept_in_final)；「别名精确」是种子来源维度，量纲不同不参与求和"),
        "squeezed_total_block_channels": list(BLOCK_CHANNELS),
        # 规格原文公式（Σ_channels(hit_count − kept_in_final)）的**逐字复算值**：
        # 与主口径的差额即"种子量纲混入块量纲"的量，落盘以便审计而不是悄悄改口径
        "squeezed_total_literal_spec_formula": squeezed_literal,
        "graph_hit_total": g_prop + g_chap,
        "graph_hit_total_basis": "图传播 + 篇章路由（display 通道口径，含 mention 块）",
        "graph_hit_edge_total": chan["图传播"]["edge_items_sum"],
        "graph_hit_mention_total": chan["图传播"]["mention_items_sum"],
        "graph_hit_total_edge_chapter": chan["图传播"]["edge_items_sum"] + g_chap,
        # 与 graph_hit_total 严格同量纲（同一批块通道的子集）：桶 4 的成对读数
        "squeezed_total_graph_only": (chan["图传播"]["squeezed_sum"]
                                      + chan["篇章路由"]["squeezed_sum"]),
        "margin_histogram": _margin_histogram(margins, single_candidate, thresholds,
                                             triggered, linked),
        "fallback_counts": dict(fallback_counts),
        # 通则：fallback_counts 全 0 必须与本轮题量 + 端到端延迟同期呈现
        "total_ms": {
            "p50": round(percentile(total_lat, 0.50), 1) if total_lat else None,
            "p95": round(percentile(total_lat, 0.95), 1) if total_lat else None,
        },
        "seeds_total_sum": seeds_sum,
        "seeds_avg": _safe_div(seeds_sum, total_cases),
        "final_paths_attribution": dict(raw_final_paths),
    }


def compute_flipped(pass_on: dict, pass_off: dict) -> list[dict]:
    """逐题配对 diff（**唯一** diff 口径，`diff_vs_baseline` 与 `ablation` 共用）。

    方向不可反：``pass_to_fail`` = 参照轮通过、本轮失败（回退）；``fail_to_pass`` = 提升。
    只有两轮都在的题参与配对（配对设计前提：集合取交集，缺题不补 0）。
    """
    ids = sorted(set(pass_on) & set(pass_off))
    return (
        [{"id": i, "direction": "pass_to_fail"} for i in ids
         if pass_on[i] and not pass_off[i]]
        + [{"id": i, "direction": "fail_to_pass"} for i in ids
           if (not pass_on[i]) and pass_off[i]]
    )


def mcnemar_ablation(pass_on: dict, pass_off: dict, cases_executed: int | None,
                     feature_flag: str, *, activation: dict | None = None,
                     cases_executed_basis: str = "") -> dict:
    """AC-1 唯一判据：McNemar 配对检验（架构表 7.6.4-b 的 11 字段逐字落地）。

    - ``pass_on`` / ``pass_off``：同题集逐题布尔判定（键 = 题目 id），只取交集做配对；
    - ``m == 0`` **在计算之前短路**返回 ``mcnemar_p = null``（先算再截断会得到 1.0 假值）；
    - ``b + c < 25`` → 精确二项检验（``exact``），否则卡方近似（含连续性校正）；
    - ``delta_pt`` 仅快速判读，**不作显著性判据**（300 题下 1pt = 3 题，配对模型下仅噪声级）；
    - 附加键（字段只增不改，§7.6.5-5）：``activation`` / ``delta_pt_tier`` / ``conclusion`` /
      ``cases_executed_basis``——供报告与看板直接使用，判据仍是 ``mcnemar_p``。
    """
    ids = sorted(set(pass_on) & set(pass_off))
    cases_total = len(ids)
    b = sum(1 for i in ids if pass_on[i] and not pass_off[i])       # 通过 → 失败
    c = sum(1 for i in ids if (not pass_on[i]) and pass_off[i])     # 失败 → 通过
    m = b + c
    flipped = compute_flipped(pass_on, pass_off)
    delta_pt = round((c - b) / cases_total * 100, 2) if cases_total else None
    out = {
        "m": m, "b": b, "c": c,
        "delta_pt": delta_pt,
        "mcnemar_p": None,
        "method": "exact",
        "case_ids_flipped": flipped,
        "cases_executed": cases_executed,
        "cases_total": cases_total,
        "feature_flag": feature_flag,
        "trace_schema": ABLATION_SCHEMA,
    }
    if m == 0:
        out.update({
            "activation": dict(activation or {}),
            "cases_executed_basis": cases_executed_basis,
            "delta_pt_tier": "≤1pt（≤3 题）：贡献不显著",
            "conclusion": (
                "无翻转：Δ 严格为 0，**无检验意义**（mcnemar_p 必须为 null，不得给 1.0 假值）。"
                f"先看 cases_executed={cases_executed} —— 为 0 只说明「功能本次未触发」，"
                "不构成「功能无效」的证据（§7.6.6）"
            ),
        })
        return out
    if m < 25:
        method = "exact"
        k = min(b, c)
        p = 2.0 * sum(comb(m, i) for i in range(k + 1)) / (2.0 ** m)
        p = min(1.0, p)
    else:
        method = "chi2_approx_corrected"
        chi2 = (abs(b - c) - 1) ** 2 / m
        p = erfc(sqrt(chi2 / 2.0))
    out["method"] = method
    out["mcnemar_p"] = round(p, 6)
    if abs(delta_pt or 0) >= 3:
        tier = "≥3pt（≥9 题）：可分辨贡献（建议以 McNemar 复核）"
    elif abs(delta_pt or 0) > 1:
        tier = "1–3pt：贡献不明确（配对误差带内，需复核 m 与检验结论）"
    else:
        tier = "≤1pt（≤3 题）：贡献不显著"
    if p < 0.05:
        concl = ("留（贡献显著）" if c > b
                 else "默认关/删（关闭后反而更好，且差异显著）")
    else:
        # 不显著 ≠ 无效：必须写明这个区分，否则 1–3pt 档最容易被跳过
        concl = ("不显著：正式结论不得写「无效」——不显著只表示本轮证据不足；"
                 "须同时给出 cases_executed 与 m 才能判读")
    out.update({
        "activation": dict(activation or {}),
        "cases_executed_basis": cases_executed_basis,
        "delta_pt_tier": tier,
        "conclusion": concl,
    })
    return out


def cases_executed_for(rows: list[dict], flag: str) -> tuple[int | None, str, dict]:
    """该功能本次**实际触发**的题数（§7.6.6 的适用性前提）。

    返回 ``(cases_executed, basis, activation_totals)``。``None`` 表示该开关不改变
    检索结果（如纯埋点），此时不填 0——0 会被误读成"未触发"。
    """
    key = ACTIVATION_KEYS.get(flag, "__unregistered__")
    if key is None:
        return None, "该开关不改变检索结果（纯埋点），cases_executed 不适用", {}
    totals: Counter = Counter()
    for r in rows:
        for k, v in (r.get("activation") or {}).items():
            totals[k] += int(v or 0)
    if key == "__unregistered__":
        return 0, (f"开关 {flag} 未在 ACTIVATION_KEYS 登记执行计数键——"
                   f"cases_executed 不可解释，按 0 输出（须补登记）"), dict(totals)
    n = sum(1 for r in rows if int((r.get("activation") or {}).get(key) or 0) > 0)
    if key == "c4_candidates":
        basis = ("该题图路存在「被豁免保留且落在跳距内」的弱证边（可能作用面）；"
                 "c4_used 为其中真正产出证据块的题数")
    elif key == "d1_seeds_downweighted":
        basis = "该题至少有 1 个种子被降权（specificity<1）；孤立种子按 1.0 不计"
    else:
        basis = f"activation[{key}] > 0 的题数"
    return n, basis, dict(totals)


# ── 失分桶归因（架构 §4e 五桶）────────────────────────────────────────────
# 规则**显式落盘**（报告内 `bucket_attribution.rules`）：桶判定必须可由数据复现，
# 不允许"研究员心证"。优先级固定 1→2→3→5→4：先归因"更上游"的病灶
# （链接失败 → 阈值拦死 → 图传不出 → 跨语言 → 被融合挤出），一题只进一个桶。
BUCKET_RULES = [
    ("bucket1_alias_bridge_missing", "别名桥缺失",
     "seeds_total == 0：查询不含任何可链接的实体名/别名，图路无起点（PPR/提及全死）"),
    ("bucket2_semantic_no_margin", "语义兜底无安全间隔",
     "实体链接兜底触发但 linked=False：候选中分数重叠，过不了阈值（正解可能就在候选里）"),
    ("bucket3_extraction_imbalance", "抽取召回不均",
     "有种子但「图传播」hit_count == 0：链接成功，图却传不出任何证据边"),
    ("bucket5_crosslingual", "跨语言底座",
     "查询为中文且返回块 CJK 占比 < 0.5：中文查询 vs 英文 ASR 正文，词法不可比"),
    ("bucket4_fusion_squeeze", "融合层稀释",
     "图通道有命中但 kept_in_final == 0：通道有货，被 RRF 融合层挤出最终结果"),
]

# triage 口径下 §4e 桶的判据文字（与审计 §1 的根因定义逐字对应；与 trace 规则区分开，
# 避免报告里出现"用 A 口径的判据描述 B 口径的读数"）
TRIAGE_BUCKET_RULE = {
    "bucket1_alias_bridge_missing":
        "alias_bridge_gap：实体在图里，但**查询里根本没出现该证据组实体的任何名字/别名**",
    "bucket3_extraction_imbalance":
        "graph_gap（语料有块但没被图谱引用为证据）+ unreachable_gap（有证据但本次激活不到）",
}

# 为什么必须复用而不是自造规则（本轮踩到）：同一条问法「海盗船上的歌手是谁」在
# trace 里 seeds_total>0（"海盗"被 token 路匹配上了），于是自造规则把它判成"非桶 1"，
# 而 §4e 的桶 1 定义是「实体在图里，但**查询里没出现它的任何名字**」——**按缺失证据组
# 对应的实体**判，不是按"有没有种子"判。自造规则的读数（桶 1 = 0 题）与 §4e 的
# 111 题差了整整一个数量级，属于**归因口径漂移**，必须消灭。
TRIAGE_PATH = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_triage_final.json"
# 自动发现顺序：本轮跑批产物优先，其后是历史命名（两者同名不同源时容易张冠李戴，
# 故报告里必须写清用的是哪一份，且通过题数与本轮不一致时给出告警）
TRIAGE_CANDIDATES = (
    ROOT / "data" / "knowledge" / "_audit" / "plot_rag_triage_r0.json",
    TRIAGE_PATH,
)
TRIAGE_BUCKET_MAP = {
    "alias_bridge_gap": "bucket1_alias_bridge_missing",
    # 图里记了证据但取不回来 / 够不着：§4e 归入「抽取召回不均」（边密度不足）
    "graph_gap": "bucket3_extraction_imbalance",
    "unreachable_gap": "bucket3_extraction_imbalance",
}
# triage 里**没有** §4e 对应桶的原因：必须单列（数据/算法缺口不是"未归因"，
# 把它们塞进"未归因"会让最大的账变成一笔糊涂账）
TRIAGE_UNMAPPED_HINT = {
    "no_entity_gap": "证据组关键词在图谱里找不到实体（补实体，数据面）",
    "corpus_gap": "语料里没有任何块含该证据词（补语料，数据面）",
    "link_bug": "名字就在查询里却没链上（修链接，算法面）",
    "retrieval_gap": "图谱记了证据也够得着，但没取回（修排序，算法面）",
    "covered": "本题已覆盖（不计入失分）",
}
# §4e 表给出的期望规模（用于架构 §5 第 9 条：「确认无某桶题量占比严重偏离预期」）
SECTION4E_EXPECTED = {
    "bucket1_alias_bridge_missing": "111/300 题（审计 §1 基线，126 个缺失证据组）",
    "bucket2_semantic_no_margin": "分诊实测：负样本实体 0.60–0.82 > 失败题正解 0.48",
    "bucket3_extraction_imbalance": "边数极不平衡（高塔 5 边 vs 阿莱夫 32 边）",
    "bucket4_fusion_squeeze": "附加桶（PM F5 假设；扩大候选已被证伪）",
    "bucket5_crosslingual": "9021 块中 88% 为英文 ASR",
}


def classify_bucket(row: dict, trace: dict | None) -> str:
    """按 §4e 优先级给**失分题**归桶；无信号 → ``unattributed``。"""
    if not trace:
        # 缺 trace 时**不得**当成"seeds_total=0"（那是把"没数据"读成"零读数"，
        # 通则明确禁止的误读），单列一个数据可得性桶
        return "unattributed_no_trace"
    t = trace
    chans = {str(r.get("channel")): r for r in (t.get("channels") or [])}
    graph = chans.get("图传播") or {}
    chapter = chans.get("篇章路由") or {}
    seeds = int(t.get("seeds_total") or 0)
    margin = t.get("entity_link_margin") or {}
    if seeds == 0:
        return "bucket1_alias_bridge_missing"
    if margin.get("triggered") and not margin.get("linked"):
        return "bucket2_semantic_no_margin"
    if int(graph.get("hit_count") or 0) == 0:
        return "bucket3_extraction_imbalance"
    if str(t.get("query_lang") or "") == "zh" and float(row.get("zh_ratio") or 0.0) < 0.5:
        return "bucket5_crosslingual"
    if (int(graph.get("hit_count") or 0) > 0
            and int(graph.get("kept_in_final") or 0) == 0
            and int(chapter.get("kept_in_final") or 0) == 0):
        return "bucket4_fusion_squeeze"
    return "unattributed"


def _trace_signals(rows: list[dict], traces: list[dict | None]) -> tuple[Counter, dict]:
    """trace 可见的**症状**信号（可重叠，且只覆盖"链路失效"型失分）。

    与 §4e 桶的差别：桶 1 的判据是"查询里没有**该证据组实体**的名字"（需要 triage 的
    组级分析），而 trace 只能看到"本次有没有种子"。两者不可互相替代，故分开呈现。
    """
    signals: Counter = Counter()
    by_id: dict[str, dict] = {}
    for i, r in enumerate(rows):
        if i < len(traces) and traces[i]:
            by_id[str(r.get("id"))] = traces[i]
    for r in rows:
        if r.get("strict_pass"):
            continue
        t = by_id.get(str(r.get("id")))
        if not t:
            signals["no_trace"] += 1
            continue
        chans = {str(x.get("channel")): x for x in (t.get("channels") or [])}
        g = chans.get("图传播") or {}
        if int(t.get("seeds_total") or 0) == 0:
            signals["seeds_empty"] += 1
        if (t.get("entity_link_margin") or {}).get("triggered"):
            signals["margin_triggered"] += 1
            if not (t.get("entity_link_margin") or {}).get("linked"):
                signals["margin_rejected"] += 1
        if int(g.get("hit_count") or 0) == 0:
            signals["graph_no_hit"] += 1
        if int(g.get("hit_count") or 0) > int(g.get("kept_in_final") or 0):
            signals["graph_squeezed"] += 1
        if str(t.get("query_lang") or "") == "zh" and float(r.get("zh_ratio") or 0.0) < 0.5:
            signals["zh_query_en_chunks"] += 1
    return signals, by_id


def bucket_attribution(rows: list[dict], traces: list[dict | None],
                       triage: dict | None = None) -> dict:
    """本次题量按 §4e 五桶的分布（F7）。

    两层口径，**不可互相替代**：
      - 第一层 `section4e`：桶的**根因**归因。有 triage 报告时按 triage 的逐题根因
        （与审计 §1 同一口径：按**缺失证据组对应实体**判"查询里有没有它的名字"）；
        没有 triage 时退回 trace 规则，并显式标注 `source=trace_rules`（次优口径）。
      - 第二层 `trace_signals`：链路**症状**计数（可重叠），含 triage 看不见的
        桶 4（融合层稀释）与桶 5（跨语言）——它们本质是"取回后"的现象。
    通过题不占桶；失分题才归桶。
    """
    failed = [r for r in rows if not r.get("strict_pass")]
    n_fail = max(1, len(failed))
    signals, by_id = _trace_signals(rows, traces)
    section: dict[str, dict] = {}
    reasons: Counter = Counter()
    source = "trace_rules"
    if triage and (triage.get("items") or triage.get("summary")):
        source = "triage_plot_rag.py（逐题根因；与审计 §1 同口径）"
        by_id_t = {str(r.get("id")): r for r in (triage.get("items") or [])}
        for r in failed:
            t = by_id_t.get(str(r.get("id")))
            reason = str((t or {}).get("reason") or "unknown")
            reasons[reason] += 1
            # 映射到 §4e 桶；没有对应桶的原因**以自身名义立一条**（单列，不并入未归因）
            b = TRIAGE_BUCKET_MAP.get(reason, reason)
            section[b] = section.get(b, {"cases": 0})
            section[b]["cases"] += 1
    else:
        # 次优口径：trace 规则（**注明**，不允许与 triage 口径混用读数）
        for r in failed:
            t = by_id.get(str(r.get("id")))
            b = classify_bucket(r, t)
            section[b] = section.get(b, {"cases": 0})
            section[b]["cases"] += 1
    # 桶 4 / 桶 5 是"取回后"的现象，triage 看不见 → 一律由 trace 补（可重叠，单列）
    overlay = {
        "bucket4_fusion_squeeze": signals.get("graph_squeezed", 0),
        "bucket5_crosslingual": signals.get("zh_query_en_chunks", 0),
    }
    out_buckets: dict[str, dict] = {}
    for key, name, rule in BUCKET_RULES:
        n = int((section.get(key) or {}).get("cases", 0))
        out_buckets[key] = {
            "name": name, "cases": n,
            "share_of_failed": round(n / n_fail, 4),
            # 判据文字必须与**实际用的口径**一致（triage 口径 vs trace 次优口径）
            "rule": TRIAGE_BUCKET_RULE.get(key, rule) if source.startswith("triage")
                    else rule,
            "expected_reference": SECTION4E_EXPECTED.get(key, ""),
            "trace_overlay_cases": overlay.get(key, 0),
        }
    # §4e 之外的原因/桶：**单列**，不塞进"未归因"（塞进去就成了糊涂账）
    EXTRA_LABELS = {
        "unattributed": "未归因（trace 口径）",
        "unattributed_no_trace": "无 trace（数据可得性）",
    }
    EXTRA_RULES = {
        "unattributed": "以上规则均不匹配：多为「证据组部分覆盖」型失分（非链路失效）",
        "unattributed_no_trace": "本题未进入埋点轮：不得据此断言任何病灶（缺数据 ≠ 零读数）",
    }
    for key, sub in section.items():
        if key in out_buckets:
            continue
        n = int((sub or {}).get("cases", 0))
        out_buckets[key] = {
            "name": EXTRA_LABELS.get(key, key), "cases": n,
            "share_of_failed": round(n / n_fail, 4),
            "rule": EXTRA_RULES.get(key, TRIAGE_UNMAPPED_HINT.get(
                key, "triage 原因在 §4e 无对应桶（数据面/算法面缺口）")),
            "expected_reference": "—（§4e 未列此桶）",
            "trace_overlay_cases": 0,
        }
    unmapped = {k: v for k, v in reasons.items() if k not in TRIAGE_BUCKET_MAP}
    return {
        "cases_total": len(rows),
        "cases_failed": len(failed),
        "cases_passed": len(rows) - len(failed),
        "traced_cases": len(by_id),
        "source": source,
        "triage_source": (triage or {}).get("_src") or None,
        "triage_pass": ((triage or {}).get("summary") or {}).get("pass"),
        "section4e": out_buckets,
        # triage 的全部根因（含 §4e 未列的原因）——**不折算、不静默**：
        # 数据面/算法面的缺口既不是五桶之一，也不是"未归因"
        "triage_reasons": dict(reasons),
        "unmapped_reasons": unmapped,
        "trace_signals": dict(signals),
        "overlay_note": ("桶 4/桶 5 由 trace 补（triage 看不见「取回后」现象），"
                         "其 `trace_overlay_cases` 与桶计数可重叠"),
        "note": ("第一层 section4e = 根因归因（一题一桶，按 triage 逐题最严重根因）；"
                 "第二层 trace_signals = 症状计数（可重叠）。两者读数不可互相校验。"),
    }



@contextmanager
def settings_override(overrides: dict[str, str]):
    """临时覆盖 ``ROLEPLAY_*`` 环境变量并刷新 Settings 缓存，退出时逐键还原。

    消融必须**走与生产同一条装配路径**（``build_plot_registry(get_settings())``），
    否则测的又是另一套配置（本项目在 §F9「手工装配注册表」上已经踩过一次）。
    """
    keys = {f"ROLEPLAY_{k.upper()}": str(v) for k, v in overrides.items()}
    old = {k: os.environ.get(k) for k in keys}
    os.environ.update(keys)
    get_settings.cache_clear()
    try:
        yield get_settings()
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        get_settings.cache_clear()


def run_pass(retr, items: list[dict], oracle: dict, top: int, lexical_fallback: int,
             inject_chars: int, *, quiet: bool = True, tag: str = "") -> list[dict]:
    """跑一轮评测（可复用：主轮 / 埋点轮 / 消融轮）。"""
    rows: list[dict] = []
    for i, item in enumerate(items, start=1):
        rows.append(evaluate_case(retr, item, oracle[str(item.get("id"))], top,
                                  lexical_fallback, inject_chars))
        if not quiet and i % 25 == 0:
            print(f"  [{tag}] {i}/{len(items)}", flush=True)
    return rows


def run_trace_pass(retr, items: list[dict], oracle: dict, top: int,
                   lexical_fallback: int, inject_chars: int) -> tuple[list[dict | None], list[dict]]:
    """埋点轮：开 trace 重跑同题集，返回 ``(traces, rows)``。

    两条纪律：
      1. **延迟只取无埋点首轮**——埋点若计入 p95，A1 的 ≤100ms 增量判据会被评测自身污染；
      2. 埋点轮**不写运行期 jsonl**（``trace_out_path`` 临时置 None）：那是生产排障轨道，
         评测批量写 353 条查询会把真正的现场淹掉。
    同时这轮天然是"埋点不改变检索结果"的不变量检验（与首轮逐题判定比对）。
    """
    keep_enabled, keep_path = retr.trace_enabled, retr.trace_out_path
    retr.trace_enabled, retr.trace_out_path = True, None
    traces: list[dict | None] = []
    rows: list[dict] = []
    try:
        for item in items:
            rows.append(evaluate_case(retr, item, oracle[str(item.get("id"))], top,
                                      lexical_fallback, inject_chars))
            t = getattr(retr, "last_trace", None)
            traces.append(t.to_dict() if t is not None else None)
    finally:
        retr.trace_enabled, retr.trace_out_path = keep_enabled, keep_path
    return traces, rows


def trace_invariance(main_rows: list[dict], trace_rows: list[dict]) -> dict:
    """埋点轮与首轮的逐题一致性（同一题集、同一配置、仅埋点开关不同）。"""
    pairs = list(zip(main_rows, trace_rows))
    diff_ids = [str(a.get("id")) for a, b in pairs
                if a.get("strict_pass") != b.get("strict_pass")
                or a.get("n_chunks") != b.get("n_chunks")]
    return {
        "cases": len(pairs),
        "identical": not diff_ids,
        "diff_ids": diff_ids[:20],
        "diff_cases": len(diff_ids),
        "note": "埋点（M-11）应不改变任何检索结果；不一致即为埋点污染主链路",
    }


def compare_with_baseline(base: dict, cur: dict, tolerance: float = TOLERANCE) -> tuple[list[dict], bool]:
    """与基线报告对比，返回 (对比行, 是否回退)。"""
    b, c = base.get("summary", {}), cur.get("summary", {})
    b_neg = base.get("negatives", {}).get("negative_injection_total")
    c_neg = cur.get("negatives", {}).get("negative_injection_total")
    b_neg_cases = base.get("negatives", {}).get("cases")
    c_neg_cases = cur.get("negatives", {}).get("cases")
    # 负样本**条数变了就不可比**：绝对注入块数会随题量线性放大，跨口径比大小是假回退
    # （实测：10 条基线 0 块 vs 53 条本轮 37 块，被误报成 +37 回退）。只做提示，不判回退。
    neg_comparable = (b_neg_cases == c_neg_cases)
    rows: list[dict] = []
    regressed = False

    def _add(name: str, before, after, higher_better: bool,
             tol: float | None = None) -> None:
        nonlocal regressed
        if before is None or after is None:
            rows.append({"metric": name, "baseline": before, "current": after, "delta": None})
            return
        delta = round(float(after) - float(before), 4)
        # 延迟用**自己的**判据（A1：增量 ≤100ms），不吃通用容差——
        # 通用容差 0.02 是为比率型指标（0.5pt）设计的，套到 693ms 上等于 ±0.02ms，
        # 1ms 的正常抖动就会被判回退（实测踩到）。Spec §1.4.1 三口径也明确要求
        # 延迟单独裁决，不与其它指标混用同一把尺。
        thr = TARGET_LATENCY_INCREMENT_MS if tol is None and name == "latency_p95_ms" \
            else (tolerance if tol is None else tol)
        bad = delta < -thr if higher_better else delta > thr
        regressed = regressed or bad
        rows.append(
            {
                "metric": name,
                "baseline": before,
                "current": after,
                "delta": delta,
                "verdict": "回退" if bad else ("提升" if delta else "持平"),
            }
        )

    for key in HIGHER_IS_BETTER:
        _add(key, b.get(key), c.get(key), True)
    for key in LOWER_IS_BETTER:
        if key == "negative_injection_total":
            if not neg_comparable:
                # 口径不可比：只登记数值与原因，**不判回退**（假回退会掩盖真问题）
                rows.append({
                    "metric": key, "baseline": b_neg, "current": c_neg, "delta": None,
                    "verdict": f"口径不可比（负样本 {b_neg_cases} → {c_neg_cases} 条，"
                               f"绝对块数随题量放大）",
                })
            else:
                _add(key, b_neg, c_neg, False)
        else:
            _add(key, b.get(key), c.get(key), False)
    return rows, regressed


def check_targets(summary: dict, negatives: dict,
                  baseline: dict | None = None, *,
                  ablation: dict | None = None) -> tuple[bool, list[str]]:
    """验收线自检（A1 / A5 / AC-1；A2–A4 属相对基线增量，由 --baseline 判定）。

    A1 口径（Spec AC-5，三口径不可混用）：**唯一合入判据 = 新增在线组件 p95 增量
    ≤ 100ms**（相对同条件基线）。没有基线时报绝对值为**参考信息**，不判不合格——
    历史 300ms 线是消歧遗留，Spec 已明确它不作判据（否则 M8 语义层的 ~500ms
    查询嵌入会被判死，而它是当前最大的一块收益来源）。

    AC-1（消融）只做**口径自检**，不设 pt 合格线：判据是 ``mcnemar_p``，
    且 ``Δ≈0`` 必须带 ``cases_executed``、``m == 0`` 必须带 ``mcnemar_p = null``。
    """
    notes: list[str] = []
    ok = True
    b_p95 = None
    if baseline:
        b_p95 = (baseline.get("summary") or {}).get("latency_p95_ms")
    if b_p95 is None:
        notes.append(
            f"[参考] p95 {summary['latency_p95_ms']}ms（未提供同条件基线；"
            f"增量判据 ≤{TARGET_LATENCY_INCREMENT_MS}ms 本轮无法判定）"
        )
    else:
        inc = round(float(summary["latency_p95_ms"]) - float(b_p95), 1)
        if inc > TARGET_LATENCY_INCREMENT_MS:
            ok = False
            notes.append(
                f"A1 未达标：p95 增量 {inc}ms > {TARGET_LATENCY_INCREMENT_MS}ms"
                f"（基线 {b_p95}ms → 本轮 {summary['latency_p95_ms']}ms；"
                f"只写「基线值 + 本轮回测值 + 增量 + 是否达标」四件）"
            )
        else:
            notes.append(f"A1 达标：p95 增量 {inc}ms ≤ {TARGET_LATENCY_INCREMENT_MS}ms"
                         f"（基线 {b_p95}ms → 本轮 {summary['latency_p95_ms']}ms）")
    if negatives["negative_injection_total"] > TARGET_NEGATIVE_INJECTION:
        ok = False
        new_leaks = negatives.get("new_leaks") or []
        residual = negatives.get("known_residual") or []
        notes.append(
            f"A5 未达标：负样本注入 {negatives['negative_injection_total']} 块 / "
            f"{negatives['cases']} 条（判据 {TARGET_NEGATIVE_INJECTION}）"
            f"｜已知残余 {len(residual)} 条（待 B3 修复，已登记）"
            f"｜**新增泄漏 {len(new_leaks)} 条**"
            + (f"：{new_leaks}" if new_leaks else "")
        )
        if new_leaks:
            notes.append("A5 出现**新的**离题注入——这是回归，不是已知残余，必须先处理")
    else:
        notes.append(f"A5 达标：负样本 {negatives['cases']} 条零注入")
    if ablation is not None:
        # AC-1 口径自检：判据是 mcnemar_p，不是 delta_pt；Δ≈0 必须带 execution count
        m, p = ablation.get("m"), ablation.get("mcnemar_p")
        n_exec = ablation.get("cases_executed")
        if m == 0 and p is not None:
            ok = False
            notes.append(f"AC-1 口径违规：m=0 时 mcnemar_p 必须为 null，实得 {p}")
        elif m == 0:
            notes.append(
                f"AC-1 {ablation.get('feature_flag')}：m=0（无翻转）→ mcnemar_p=null；"
                f"cases_executed={n_exec}——"
                + ("该功能本次**未触发**，Δ=0 不构成「功能无效」的证据"
                   if n_exec == 0 else "功能已触发但判定无差异")
            )
        else:
            notes.append(
                f"AC-1 {ablation.get('feature_flag')}：m={m}（b={ablation.get('b')}"
                f"/c={ablation.get('c')}）Δ={ablation.get('delta_pt')}pt"
                f"｜mcnemar_p={p}（{ablation.get('method')}，<0.05 才叫显著）"
                f"｜cases_executed={n_exec}"
            )
    return ok, notes


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情 RAG 离线检索评测台（300 题集）")
    ap.add_argument("--character", default=DEFAULT_CHARACTER, help="角色 id（默认 wu_ming_zhe）")
    ap.add_argument("--evidence-override", default=str(OVERRIDES_PATH),
                    help="证据组 override 清单（主组口径）；置空字符串则禁用")
    ap.add_argument("--testset", default="",
                    help="题库路径（默认现行基准 rag_testset_300.json）")
    # 默认与生产严格对齐：plot_max_chunks=3 + plot_lexical_fallback=2（返回上限 5 块）。
    # 想复现灰机报告的宽松口径可显式 --top 10。
    ap.add_argument("--top", type=int, default=None,
                    help="图路返回块上限（默认取生产 settings.plot_max_chunks）")
    ap.add_argument("--lexical-fallback", type=int, default=None,
                    help="词法兜底条数（默认取生产 settings.plot_lexical_fallback）")
    ap.add_argument("--sample", type=int, default=0, help="分层抽样题量（0=全量；同 seed 确定性）")
    ap.add_argument("--seed", type=int, default=7, help="抽样随机种子")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（冒烟用，不用于对比）")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="报告落盘路径")
    ap.add_argument("--baseline", default="", help="基线报告路径：与本次结果对比并判定回退")
    ap.add_argument(
        "--tolerance",
        type=float,
        default=TOLERANCE,
        help="回退判定容忍度（比率类指标；本轮验收规则为 −1pt 时可传 0.01）",
    )
    ap.add_argument("--check-targets", action="store_true", help="按审计验收线 A1/A5 自检")
    ap.add_argument(
        "--inject-chars", type=int, default=None,
        help="注入口径预算（默认取生产 settings.plot_context_max_chars；0=只算返回块口径）",
    )
    ap.add_argument("--quiet", action="store_true", help="不逐题打印")
    ap.add_argument("--allow-degraded", action="store_true",
                    help="允许在语义通道静默降级时继续出报告（报告会标注 DEGRADED）")
    # ── M-12 ────────────────────────────────────────────────────────────────
    ap.add_argument("--trace", dest="trace", action="store_true", default=True,
                    help="产出 trace_agg / bucket_attribution（默认开：评测内嵌 trace 段）")
    ap.add_argument("--no-trace", dest="trace", action="store_false",
                    help="跳过埋点轮（快跑；报告 trace_agg/bucket_attribution 为 null）")
    # ── P1-4 召回率修复 A/B：允许评测里直接覆盖保底名额，不必改生产配置 ──
    ap.add_argument("--min-semantic-kept", type=int, default=None,
                    help="语义通道保底保留块数（覆盖 settings；默认取生产值）")
    ap.add_argument("--min-chapter-kept", type=int, default=None,
                    help="篇章通道保底保留块数（覆盖 settings；默认取生产值）")
    ap.add_argument("--diversity-per-doc", type=int, default=None,
                    help="同 doc（同支视频/分P）软上限（覆盖 settings；默认取生产值）")
    ap.add_argument("--ablate-flag", default="",
                    help="消融开关名（如 plot_ppr_node_specificity）→ 产出 ablation 段")
    ap.add_argument("--ablate-on", default="",
                    help="该开关「全开」取值（默认取当前 Settings 值）；bool 传 true/false")
    ap.add_argument("--ablate-off", default="",
                    help="该开关「关闭」取值（缺省时按类型取 false/0/空串）")
    ap.add_argument("--ablate-reference", default="",
                    help="全开参照轮报告（复用其 items 做配对，省一轮 300 题；缺省用本轮主轮）")
    ap.add_argument("--triage", default="",
                    help="triage 报告路径（§4e 五桶的权威口径；缺省自动发现）")
    args = ap.parse_args()

    # 证据组 override（主组口径）：只在判定层生效，检索行为完全不变
    n_ov = load_evidence_overrides(Path(args.evidence_override)) if args.evidence_override else 0
    if n_ov:
        print(f"[override] 加载证据组 override {n_ov} 题（主组口径将与全组口径并列报告）")

    settings = get_settings()
    # 默认口径一律**取生产 Settings**，不写死常量：写死过一次（top=3/注入 1000），
    # 结果生产把预算调到 6/2400 后脚本仍在测旧配置——"评测与生产漂移"是本项目
    # 反复踩到的坑（见 §F9「手工装配注册表」同一类问题）。
    if args.top is None:
        args.top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    if args.lexical_fallback is None:
        args.lexical_fallback = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    if args.inject_chars is None:
        args.inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    # 走**生产同一条装配路径**（build_plot_registry 从 Settings 读全部检索参数）。
    # 反例教训：脚本一度自行 new PlotGraphRegistry(...) 只传了 4 个参数，新增的融合权重
    # 与门控参数全被默认值覆盖——评测量到的根本不是生产配置（消融实验 7 组结果一模一样
    # 才发现）。凡"调试入口"都必须与生产共用装配函数。
    registry = build_plot_registry(settings)
    # P1-4 召回率修复：允许评测里直接覆盖保底名额做 A/B，而不必改生产配置。
    # 必须在首次 get() 之前注入——注册表按 mtime 缓存检索器，之后改 _cfg 不会重建。
    if getattr(args, "min_semantic_kept", None) is not None:
        registry._cfg["min_semantic_kept"] = max(0, int(args.min_semantic_kept))
    if getattr(args, "min_chapter_kept", None) is not None:
        registry._cfg["min_chapter_kept"] = max(0, int(args.min_chapter_kept))
    if getattr(args, "diversity_per_doc", None) is not None:
        registry._cfg["diversity_per_doc"] = max(1, int(args.diversity_per_doc))
    t0 = time.time()
    retr = registry.get(args.character)
    if retr is None:
        print(f"[FAIL] 剧情图谱未能加载（角色 {args.character}）；请先运行 "
              f"scripts/build_plot_graph.py --character {args.character}")
        return 1
    # ── 护栏（2026-09-17 新增）：语义通道静默降级必须 fail loud ──
    # 事故：嵌入器在 ollama 探测失败时静默回退 hashing（embedder.py:253），
    # 语义索引随即因「模型不符」被静默停用（plot_graph._load_semantic 静默降级），
    # 结果 inject_pass 掉 6.7pt 却没有任何报错——当天 73 份报告里有 27 份是降级态。
    # 判据：配置要求语义开启，但检索器没拿到语义索引 ⇒ 拒绝出报告。
    # 逃生门：--allow-degraded（仅供刻意测量"无语义"状态时使用，报告会标注）。
    if (bool(getattr(settings, "plot_semantic_enabled", True))
            and getattr(retr, "semantic", None) is None
            and not args.allow_degraded):
        status = (getattr(registry, "semantic_status", {}) or {}).get(args.character)
        print("[FAIL] 语义通道已静默降级（语义索引未加载），拒绝在错误状态下出报告。")
        print(f"       registry.semantic_status[{args.character!r}] = {status!r}")
        print("       最常见原因：ollama 探测失败 → 嵌入器回退 hashing → 指纹不符。")
        print("       处置：确认 ollama 可用后重跑；或加 --allow-degraded 强行继续。")
        return 2
    load_s = time.time() - t0

    testset_path = Path(args.testset) if args.testset else None
    items = load_testset(testset_path)
    if args.sample:
        items = stratified_sample(items, args.sample, args.seed)
    if args.limit:
        items = items[: args.limit]

    print(
        f"[load] 角色 {args.character}｜实体 {len(retr.store.entities())}｜"
        f"边 {len(retr.store.all_edges())}｜语料 {len(retr.corpus.chunks)} 块｜"
        f"加载 {load_s:.2f}s"
    )
    print(f"[eval] 题量 {len(items)}｜top={args.top}｜lexical_fallback={args.lexical_fallback}"
          f"｜sample={args.sample or '全量'}｜seed={args.seed}")

    t0 = time.time()
    oracle = build_oracle(retr.corpus, items)
    ceiling_n = sum(1 for v in oracle.values() if v["ceiling"])
    print(f"[oracle] 天花板内题 {ceiling_n}/{len(items)}（其余题不存在单块覆盖全部证据组的语料块）"
          f"｜耗时 {time.time() - t0:.1f}s")

    rows: list[dict] = []
    t0 = time.time()
    for i, item in enumerate(items, start=1):
        row = evaluate_case(retr, item, oracle[str(item.get("id"))], args.top,
                            args.lexical_fallback, args.inject_chars)
        rows.append(row)
        if not args.quiet:
            tag = "PASS" if row["strict_pass"] else "FAIL"
            print(
                f"[{i:3d}/{len(items)}] {tag} {row['id']} {str(row['dims'].get('type'))[:9]:9s} "
                f"覆盖 {row['covered']}｜相关 {row['n_relevant']}/{row['n_chunks']}｜"
                f"满匹配 {row['n_full_match']}｜{row['latency_ms']:8.1f}ms  {row['q'][:30]}",
                flush=True,
            )
    eval_s = time.time() - t0

    summary = aggregate(rows)
    negatives = evaluate_negatives(retr, args.top, args.lexical_fallback)
    dims_report = {
        dim: by_dimension(rows, dim)
        for dim in ("type", "difficulty", "depth", "hop", "chapter", "text_len")
        if any((r.get("dims") or {}).get(dim) for r in rows)
    }

    # ── M-12：埋点轮（trace_agg + bucket_attribution）────────────────────────
    trace_agg: dict | None = None
    bucket_rep: dict | None = None
    if args.trace and not args.limit:
        t0 = time.time()
        traces, trace_rows = run_trace_pass(retr, items, oracle, args.top,
                                            args.lexical_fallback, args.inject_chars)
        trace_agg = aggregate_traces([t for t in traces if t], cases=len(items))
        trace_agg["invariance_vs_main_pass"] = trace_invariance(rows, trace_rows)
        # 负样本单独走一轮埋点（53 条，约 30s）：注入判定仍以 evaluate_negatives 的
        # 无埋点读数为准，这里的目的是拿**成因侧执行计数**——零注入既可能是"护栏有效"，
        # 也可能是"语义通道压根没触发"，只有执行计数能区分（§7.6.6 的原始动因）。
        neg_traces: list[dict | None] = []
        keep_enabled, keep_path = retr.trace_enabled, retr.trace_out_path
        retr.trace_enabled, retr.trace_out_path = True, None
        try:
            for _cat, _q in NEGATIVE_CASES:
                retr.retrieve(_q, top_chunks=args.top,
                              lexical_fallback=args.lexical_fallback)
                _t = getattr(retr, "last_trace", None)
                neg_traces.append(_t.to_dict() if _t is not None else None)
        finally:
            retr.trace_enabled, retr.trace_out_path = keep_enabled, keep_path
        trace_agg["negatives"] = aggregate_traces(
            [t for t in neg_traces if t], cases=len(NEGATIVE_CASES), label="negatives")
        # §4e 归因的第一层口径取 triage 报告（可 --triage 指定或自动发现）；
        # 缺报告时退回 trace 规则并在报告里标明口径（不允许口径不明地出数）
        triage_rep = None
        if args.triage:
            tp = Path(args.triage)
        else:
            tp = next((p for p in TRIAGE_CANDIDATES if p.is_file()), TRIAGE_CANDIDATES[0])
        if tp.is_file():
            try:
                triage_rep = json.loads(tp.read_text(encoding="utf-8"))
                triage_rep["_src"] = str(tp)
                _ts = (triage_rep.get("summary") or {})
                if _ts.get("pass") != summary["strict_pass_n"]:
                    # 口径漂移告警：triage 是**另一次运行**，题集规模/配置不一致时
                    # 它的逐题根因不能直接贴到本轮失分题上（会张冠李戴）
                    print(f"[warn] triage 报告与本轮不同源：triage 通过 {_ts.get('pass')} vs "
                          f"本轮 {summary['strict_pass_n']}——逐题根因仅供参考，"
                          f"建议重跑 scripts/triage_plot_rag.py")
            except Exception as exc:  # noqa: BLE001
                print(f"[warn] triage 报告读取失败（归因退回 trace 口径）：{exc}")
                triage_rep = None
        else:
            print(f"[warn] 未找到 triage 报告 {tp}：§4e 归因退回 trace 口径（次优）")
        bucket_rep = bucket_attribution(rows, traces, triage=triage_rep)
        trace_agg["trace_pass"] = "second_pass（延迟取自无埋点首轮）"
        print(f"[trace] 埋点轮 {trace_agg['traced_cases']} 题 + 负样本 "
              f"{trace_agg['negatives']['traced_cases']} 条｜耗时 {time.time() - t0:.1f}s"
              f"｜与主轮逐题一致：{trace_agg['invariance_vs_main_pass']['identical']}")

    # ── M-12：消融轮（ablation）─────────────────────────────────────────────
    ablation: dict | None = None
    diff_vs_baseline: dict = {
        "newly_passed": [], "newly_failed": [], "source": None, "cases_paired": 0,
        "note": "未提供基线/消融参照：空 diff 必须与配对题数 = 0 同时呈现",
    }
    if args.ablate_flag:
        flag = args.ablate_flag
        on_v = args.ablate_on or str(getattr(settings, flag, ""))
        if args.ablate_off:
            off_v = args.ablate_off
        else:
            cur = getattr(settings, flag, "")
            off_v = "false" if isinstance(cur, bool) else ("" if isinstance(cur, str) else "0")
        ref_rows, ref_src = rows, "本轮主轮"
        ref_cfg = {k: getattr(settings, k) for k in dir(settings)
                   if k.startswith("plot_") and not k.startswith("__")}
        if args.ablate_reference:
            rp = Path(args.ablate_reference)
            if not rp.is_file():
                print(f"[FAIL] 参照轮报告不存在：{rp}")
                return 2
            _ref = json.loads(rp.read_text(encoding="utf-8"))
            ref_rows = _ref.get("items") or []
            ref_cfg = (_ref.get("meta") or {}).get("config") or {}
            ref_src = str(rp)
        # **配置一致性硬校验**：配对检验只对"只差这一个开关"的两轮有意义。
        # 参照轮的该开关取值与 `--ablate-on` 不符时必须拒绝出结论——否则算出来的是
        # 两个不同配置的差，却被贴成该功能的贡献（"评测与生产漂移"的同类事故）。
        _ref_v = ref_cfg.get(flag, "<缺失>")
        if str(_ref_v).lower() != str(on_v).lower():
            print(f"[FAIL] 参照轮 {flag}={_ref_v!r} 与 --ablate-on={on_v!r} 不一致："
                  f"配对比较必须只差被消融的那一个开关")
            return 2
        print(f"\n[ablate] {flag}：全开={on_v!r}（参照 {ref_src}）→ 关闭={off_v!r}（本轮实跑）")
        t0 = time.time()
        with settings_override({flag: off_v}) as off_settings:
            off_reg = build_plot_registry(off_settings)
            off_retr = off_reg.get(args.character)
            if off_retr is None:
                print("[FAIL] 消融轮图谱未能加载")
                return 1
            off_rows = run_pass(off_retr, items, oracle, args.top, args.lexical_fallback,
                                args.inject_chars, quiet=args.quiet, tag="ablate")
            off_neg = evaluate_negatives(off_retr, args.top, args.lexical_fallback)
        print(f"[ablate] 关闭轮耗时 {time.time() - t0:.1f}s｜严格通过 "
              f"{sum(1 for r in off_rows if r['strict_pass'])}/{len(off_rows)}"
              f"｜负样本注入 {off_neg['negative_injection_total']} 块")
        pass_on = {str(r["id"]): bool(r["strict_pass"]) for r in ref_rows if r.get("id")}
        pass_off = {str(r["id"]): bool(r["strict_pass"]) for r in off_rows if r.get("id")}
        n_exec, basis, act_tot = cases_executed_for(ref_rows, flag)
        ablation = mcnemar_ablation(pass_on, pass_off, n_exec, flag,
                                    activation=act_tot, cases_executed_basis=basis)
        ablation["reference"] = ref_src
        ablation["on_value"], ablation["off_value"] = on_v, off_v
        ablation["off_pass"] = {
            "strict_pass": round(sum(pass_off.values()) / max(1, len(pass_off)), 4),
            "strict_pass_n": sum(pass_off.values()),
            "negative_injection_total": off_neg["negative_injection_total"],
            "negative_new_leaks": off_neg["new_leaks"],
        }
        diff_vs_baseline = {
            "newly_passed": [f["id"] for f in ablation["case_ids_flipped"]
                             if f["direction"] == "fail_to_pass"],
            "newly_failed": [f["id"] for f in ablation["case_ids_flipped"]
                             if f["direction"] == "pass_to_fail"],
            "source": "ablation.case_ids_flipped",
            "cases_paired": ablation["cases_total"],
            "note": f"配对参照 = {ref_src}（全开）；本轮 = {flag}={off_v!r}",
        }
    elif args.baseline:
        # 非消融的相对基线：diff 与 ablation 共用 compute_flipped 这一份口径
        bp = Path(args.baseline)
        if bp.is_file():
            b_items = json.loads(bp.read_text(encoding="utf-8")).get("items") or []
            pass_on = {str(r["id"]): bool(r.get("strict_pass")) for r in b_items if r.get("id")}
            pass_off = {str(r["id"]): bool(r["strict_pass"]) for r in rows if r.get("id")}
            flipped = compute_flipped(pass_on, pass_off)
            diff_vs_baseline = {
                "newly_passed": [f["id"] for f in flipped if f["direction"] == "fail_to_pass"],
                "newly_failed": [f["id"] for f in flipped if f["direction"] == "pass_to_fail"],
                "source": "compute_flipped(baseline.items, items)（与 ablation 同一实现）",
                "cases_paired": len(set(pass_on) & set(pass_off)),
                "baseline": str(bp),
            }

    print("\n==== 汇总（严格口径：并集子串覆盖全部证据组） ====")
    print(
        f"题量 {summary['cases']}｜严格通过 {summary['strict_pass_n']} "
        f"({summary['strict_pass']:.1%})｜天花板内 {summary['ceiling_pass']:.1%}"
    )
    if n_ov:
        pn = summary.get("primary_pass_n")
        pr = summary.get("primary_pass") or 0.0
        delta = (pn or 0) - summary["strict_pass_n"]
        print(
            f"主组口径 {pn}（{pr:.1%}）｜差值 +{delta} 题（+{delta / max(1, summary['cases']) * 100:.1f} pt）"
            f"｜依据 {OVERRIDES_PATH.name}（{n_ov} 题 override，题集未改动）"
        )
    print(
        f"块精度 {summary['chunk_precision']:.3f}｜答案块率 {summary['answer_chunk_rate']:.3f}"
        f"｜MRR {summary['mrr']:.3f}｜oracle recall {summary['recall']:.3f}"
        f"｜平均返回 {summary['avg_returned_chunks']} 块｜空结果 {summary['empty_rate']:.1%}"
    )
    if summary.get("inject_pass") is not None:
        print(
            f"★ 注入口径（产品真实口径，预算 {args.inject_chars} 字符，"
            f"实际装入均 {summary['injected_chars_avg']} 字符）："
            f"通过 {summary['inject_pass_n']} ({summary['inject_pass']:.1%})"
        )
    print(
        f"延迟 p50 {summary['latency_p50_ms']}ms｜p90 {summary['latency_p90_ms']}ms"
        f"｜p95 {summary['latency_p95_ms']}ms｜max {summary['latency_max_ms']}ms"
        f"｜检索总耗时 {eval_s:.1f}s"
    )
    print(f"路径归因 {summary['path_counts']}")
    print(
        f"负样本 {negatives['cases']} 条｜注入块合计 {negatives['negative_injection_total']}"
        f"｜零注入 {negatives['negative_clean']}"
    )
    for dim, buckets in dims_report.items():
        worst = sorted(buckets.items(), key=lambda kv: kv[1]["strict_pass"])[:3]
        print(f"  [{dim}] 最弱三档：" + "｜".join(
            f"{k} {v['strict_pass']:.0%}(n={v['cases']})" for k, v in worst
        ))
    for r in negatives["rows"]:
        if r["injected"]:
            print(f"  [负样本注入] {r['q']} → {r['injected']} 块 {r['paths']} "
                  f"样例：{r['samples'][:1]}")

    # ── M-12：trace_agg 打印（瀑布图口径；hit 与 kept **并列**，差值即被挤出量）──
    if trace_agg is not None:
        print(f"\n==== 六通道瀑布（跨题聚合；块级候选 hit_blk_avg 与 kept_avg 并列） ====")
        for c in trace_agg["channels"]:
            kr = "—" if c["kept_rate"] is None else f"{c['kept_rate']:.0%}"
            ha = c["hit_avg"] if c["hit_avg"] is not None else "—"
            hb = c["hit_blocks_avg"] if c["hit_blocks_avg"] is not None else "—"
            ka = (c["kept_in_final_avg"] if c["kept_in_final_avg"] is not None else "—")
            print(f"  {c['channel']:6s}[{c['unit']:5s}] 执行 {c['cases_executed']:3d}/{trace_agg['cases']}"
                  f"｜命中率 {'—' if c['hit_rate'] is None else format(c['hit_rate'], '.0%'):>4s}"
                  f"｜hit_avg {ha}"
                  f"｜hit_blk_avg {hb}"
                  f"｜kept_avg {ka}"
                  f"｜kept_rate {kr:>4s}"
                  f"｜skip {c['skip_reason_dist']}")
        # 通则：squeezed_total 必须与 graph_hit_total 成对呈现（否则"无稀释"与
        # "图通道没产出"在报告里长得一样）
        print(f"  桶 4 融合层稀释：squeezed_total {trace_agg['squeezed_total']}"
              f"（块量纲；图通道子集 squeezed_graph {trace_agg['squeezed_total_graph_only']}）"
              f"｜适用性前提 graph_hit_total {trace_agg['graph_hit_total']}"
              f"（＝图传播 {chan_of(trace_agg, '图传播', 'hit_blocks_total')}"
              f"+篇章路由 {chan_of(trace_agg, '篇章路由', 'hit_blocks_total')}）")
        mg = trace_agg["margin_histogram"]
        print(f"  实体链接 margin：触发 {mg['n_triggered']} 题｜有 margin {mg['n_with_margin']}"
              f"｜单候选（margin 无定义）{mg['n_single_candidate']}｜直方图 {mg['counts']}")
        print(f"  降级 fallback_counts {trace_agg['fallback_counts']}"
              f"（全 0 的适用性前提：cases={trace_agg['cases']}、"
              f"total_ms={trace_agg['total_ms']}）")
        print(f"  skip_reason 汇总 {trace_agg['skip_reason_dist']}")
        inv = trace_agg["invariance_vs_main_pass"]
        print(f"  埋点不变量：埋点轮与主轮逐题一致 {inv['identical']}"
              f"（差异 {inv['diff_cases']}/{inv['cases']}）")
        negt = trace_agg["negatives"]
        print(f"  负样本通道执行计数：seeds 合计 {negt['seeds_total_sum']}"
              f"｜图传播 hit {chan_of(negt, '图传播')}"
              f"｜语义向量 hit {chan_of(negt, '语义向量')}"
              f"｜skip {negt['skip_reason_dist']}")
    if bucket_rep is not None:
        print(f"\n==== 失分桶归因（§4e；失分 {bucket_rep['cases_failed']}/"
              f"{bucket_rep['cases_total']}） ====")
        print(f"  口径：{bucket_rep['source']}")
        for key, b in bucket_rep["section4e"].items():
            ov = b.get("trace_overlay_cases") or 0
            print(f"  {b['name']:12s} {b['cases']:3d} 题"
                  f"（占失分 {b['share_of_failed']:.0%}）"
                  f"｜§4e 期望：{b.get('expected_reference')}"
                  + (f"｜trace 症状 {ov} 题" if ov else ""))
        print(f"  triage 全部根因：{bucket_rep['triage_reasons']}")
        print(f"  §4e 未列的原因（数据/算法缺口，单列不并入未归因）："
              f"{bucket_rep['unmapped_reasons']}")
        print(f"  trace 症状计数（可重叠）：{bucket_rep['trace_signals']}")
    if ablation is not None:
        print(f"\n==== 消融配对（AC-1 唯一判据 = McNemar） ====")
        print(f"  开关 {ablation['feature_flag']}：全开 {ablation['on_value']!r} vs "
              f"关闭 {ablation['off_value']!r}｜配对题数 {ablation['cases_total']}")
        print(f"  m={ablation['m']}（b={ablation['b']} 通过→失败 / c={ablation['c']} 失败→通过）"
              f"｜delta_pt={ablation['delta_pt']}｜method={ablation['method']}"
              f"｜mcnemar_p={ablation['mcnemar_p']}")
        # §7.6.6：Δ 与 execution count 必须同期出现，否则 Δ≈0 会被误读成"功能无效"
        print(f"  执行计数 cases_executed={ablation['cases_executed']}"
              f"（{ablation['cases_executed_basis']}）")
        print(f"  快速判读档：{ablation['delta_pt_tier']}")
        print(f"  结论：{ablation['conclusion']}")

    report = {
        "event": EVAL_EVENT,
        "meta": {
            "tool": "scripts/eval_plot_rag.py",
            "standard": "rag_testset_300.json（证据组并集子串覆盖）+ 负样本零注入",
            "character": args.character,
            "argv": sys.argv,
            "top": args.top,
            "lexical_fallback": args.lexical_fallback,
            "sample": args.sample,
            "seed": args.seed,
            "limit": args.limit,
            "trace_enabled": bool(args.trace and not args.limit),
            "config": {
                k: getattr(settings, k)
                for k in dir(settings)
                if k.startswith("plot_") and not k.startswith("__")
            },
            "assets_sha256_head16": {
                "plot_graph": sha256_head(Path(settings.plot_graph_dir) / f"plot_graph_{args.character}.json"),
                "plot_corpus": sha256_head(Path(settings.plot_corpus_dir) / f"plot_corpus_{args.character}.json"),
                "testset": sha256_head(TESTSET_PATH),
            },
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_s": round(load_s + eval_s, 1),
        },
        "summary": summary,
        "by_dims": dims_report,
        "negatives": negatives,
        # M-12 四段（§7.6.4）。ablation 非消融运行**显式 null**（缺字段会被误读成 Δ=0）
        "trace_agg": trace_agg,
        "ablation": ablation,
        "diff_vs_baseline": diff_vs_baseline,
        "bucket_attribution": bucket_rep,
        # 通道装载状态（2026-09-17 新增）：语义通道静默降级必须可追溯。
        # 事故：embedding 回退 hashing 时语义索引被静默停用，inject 掉 6.7pt 无报错。
        "semantic_status": dict(getattr(registry, "semantic_status", {}) or {}),
        "semantic_loaded": getattr(retr, "semantic", None) is not None,
        "assets_sha256_head16": {
            "plot_graph": sha256_head(Path(settings.plot_graph_dir) / f"plot_graph_{args.character}.json"),
            "plot_corpus": sha256_head(Path(settings.plot_corpus_dir) / f"plot_corpus_{args.character}.json"),
            "testset": sha256_head(TESTSET_PATH),
        },
        "items": rows,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[save] {out}")

    rc = 0
    if args.baseline:
        bp = Path(args.baseline)
        if not bp.is_file():
            print(f"[FAIL] 基线报告不存在：{bp}")
            return 2
        base = json.loads(bp.read_text(encoding="utf-8"))
        b_meta = base.get("meta", {})
        if (b_meta.get("sample"), b_meta.get("seed"), b_meta.get("top")) != (
            args.sample, args.seed, args.top
        ) and not args.limit:
            print(
                f"[warn] 基线抽样参数不一致（基线 sample={b_meta.get('sample')} "
                f"seed={b_meta.get('seed')} top={b_meta.get('top')}）——对比仅供参考"
            )
        rows_cmp, regressed = compare_with_baseline(base, report, args.tolerance)
        print("\n==== 基线对比（+ 提升 / - 回退） ====")
        for r in rows_cmp:
            d = "—" if r["delta"] is None else f"{r['delta']:+.4f}"
            print(f"  {r['metric']:24s} {str(r['baseline']):>10} → {str(r['current']):>10}  {d}"
                  f"  {r.get('verdict', '')}")
        if regressed:
            print(f"[FAIL] 存在指标回退（容忍度 {args.tolerance}）")
            rc = 3

    if args.check_targets:
        ok, notes = check_targets(summary, negatives, base if args.baseline else None,
                                 ablation=ablation)
        print("\n==== 验收线自检 ====")
        print(f"  A1 延迟增量判据：p95 ≤ 同条件基线 + {TARGET_LATENCY_INCREMENT_MS}ms"
              f"｜本轮 p95 {summary['latency_p95_ms']}ms")
        print(f"  A5 负样本零注入：{negatives['negative_injection_total']} 块"
              f"（{negatives['cases']} 条：已知残余 {len(negatives.get('known_residual') or [])}"
              f" / 新增泄漏 {len(negatives.get('new_leaks') or [])}）")
        for note in notes:
            # 前缀按内容判定：合格项不该被打印成「未达标」（旧版无条件加前缀，
            # 会把 "[参考]" 与 "A1 达标" 这类正常信息误标为失败）
            tag = "[未达标]" if note.startswith(("A1 未达标", "A5 未达标")) else "[信息]"
            print(f"  {tag} {note}")
        if not ok and rc == 0:
            rc = 4
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
