# -*- coding: utf-8 -*-
"""并发批次收尾审计(只读,零网络)。

用法:
    python _audit_concurrent_batches.py            # 默认审计 >=247 的全部 batch
    python _audit_concurrent_batches.py 247 251    # 只审计指定号位

四项检查(对应交接文档的四类真实翻车):
  A 重复块   :同一 chunk key 被两个 batch 提交(并发号位串位)          —— **清单,不判失败**
             (实测:败方的 key 全输则其词典一个字不进图,不构成污染;
              真分裂须由 rebuild 后 `_adjudicate_splits.py` 的 resolve() 实测裁定)
  B 禁用裸名 :§3.1–3.4 已记录的「不可裸用」写法被当作 name 使用      —— **失败闸**
  C alias 撞名:声明的 alias 在 **cache 现值**里同时是某个 name,
             且 rebuild 后 resolve()=None → §4.11 落盘失效            —— **清单,不判失败**
             (修法是在**存活批**把被归并写法改写进规范名;
              老号位(≤246)的撞名系上游待修,登记在 §10)
  D 近义异体 :本轮新名之间、或新名与既有名互为子串且同为角色/组织(疑似同人裂分)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = int(sys.argv[1]) if len(sys.argv) > 1 else 247

# §3.1–3.4 + §0 各会话确立的「不可裸用」写法(作为 name 出现即报)
BANNED_NAMES = {
    "拉普拉斯", "拉普拉斯科算中心", "乌尔里希", "纸信圈儿", "福葛", "宽檐帽", "夏洛特",
    "卡邦克鲁", "凯拉", "淑女格蕾丝", "格蕾丝", "安德烈", "司机", "奇索斯镇", "玛丽",
    "镇民Ⅰ", "镇民Ⅱ", "爱丽丝", "镜子", "幽灵", "唱片", "努库泰澳", "传单",
    "神秘学唱片机", "芝诺军备学院", "洛杉矶·神秘学犯罪科", "洛杉矶·街道", "夜巡特遣",
    "夜巡局", "新巴别塔", "艾丽娅·波蒂埃", "梁家的强梁", "传送软盘", "数据卡",
    "基金会", "远东分部", "卡森先生", "熏香", "洛伦兹蝴蝶", "别斯米尔", "玛尔塔",
    "兀尔德", "德洛丝", "苦目糖", "莱瑟姆", "天使娜娜", "阿星", "泰瑞莎", "老板",
    "男子", "女子", "名字", "东西", "事件", "能量", "泡泡", "垃圾", "垃圾桶",
}
# 语境豁免:某些裸名只在**特定语义**下被禁(§3.4 记的是「公司/机构」义),
# 而它作为既有的**角色** canonical 节点复用是正确做法。列在此处 → 不报 B,
# 改记入 adjudicated 供人工复核。理由必须写清,否则等于削弱闸口。
BANNED_TYPES_OK = {
    "\u65b0\u5df4\u522b\u5854": {"\u89d2\u8272"},   # \u65e2\u6709\u8282\u70b9\u5373\u89d2\u8272\u300c\u5c55\u793a\u65b0\u57f9\u80b2\u9b54\u7cbe\u8005\u300d;\u7981\u7684\u662f\u300c\u9b54\u7cbe\u516c\u53f8\u300d\u4e49(\u2192\u65b0\u5df4\u522b\u5854\u9b54\u7cbe\u516c\u53f8)
    "\u591c\u5de1\u7279\u9063": {"\u89d2\u8272"},   # \u65e2\u6709\u8282\u70b9\u662f\u89d2\u8272(\u65e7\u90e8\u6765\u6e90);\u7981\u7684\u662f\u673a\u6784\u4e49(\u2192\u591c\u5de1\u7279\u9063\u7ba1\u7406\u5c40)
}
HAN = re.compile(r"[\u4e00-\u9fff]")

# 按篇豁免:某裸名在**特定版本内**是「复用既有同源节点」的正确做法,不是污染。
# 依据交接文档 §10「第 18 会话复核」③:图谱 `镜子` 节点 = mainline__106「自由联想之喻」,
# appendix 022 与 106/107 同属维也纳精神分析篇、同一只口袋之镜,拆限定名反而**制造**分裂;
# §429 那行 `镜子`(→`镜中幽灵`)只适用于该表所属那一篇,不得外推。白名单外的裸用仍判失败。
BANNED_DOC_OK = {
    "镜子": ("mainline__106_", "mainline__107_", "appendix_unbound__022_"),
    # `卡森先生`(§3.4 batch240 裁定「写 `苏芙比的管家`」)—— **该裁定的前提已被实测推翻**：
    # ① 全语料 27 块以 `卡森先生` 为 name，desc **无一例外**指向苏芙比家的管家
    #    (mainline__101/102/108、anecdote__1913 淑女的守则、activity__305101、
    #     appendix_unbound__020/024) → 同一个所指，`苏芙比的管家` 只是描述性写法；
    # ② 当年担心的「并入他章管家组(`邓肯先生`)」**没有发生**：`mainline__108 22.0.0`
    #    同一块里 `卡森先生` 与 `邓肯先生` **并现**(判据①反证二人不同)，且
    #    `_diag_weld_group.py` 报两组各 size=1；灰机 `邓肯先生` 页亦证实他是独立的
    #    尤提姆角色(热情豪爽、常端酒杯)，不是管家。
    # ③ 落盘实测：`卡森先生`/`苏芙比的管家`/`庄园管家`/`卡森管家` **四条写法全部
    #    resolve() 到同一节点**，`邓肯先生` 独立 → 归并已完成且语义正确。
    # 故按篇豁免(保留 name=卡森先生)，**白名单外的篇章裸用仍判失败**。
    "卡森先生": ("mainline__101_", "mainline__102_", "mainline__108_",
                 "anecdote__1913_", "activity__305101_",
                 "appendix_unbound__020_", "appendix_unbound__024_"),
}


def load_slots():
    out = {}
    for p in ROOT.glob("_agent_batch*.json"):
        m = re.fullmatch(r"_agent_batch(\d+)b?\.json", p.name)
        if m and int(m.group(1)) >= BASE:
            out[p.name] = json.loads(p.read_text(encoding="utf-8"))
    return out


def main() -> int:
    slots = load_slots()
    if not slots:
        print(f"没有 >= batch{BASE} 的产物")
        return 0

    # 全量并集(所有 batch + graph),用于 C/D 的「既有名」参照
    all_names = {}          # name -> set(出处文件)
    alias_decl = {}         # alias -> set(name)
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        for k, blk in data.items():
            for e in blk.get("entities", []):
                n = e.get("name")
                if n:
                    all_names.setdefault(n, set()).add(p.name)
                for a in (e.get("aliases") or []):
                    alias_decl.setdefault(a, set()).add(n)

    problems = []
    catalogue = []        # A/C:清单(不判失败),交 rebuild 后 resolve() 与 §10 裁定
    adjudicated = []
    # cache 现值里的 name(= 真正进图的那批),以及 rebuild 后的 resolve 实况
    cache_names = set()
    for p in (ROOT / "cache").rglob("*.json"):
        raw = (json.loads(p.read_text(encoding="utf-8")) or {}).get("raw") or {}
        for e in raw.get("entities") or []:
            if e.get("name"):
                cache_names.add(e["name"])
    resolve = None
    gp = ROOT / "graph.json"
    if gp.exists():
        try:
            sys.path.insert(0, str(ROOT.parent.parent / "src"))
            from compendium_rag.graph_store import GraphStore
            gg = GraphStore.load(gp)
            resolve = gg.resolve
        except Exception:                       # 未 rebuild 时退化为仅看 cache
            resolve = None
    # key → chunk_id(来自本会话各号位 dump),用于 §3.x 的**按篇豁免**;取不到即按最严处理
    k2cid = {}
    for dp in ROOT.glob("_dump*.txt"):
        for ln in dp.read_text(encoding="utf-8").splitlines():
            try:
                o = json.loads(ln)
                k2cid[o["key"]] = o["chunk_id"]
            except Exception:
                continue
    # A 重复块
    seen = {}
    for fn, data in sorted(slots.items()):
        for k in data:
            if k in seen and seen[k] != fn:
                catalogue.append(f"A 重复块 {k}: {seen[k]} 与 {fn}")
            seen.setdefault(k, fn)

    for fn, data in sorted(slots.items()):
        for k, blk in data.items():
            for e in blk.get("entities", []):
                n, t = e.get("name", ""), e.get("type", "")
                # B 禁用裸名
                if n in BANNED_NAMES:
                    if t in BANNED_TYPES_OK.get(n, set()):
                        adjudicated.append(f"B豁免 {fn}/{k}: name={n} type={t}")
                    elif any(k2cid.get(k, "").startswith(p)
                             for p in BANNED_DOC_OK.get(n, ())):
                        adjudicated.append(
                            f"B按篇豁免 {fn}/{k}: name={n} 篇={k2cid.get(k)}")
                    else:
                        problems.append(f"B 禁用裸名 {fn}/{k}: name={n} type={t}")
                # C alias 撞名:只在 alias **确实进不了图**时登记(§4.11 落盘失效)
                for a in (e.get("aliases") or []):
                    if a in cache_names and a != n and (resolve is None
                                                        or resolve(a) is None):
                        srcs = sorted(all_names[a])
                        catalogue.append(
                            f"C alias落盘失效 {fn}/{k}: {n} 声明 alias={a},"
                            f" 而 {a} 在 cache 里又是 name(见 {srcs[:3]}{'…' if len(srcs)>3 else ''})")
                # D 近义异体(新名互为子串,同类别)
                for m, files in all_names.items():
                    if m == n or not (len(n) >= 3 and len(m) >= 3):
                        continue
                    if n in m or m in n:
                        others = {f for f in files} - {fn}
                        if others and (n[:1] == m[:1]):
                            pass  # 交由人工:下方只汇总统计
    # D 汇总:本轮各号位的新名(只在本号位出现),供人工比对近义
    fresh = {}
    for fn, data in sorted(slots.items()):
        for k, blk in data.items():
            for e in blk.get("entities", []):
                n = e.get("name", "")
                if all_names.get(n, set()) <= {fn} and n not in fresh:
                    fresh[n] = (fn, e.get("type", ""))
    pairs = []
    ns = list(fresh)
    for i, a in enumerate(ns):
        for b in ns[i + 1:]:
            if (a in b or b in a) and fresh[a][1] == fresh[b][1]:
                pairs.append((a, b, fresh[a][0], fresh[b][0]))

    tot_blocks = sum(len(d) for d in slots.values())
    print(f"审计号位 {len(slots)} 个文件 / {tot_blocks} 块｜并集 name {len(all_names)}")
    print(f"本轮全新名 {len(fresh)} 个")
    if pairs:
        print("D 疑似近义异体(互为子串且同 type,需人工判定同人/分人):")
        for a, b, fa, fb in pairs:
            print(f"  - {a}({fa}) ↔ {b}({fb})")
    if catalogue:
        na = sum(1 for c in catalogue if c.startswith("A"))
        nc = len(catalogue) - na
        print(f"\n⚠ 清单 {len(catalogue)} 条(A 重复块 {na} / C alias落盘失效 {nc})"
              f"—— **不判失败**:A 由 rebuild 后 `_adjudicate_splits.py` 按 resolve() 裁定,"
              f"  C 需在存活批把写法改写进规范名(老号位撞名登记 §10 上游待修)")
        for c in catalogue[:200]:
            print("  - " + c)
    if problems:
        print(f"\n✗ 发现 {len(problems)} 处问题：")
        for p in problems[:200]:
            print("  - " + p)
        return 1
    if adjudicated:
        print(f"B 语境豁免(已裁定,不计为问题) {len(adjudicated)} 处:")
        for a in sorted(set(adjudicated)):
            print("  - " + a)
    print("\n✓ B 禁用裸名通过(A/C 见上方清单)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
