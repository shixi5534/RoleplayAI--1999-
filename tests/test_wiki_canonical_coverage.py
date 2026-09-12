"""灰机 wiki 正典覆盖率回归测试。

用灰机 wiki 查证得到的权威设定（deliverables/wiki-r1999-relation-reference-20260909.md
第 2.1 节阵营关系、第 3 节核心人物关系）反向检验知识图谱。

基线（2026-09-09 首次实测）：
    plot  57.9% (11/19)
    lore  68.4% (13/19)
    并集  89.5% (17/19)

红线：覆盖率不得低于基线。缺口允许存在，但不得扩大。
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from verify_wiki_canonical import (  # noqa: E402
    CANON_RELATIONS,
    LORE_PATH,
    PLOT_PATH,
    audit_one,
    check_attr_error,
    load_graph,
)

# —— 基线（不得回退）——
# ⚠️ 2026-09-11 下调 plot 1 条（11→10）、并集 1 条（17→16），**待 N1 后复核**。
# 这不是抽取质量回退，而是图谱首次「干净重建」的必然结果：
# 重建前 plot 图里躺着 269 条 relation=="待审核" 的边，是早期版本遗留的未核验关系。
# 而 canonicalize_relation("待审核") 恒返回 None（该词不在 77 条受控词表内，只是
# REVIEW_SENTINEL 哨兵），因此**任何一次干净重建都会把它们全部清除**——总结 B7 已预判
# （「边数 4 035 降至约 3 766，这是预期而非回归」）。
# 被扣掉的是 `无名者 —隶属— 圣洛夫基金会`：它原先只以「圣洛夫基金会 —待审核→ 无名者」
# 的形态存在，本就不该计为正典命中。
# 恢复路径：N1 云端抽取产出明确的「隶属」边后，基线应调回 11 / 17。
BASELINE = {"plot": 10, "lore": 13, "union": 16}


@pytest.fixture(scope="module")
def graphs():
    return {
        "plot": load_graph(PLOT_PATH) if os.path.exists(PLOT_PATH) else None,
        "lore": load_graph(LORE_PATH) if os.path.exists(LORE_PATH) else None,
    }


@pytest.fixture(scope="module")
def results(graphs):
    return {
        name: (audit_one(name, g) if g else [])
        for name, g in graphs.items()
    }


def _hits(res, confs=("高", "中")):
    scored = [r for r in res if r["confidence"] in confs]
    return sum(1 for r in scored if r["status"] == "HIT"), len(scored)


def test_plot_coverage_no_regression(results):
    assert results["plot"], "plot 图谱不可用"
    hit, total = _hits(results["plot"])
    assert hit >= BASELINE["plot"], (
        f"plot 正典覆盖率回退：{hit}/{total}，基线 {BASELINE['plot']}/{total}"
    )


def test_lore_coverage_no_regression(results):
    assert results["lore"], "lore 图谱不可用"
    hit, total = _hits(results["lore"])
    assert hit >= BASELINE["lore"], (
        f"lore 正典覆盖率回退：{hit}/{total}，基线 {BASELINE['lore']}/{total}"
    )


def test_union_coverage_no_regression(results):
    """混合检索口径：两图谱任一命中即算覆盖"""
    plot_res, lore_res = results["plot"], results["lore"]
    assert plot_res and lore_res
    scored = [p for p, l in zip(plot_res, lore_res) if p["confidence"] in ("高", "中")]
    union_hit = sum(
        1 for p, l in zip(plot_res, lore_res)
        if p["confidence"] in ("高", "中")
        and (p["status"] == "HIT" or l["status"] == "HIT")
    )
    assert union_hit >= BASELINE["union"], (
        f"并集正典覆盖率回退：{union_hit}/{len(scored)}，基线 {BASELINE['union']}/{len(scored)}"
    )


@pytest.mark.parametrize("gname", ["plot", "lore"])
def test_no_wrong_afflatus(graphs, gname):
    """属性纠错：无名者为「岩」灵感，图谱中不得出现「智」属性边"""
    g = graphs[gname]
    if g is None:
        pytest.skip(f"{gname} 图谱不存在")
    bad = check_attr_error(gname, g)
    assert not bad, f"{gname} 图谱存在错误的属性边：{bad}"


# —— 已知缺口白名单 ——
# 高置信度正典事实但两图谱均未覆盖。登记在此处是为了「可见」而非「掩盖」：
# 缺口一旦被修复，本测试会立即失败并提示从白名单移除。
#
# 缺口分类（2026-09-09 用户确认）：
#   corpus_pending — 游戏剧情尚有早期部分未导入语料库，该部分设定占比高。
#     典型例子：勿忘我个体在 plot 层无实体属预期行为（lore 层设定已覆盖其「隶属重塑之手」），
#     不是抽取/治理缺陷，不应计入图谱质量扣分。
KNOWN_GAPS = {
    ("芝诺军备学院", "隶属", "鸽子屋"):
        "corpus_pending：两图谱均缺该边；鸽子屋→芝诺指挥链属早期设定剧情，语料未导入（wiki 置信度 高）",
    ("无名者", "隶属", "圣洛夫基金会"):
        "review_purged：2026-09-11 图谱干净重建清除了 269 条 relation=='待审核' 的边"
        "（canonicalize_relation 对该词恒返回 None）。本条原先仅以"
        "「圣洛夫基金会 —待审核→ 无名者」形态存在，属未核验关系，不计正典命中。"
        "待 N1 云端抽取产出明确「隶属」边后应移除本缺口并调回基线 11/17",
}


def test_high_confidence_core_facts_present(results):
    """最高置信度的核心正典事实：至少在一个图谱中命中，或已在缺口白名单登记"""
    plot_core = {r["a"] + r["b"]: r for r in results["plot"] if r["confidence"] == "高"}
    for r in (x for x in results["lore"] if x["confidence"] == "高"):
        key = r["a"] + r["b"]
        covered = r["status"] == "HIT" or plot_core.get(key, {}).get("status") == "HIT"
        gap_key = (r["a"], r["relation"], r["b"])
        if covered:
            assert gap_key not in KNOWN_GAPS, (
                f"缺口已修复，请从 KNOWN_GAPS 移除：{gap_key}"
            )
        else:
            assert gap_key in KNOWN_GAPS, (
                f"新增未登记的正典缺口：{r['a']} —{r['relation']}— {r['b']}"
            )


def test_known_gaps_not_stale():
    """白名单不得无限膨胀：缺口数不得增加"""
    # 基线 1 → 2（2026-09-11）：新增的一条是「待审核」边清理的连带结果，
    # 非新的覆盖退化，已在 KNOWN_GAPS 内注明 review_purged 与 N1 恢复路径。
    assert len(KNOWN_GAPS) <= 2, (
        f"已知缺口数增加到 {len(KNOWN_GAPS)}（基线 2），请核查是否引入新的正典覆盖退化"
    )


def test_canon_registry_not_shrunk():
    """正典事实表本身不得被删减（防止靠删用例刷通过率）"""
    assert len(CANON_RELATIONS) >= 20, (
        f"正典事实表被删减：{len(CANON_RELATIONS)} 条，应 >= 20"
    )
