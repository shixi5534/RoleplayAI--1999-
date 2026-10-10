# -*- coding: utf-8 -*-
"""P6 · L4.4 世界观互斥 —— **可复用的重审装配器**（R9 臂）。

## 为什么需要它
L4.4 gate（unity ≥ 0.95，当前读数 **0.9425 FAIL**）的统计量**不来自图**，而来自一份
冻结的子代理评审缓存：

    scripts/audit_l4.py:908-919   # mode_worldview 尾部
        unity = round(1 - n_excl / max(1, n_judged), 4)
        n_excl   = 有 mutually_exclusive 或 verdict=="mutually_exclusive" 的条数
        n_insuff = verdict=="insufficient" 的条数
        n_judged = len(rv) - n_insuff

也就是说：**光删边、不重出评审，读数一动不动**。而 `mode_worldview` 又**没有
`--prep` 分支**（`--prep` 只存在于 privacy / multiscene，见 :776 与 privacy 分支），
重审输入只能像 L4.5 臂那样手工装配。

本脚本就是那个装配器：把**同一批 90 个概念**放到**任意一张图**上重新装配成盲评批次，
使下一次（修边后）的 unity 与 0.9425 是**同一把尺子量出来的**。

## 与 audit_l4.py 的同口径保证（逐字复刻，勿"顺手优化"）
1. 概念集合：**以既有评审 `l4_worldview_review.json` 里出现的 90 个 concept 为准**，
   既不新增也不删除——否则 n_judged 分母变了，读数不可比。
2. 定义边口径（`audit_l4.py:886-900`）：
   - 遍历 `graph["edges"]` 的**原始顺序**，取 `e.eid in (ed.src, ed.dst)` 的边；
   - `canon(relation) ∈ ("是","象征","包含","隶属","影响")` 才要；
   - `direction = "out" if ed.src == e.eid else "in"`；`other` 取对端**实体 name**；
   - `evidence` 截断到 `[:60]`；整行列表最后 `rows[:12]`。
3. `canon` 口径（`audit_l4.py:877-879`，**注意它与 `_canon_of` 不是同一个函数**）：
   优先查 sidecar `data/knowledge/_audit/predicate_grouping_v1.json` 的 `mapping`，
   命中即用 `v["canonical"]`；未命中回退 `classify_relation(rel)[0]`。
   `_canon_of`（:327-334）用的是 `if v is not None: return v.get("canonical")`，
   在 sidecar 值为空 dict 时与 `canon` 结果不同——此处**按 mode_worldview 的 inline
   版本复刻**，不 import `_canon_of`。

用法::

    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \
      scripts/compendium_rag_p6_l44_review_prep.py \
      --graph data/compendium_rag/graph.json \
      --sha16 329671bba0988c68 \
      --out   data/knowledge/_audit/l4_worldview_r9 \
      --note  "r9 worldview re-review arm"

硬门：`--graph` 的 sha16（文件字节 sha256 取前 16 位小写，同
`audit_common.sha16_file` / `compendium_rag_p6_l45_arm_prep.py`）必须等于 `--sha16`，
否则 `[FATAL]` + `sys.exit(2)` 且**一个文件都不写**。

红线：只读图 + 只读既有评审；只写 `--out` 目录；不跑 cli rebuild/extract；
不跑 audit_l4.py；不联网；不调 LLM；**不用 rmtree/unlink**（守门测试
``tests/compendium_rag/test_independence.py::test_scripts_never_target_real_data_dir``
要求 ``scripts/compendium_rag_*.py`` 出现 rmtree/unlink 时必须把 data_dir 钉到临时目录）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

AUDIT = ROOT / "data" / "knowledge" / "_audit"
REVIEW = AUDIT / "l4_worldview_review.json"
SIDECAR = AUDIT / "predicate_grouping_v1.json"

BATCH = 15
EDGE_CAP = 12
EVID_CAP = 60
DEF_CANONS = ("是", "象征", "包含", "隶属", "影响")
GATE_NAME = "L4.4 世界观定义统一性"
GATE_THRESHOLD = 0.95

INSTRUCTIONS = """\
# L4.4 世界观定义互斥一致性评分说明（重新盲评 · 审查子代理）

> 本目录是一次**重新盲评**的输入。判定口径（verdict 词汇、字段名、判定标准）与历史上
> 跑出 `unity=0.9425` 的那一次**逐字一致**；唯一差别是 `definition_edges` 取自**新图**
> （图指纹 `%(sha16)s`）。两次读数之差才是"修边"的效果，所以**不要改口径**。
>
> **禁止**参考其它臂目录下的任何旧文件（见文末禁令）。

你是**独立审查员**。任务：对每一个概念，判断**知识图谱给它的描述（desc）与它的定义边之间
是否自相矛盾**。你不需要懂这款游戏，判定只依据手上给到的输入。

## 输入
`%(outdir)s/wv_bNN.json`（NN 与你的批号一致）：
```json
{"schema":"audit.l4_worldview_review_input/v1","batch":"b01",
 "items":[{"concept":"…","type":"概念","desc":"…","aliases":["…"],
           "definition_edges":[{"dir":"out","relation":"象征","canonical":"象征",
                                "counterpart":"启示","evidence":"原文短句",
                                "chunk_id":"…"}]}]}
```
- `desc`：图谱里该概念的描述（可能很短，本身也可能就是错的——这正是要查的）。
- `aliases`：该概念的别名清单（判定"是"的对象是否只是同一事物的另一种叫法时可用）。
- `definition_edges`：图谱从全库抽出的、能把 `concept` **定义成什么**的关系边。口径：
  只保留 `canonical ∈ {是, 象征, 包含, 隶属, 影响}` 的边，按图内边序取前 12 条。
  - `dir="out"` 读作 `concept --relation--> counterpart`；
  - `dir="in"`  读作 `counterpart --relation--> concept`。
  - **数组的 0 基下标就是 `conflicting_edges[*].index` 要填的序号。**

## 判定标准（verdict）
把每个概念判成三者**之一**：
- **`consistent`**：desc 与定义边自洽，没有互斥定义。
- **`mutually_exclusive`**：同一概念被**同时定义成 A 与 非A**，或同一个 counterpart
  既被说成"就是它"、又被说成"是另一个 / 另一天 / 另一件东西"。典型形态：
  - `X --是--> A` 与 `X --是--> B`，而证据语境里 A、B 明确不是一回事；
  - `A --是--> X` 与 `A --是--> Y`，把 X、Y 当成同一件事，但原文说 X 是 Y 的次日；
  - 同一个 counterpart 上 `隶属` 与 `象征` 并存且语义冲突。
  **不构成互斥**（不要判 mutually_exclusive）：单边的 `隶属`/`象征`；`是` 的两端互为别名；
  几条边彼此独立、不指涉同一对象；只是"关系稀疏/看起来不够定义"。
- **`insufficient`**：**给到的定义边不足以判定**该概念（例如只有单边且证据是旁白/失败台词、
  与概念的定义无关；`definition_edges` 为空时一律判此值）。
  判 `insufficient` 的条**会移出判分母**——所以只在边确实不定义该概念时使用，
  不要用它来回避没把握的判断。

## 输出
写到 `%(outdir)s/wv_bNN_review.json`（NN 与输入批号一致）：
```json
{"schema":"audit.l4_worldview_review/v1","batch":"b01",
 "reviews":[{"concept":"…",
             "verdict":"consistent",
             "conflicting_edges":[{"index":2,"why":"≤30 字"}],
             "constraint_risk":0.1,
             "notes":"≤40 字判据"}]}
```
- `verdict` **必须逐字**取 `consistent` / `mutually_exclusive` / `insufficient` 三者之一
  （大小写与下划线都要一样），否则本轮 `unity` 复算不出来；
- `conflicting_edges`：只有 `mutually_exclusive` 时非空，`index` 为上面 `definition_edges`
  的 **0 基下标**（历史臂写作 `idx`，也接受），`why` ≤30 字；其余 verdict 写 `[]`；
- `constraint_risk`：0.0~1.0 浮点，你对"该概念后续会造成世界观冲突"的风险估计
  （**不参与 unity 计算**，只做留痕）；
- `notes`：≤40 字判据；
- 一条 concept 都不能少；**每评完 5 条立刻用当时已有的全部结果覆盖落一次盘**，防中断丢失；
- 收尾自查：`reviews[*].concept` 集合 == 输入 `items[*].concept` 集合（本臂共 90 条，
  拆成 6 批、每批 15 条）。

## 复算口径（写给你自查，不要改）
设你的输出为 R：
- `n_insuff = |{r ∈ R : r.verdict == "insufficient"}|`
- `n_excl  = |{r ∈ R : r.verdict == "mutually_exclusive"（或 r.mutually_exclusive 为真）}|`
- `n_judged = |R| - n_insuff`
- `unity = round(1 - n_excl / max(1, n_judged), 4)`，gate = `unity ≥ 0.95`

即：**`insufficient` 的条移出分母；每一条 `mutually_exclusive` 扣 1/n_judged。**

## 禁令
- **禁止**读取仓库里的其它任何文件（图谱产物、评测集、gold、别人的 review 都不许看）；
  只能打开本说明文件和你自己的输入批次文件。
- **特别禁止**打开：`data/knowledge/_audit/l4_worldview_review.json`（历史判分，
  它是本轮要对照的基线）、本目录下的 `arm_map.json` 与 `baseline_unity.json`
  （含基线读数，属泄漏）、以及 `../l4_multiscene*/`、`../l4_privacy*/` 等其它臂下的任何
  `*_review.json`。看了就不再是盲评。
- 判分要敢给低分，也要敢给满分：把"看起来合理"当成"有依据"是放水，
  把"边太少"当成"互斥"是口径错位。
"""


def sha16(path: Path) -> str:
    """文件字节 sha256 取前 16 位小写（口径同 audit_common.sha16_file）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def load_canon():
    """复刻 audit_l4.py:872-879 的 canon 口径（inline 版，非 _canon_of）。"""
    import audit_l4 as L4  # noqa: E402  （scripts/ 已在 sys.path 上）

    _CANON, _G, classify_relation = L4._vocab()
    smap = json.loads(SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if SIDECAR.exists() else {}

    def canon(rel):
        v = smap.get(rel)
        return v["canonical"] if v else classify_relation(rel)[0]

    return canon


def build(graph_path: Path, expect_sha16: str, out_dir: Path, note: str) -> int:
    # ── 硬门：先验图指纹，任何写盘动作都在其之后 ──
    if not graph_path.exists():
        print(f"[FATAL] 缺图 {graph_path}")
        return 2
    got = sha16(graph_path)
    if got != expect_sha16:
        print(f"[FATAL] graph sha16 不符：期望 {expect_sha16}，实际 {got}"
              f"（{graph_path}）")
        return 2
    if not REVIEW.exists():
        print(f"[FATAL] 缺既有评审 {REVIEW}（概念集合以它为准）")
        return 2

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    ent = {e["eid"]: e for e in graph["entities"]}
    edges = graph["edges"]

    # 概念集合 = 既有评审的 90 个 concept，顺序也照抄（保证批次切分可复现）
    rv = json.loads(REVIEW.read_text(encoding="utf-8"))["reviews"]
    concepts = [r["concept"] for r in rv]
    if len(set(concepts)) != len(concepts):
        print("[FATAL] 既有评审 concept 有重复，无法一一对应")
        return 2

    # 无向 degree（口径同 audit_common.build_adjacency/degrees），仅用于体检告警
    adj: dict[str, set] = {eid: set() for eid in ent}
    for e in edges:
        if e["src"] in adj and e["dst"] in adj:
            adj[e["src"]].add(e["dst"])
            adj[e["dst"]].add(e["src"])
    deg = {k: len(v) for k, v in adj.items()}

    canon = load_canon()
    by_name = {}
    for eid, e in ent.items():
        by_name.setdefault(e["name"], []).append(eid)

    warn: list[str] = []
    items = []
    for name in concepts:
        eids = by_name.get(name, [])
        if len(eids) != 1:
            warn.append(f"{name}: 新图同名实体 {len(eids)} 个，取第一个")
        if not eids:
            print(f"[FATAL] 新图缺概念实体 {name}")
            return 2
        eid = eids[0]
        e = ent[eid]
        if e.get("type") != "概念":
            warn.append(f"{name}: type={e.get('type')}（原口径只送 概念）")
        if deg.get(eid, 0) < 3:
            warn.append(f"{name}: degree={deg.get(eid, 0)}<3（原口径会剔除）")

        rows = []
        for ed in edges:                     # audit_l4.py:887 逐边、原始顺序
            if eid not in (ed["src"], ed["dst"]):
                continue
            c = canon(ed["relation"])        # audit_l4.py:890
            if c not in DEF_CANONS:          # audit_l4.py:891
                continue
            other = ed["dst"] if ed["src"] == eid else ed["src"]
            oe = ent.get(other)
            cids = ed.get("chunk_ids") or []
            rows.append({
                "dir": "out" if ed["src"] == eid else "in",   # :895
                "relation": ed["relation"],
                "canonical": c,
                "counterpart": oe["name"] if oe else other,   # :896
                "evidence": (ed.get("evidence") or "")[:EVID_CAP],  # :897
                "chunk_id": cids[0] if cids else None,
            })
        items.append({
            "concept": name,
            "type": e.get("type"),
            "desc": e.get("desc"),
            "aliases": list(e.get("aliases") or []),
            "definition_edges": rows[:EDGE_CAP],              # :900 rows[:12]
        })

    batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]

    # 基线快照：**只从冻结评审重算**，不回写任何冻结文件
    n_excl = sum(1 for r in rv if r.get("mutually_exclusive")
                 or r.get("verdict") == "mutually_exclusive")
    n_insuff = sum(1 for r in rv if r.get("verdict") == "insufficient")
    n_judged = len(rv) - n_insuff
    unity = round(1 - n_excl / max(1, n_judged), 4)
    baseline = {
        "schema": "audit.l4_worldview_baseline_unity/v1",
        "source": REVIEW.relative_to(ROOT).as_posix(),
        "n_total": len(rv),
        "n_excl": n_excl,
        "n_insuff": n_insuff,
        "n_judged": n_judged,
        "unity": unity,
        "gate": GATE_NAME,
        "threshold": GATE_THRESHOLD,
        "verdict": "PASS" if unity >= GATE_THRESHOLD else "FAIL",
        "note": ("从既有冻结评审重算的只读基线（口径 audit_l4.py:912-916）；"
                 "未写回任何冻结文件"),
    }

    # ── 上面全部成功，下面才开始写盘 ──
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, batch in enumerate(batches, 1):
        (out_dir / f"wv_b{i:02d}.json").write_text(json.dumps({
            "schema": "audit.l4_worldview_review_input/v1",
            "task": "逐概念判定其 desc 与 definition_edges 是否互斥/自相矛盾",
            "batch": f"b{i:02d}",
            "items": batch,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    rel_out = out_dir.relative_to(ROOT).as_posix()
    (out_dir / "INSTRUCTIONS.md").write_text(
        INSTRUCTIONS % {"sha16": got, "outdir": rel_out}, encoding="utf-8")

    (out_dir / "arm_map.json").write_text(json.dumps({
        "schema": "audit.l4_worldview_review_arm/v1",
        "graph": graph_path.relative_to(ROOT).as_posix(),
        "graph_sha16": got,
        "note": note,
        "n_concepts": len(items),
        "batch_size": BATCH,
        "batches": len(batches),
        "concept_order_source": REVIEW.relative_to(ROOT).as_posix(),
        "def_canons": list(DEF_CANONS),
        "edge_cap": EDGE_CAP,
        "review_output_glob": "wv_b*_review.json",
        "reviewer_must_not_read": ["arm_map.json", "baseline_unity.json"],
        "batch_concepts": {f"b{i:02d}": [x["concept"] for x in b]
                           for i, b in enumerate(batches, 1)},
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    (out_dir / "baseline_unity.json").write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 自检 ──
    print(f"[ok] graph sha16={got} ({graph_path.relative_to(ROOT).as_posix()})")
    print(f"[ok] concepts={len(items)} batches={len(batches)}")
    print(f"[ok] baseline unity={unity} "
          f"(n_total={baseline['n_total']} n_excl={n_excl} "
          f"n_insuff={n_insuff} n_judged={n_judged})")
    for i, b in enumerate(batches, 1):
        print(f"[ok] wv_b{i:02d}.json items={len(b)}")
    print(f"[ok] arm_map.json + baseline_unity.json + INSTRUCTIONS.md -> {rel_out}")
    for w in warn:
        print(f"[warn] {w}")
    print("[done]")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", required=True)
    ap.add_argument("--sha16", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    return build(ROOT / a.graph, a.sha16, ROOT / a.out, a.note)


if __name__ == "__main__":
    sys.exit(main())
