"""P9 · 子代理 fan-out 治理：期望批次清单 + qid-set 完成校验 + 存活/越界判定。

三个子命令：
    plan    从**输入批次目录**枚举期望批次，落 manifest（声明写面 + 冻结保护快照）
    check   按 manifest 逐批查产物，以 **qid 集合相等** 判完成；双信号分 slow / 死
    guard   重算保护路径摘要，揪出写在声明写面之外的越界改动

为什么遍历 manifest 而不是 glob 产物：glob 会让「整个不存在的批次」静默消失。
P8 实案 —— 检查器报「30 批齐、3 批待办」，实际有 2 批根本没落过盘。
为什么判生死要两个信号：单看 mtime 冻结会把慢代理判死，重派的那个和复活的原代理
会抢同一个输出文件（jdg_b29：原代理 409 s 后自己回来了，已是 last-writer）。

只写 `data/compendium_rag/reports/p9_fanout/`，不碰 data 下其他路径；
无 rmtree / unlink（守门测试 tests/compendium_rag/test_independence.py:265）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag" / "reports" / "p9_fanout"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"

# 锚点出处 scripts/audit_common.py:47 V9P5_GRAPH_SHA16（r11，27110 边 / 7033 实体）。
# 与 P8 影子评测脚本同款：本地复制常量，图指纹漂移即中止且不写文件。
EXPECTED_SHA = "911bb538160db80e"

SCHEMA_MANIFEST = "compendium_rag.p9_fanout_manifest/v1"
SCHEMA_CHECK = "compendium_rag.p9_fanout_check/v1"


def sha16_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def _rel(p: Path) -> str:
    """相对 ROOT 的展示路径；落在 ROOT 外就退回绝对路径（别炸）。"""
    try:
        return str(p.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p.resolve()).replace("\\", "/")


def _is_blank(row: dict, qid_key: str) -> bool:
    """除 qid 外整条记录全空 —— 抓到「写了题号但正文是 null」的假完成。"""
    return all(k == qid_key or v in (None, "", [], {}) for k, v in row.items())


def manifest_path(tag: str) -> Path:
    return R / f"{tag}.manifest.json"


def beat_path(tag: str) -> Path:
    return R / f"{tag}.heartbeat.txt"


def beat(path: Path, msg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def load_items(path: Path) -> list[dict]:
    """批次文件的三种历史形态：裸 list / {items} / {reviews}。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("items", "reviews", "cases", "candidates"):
            rows = data.get(key)
            if isinstance(rows, list):
                return [x for x in rows if isinstance(x, dict)]
    raise ValueError(f"无法识别批次结构：{path.name}")


def check_graph_sha() -> str:
    if not GRAPH.exists():
        raise SystemExit(f"[FATAL] 冻结图不存在：{GRAPH}")
    sha = sha16_file(GRAPH)
    if sha != EXPECTED_SHA:
        raise SystemExit(
            f"[FATAL] 图谱 SHA 漂移：期望 {EXPECTED_SHA}，实际 {sha}。"
            f"中止，不写任何文件 —— 先查明谁改了图。")
    return sha


def digest_paths(paths: list[Path]) -> list[dict]:
    out = []
    for p in sorted({q.resolve() for q in paths}):
        if p.is_file():
            st = p.stat()
            out.append({"path": _rel(p), "sha16": sha16_file(p), "bytes": st.st_size,
                        "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(
                            timespec="seconds")})
        elif p.is_dir():
            out.extend(digest_paths(sorted(p.rglob("*"))))
    return [d for d in out if not d["path"].endswith(".pyc")]


def cmd_plan(args: argparse.Namespace) -> int:
    sha = check_graph_sha()
    R.mkdir(parents=True, exist_ok=True)
    mp = manifest_path(args.tag)
    if mp.exists() and not args.force:
        print(f"[FATAL] manifest 已存在：{mp.name}\n"
              f"        在途波次不许重排 plan（防 stale dispatch）。确要重来加 --force。")
        return 2

    in_dir = args.in_dir.resolve()
    if not in_dir.is_dir():
        print(f"[FATAL] 输入批次目录不存在：{in_dir}")
        return 2
    files = sorted(in_dir.glob(args.in_glob))
    if not files:
        print(f"[FATAL] {in_dir} 下没有匹配 {args.in_glob} 的输入批次")
        return 2

    hb = beat_path(args.tag)
    hb.write_text(f"start {time.strftime('%F %T')} tag={args.tag}\n", encoding="utf-8")

    batches, bad = [], []
    for f in files:
        try:
            items = load_items(f)
        except Exception as exc:  # noqa: BLE001
            bad.append(f"{f.name}: {exc}")
            continue
        qids = [str(i.get(args.qid_key)) for i in items if i.get(args.qid_key)]
        if len(set(qids)) != len(qids):
            bad.append(f"{f.name}: {args.qid_key} 在输入内重复，清单不可用")
            continue
        batches.append({
            "batch_id": f.stem,
            "input_path": _rel(f),
            "n_qids": len(qids),
            "qids": qids,
            "output_path": _rel((args.out_dir / args.out_pattern.format(stem=f.stem)).resolve()),
        })
        beat(hb, f"planned {f.stem} n={len(qids)}")
    if bad:
        for line in bad:
            print(f"[FATAL] {line}")
        return 2

    protected_roots = [GRAPH] + [p.resolve() for p in args.protect]
    man = {
        "schema": SCHEMA_MANIFEST,
        "tag": args.tag,
        "planned_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": sha,
        "qid_key": args.qid_key,
        "n_batches": len(batches),
        "n_qids_total": sum(b["n_qids"] for b in batches),
        "batches": batches,
        # 写面 = 各批 output_path + 本 tag 的 heartbeat。越出即 guard 判失败。
        "write_scope": sorted([b["output_path"] for b in batches] + [_rel(hb)]),
        # 存根目录而非展平文件清单：否则保护目录里**新增**的文件永远检不出。
        "protected_roots": sorted(_rel(p) for p in protected_roots),
        "protected": digest_paths(protected_roots),
    }
    mp.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    beat(hb, f"plan done batches={len(batches)} qids={man['n_qids_total']}")
    print(f"[OK] manifest {mp}")
    print(f"     {len(batches)} 批 / {man['n_qids_total']} 题 / 保护 {len(man['protected'])} 个文件")
    print("     派活 prompt 里必须写死本批 batch_id 与 output_path，且 pending=0 即回报并停手。")
    return 0


def _classify(row: dict, peers_done: bool, age_min: float | None,
              stale_min: float, fresh_min: float) -> str:
    if row["status"] == "ok":
        return "done"
    if age_min is None:
        return "suspected_dead_no_output" if peers_done else "not_started"
    if age_min <= fresh_min:
        return "alive_hands_off"          # 3 分钟内写过：属于活代理的槽，别动
    if age_min >= stale_min and peers_done:
        return "suspected_dead"           # 双信号齐：同伴全齐 + 产物冻结
    if age_min >= stale_min:
        return "stalled"
    return "slow"


def cmd_check(args: argparse.Namespace) -> int:
    mp = manifest_path(args.tag)
    if not mp.exists():
        print(f"[FATAL] 先跑 plan：{mp} 不存在")
        return 2
    man = json.loads(mp.read_text(encoding="utf-8"))
    now = time.time()
    rows = []
    for b in man["batches"]:
        out = ROOT / b["output_path"]
        want = set(b["qids"])
        row = {"batch_id": b["batch_id"], "want": len(want), "output": b["output_path"]}
        if not out.exists():
            row.update(status="missing", have=0, mtime_age_min=None)
        else:
            row["mtime_age_min"] = round((now - out.stat().st_mtime) / 60.0, 1)
            try:
                items = load_items(out)
            except Exception as exc:  # noqa: BLE001
                row.update(status="unreadable", have=0, error=str(exc)[:160])
                rows.append(row)
                continue
            got = [str(i.get(man["qid_key"])) for i in items if i.get(man["qid_key"])]
            gs = set(got)
            blanks = [str(i.get(man["qid_key"])) for i in items
                      if i.get(man["qid_key"]) and _is_blank(i, man["qid_key"])]
            dup = sorted({q for q in gs if got.count(q) > 1})
            ok = gs == want and not dup and not blanks
            row.update(status="ok" if ok else "partial", have=len(gs),
                       missing=sorted(want - gs), extra=sorted(gs - want),
                       dup=dup, blank=blanks)
        rows.append(row)

    for row in rows:
        peers_done = all(r["status"] == "ok" for r in rows if r is not row)
        row["liveness"] = _classify(row, peers_done, row.get("mtime_age_min"),
                                    args.stale_min, args.fresh_min)

    n_ok = sum(1 for r in rows if r["status"] == "ok")
    print(f"tag={args.tag} 批次 {n_ok}/{len(rows)} 齐"
          f"（阈值：冻结 {args.stale_min} 分 / 免碰 {args.fresh_min} 分）")
    for r in rows:
        line = f"  {r['batch_id']:<16} {r['status']:<9} want {r['want']:>4} -> {r.get('have', 0):>4}"
        if r["status"] != "ok":
            line += (f"  missing={len(r.get('missing', []))}"
                     f" extra={len(r.get('extra', []))}"
                     f" dup={len(r.get('dup', []))}"
                     f" blank={len(r.get('blank', []))}")
        age = r.get("mtime_age_min")
        line += f"  [{r['liveness']}" + (f" age={age}min]" if age is not None else "]")
        print(line)
        if r.get("missing"):
            print(f"      缺 qid: {r['missing'][:12]}{' …' if len(r['missing']) > 12 else ''}")

    rep = {
        "schema": SCHEMA_CHECK, "tag": args.tag,
        "at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": man["graph_sha"], "thresholds": {"stale_min": args.stale_min,
                                                     "fresh_min": args.fresh_min},
        "n_batches": len(rows), "n_ok": n_ok, "rows": rows,
    }
    cp = R / f"{args.tag}.check.json"
    cp.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    beat(beat_path(args.tag), f"check ok={n_ok}/{len(rows)}")
    print(f"[wrote] {cp}")
    return 0 if n_ok == len(rows) else 1


def cmd_guard(args: argparse.Namespace) -> int:
    mp = manifest_path(args.tag)
    if not mp.exists():
        print(f"[FATAL] 先跑 plan：{mp} 不存在")
        return 2
    man = json.loads(mp.read_text(encoding="utf-8"))
    sha = check_graph_sha()
    if sha != man["graph_sha"]:
        print(f"[FAIL] 图指纹从 plan 时的 {man['graph_sha']} 变成 {sha}")
    scope = set(man["write_scope"])
    snap = {d["path"]: d for d in man["protected"]}
    cur = {d["path"]: d for d in digest_paths([ROOT / p for p in man["protected_roots"]])}
    changed, touched = [], []
    for path, old in snap.items():
        new = cur.get(path)
        if new is None:
            changed.append(f"{path} 消失（保护对象被删除）")
        elif new["sha16"] != old["sha16"]:
            changed.append(f"{path} 内容变了 {old['sha16']}->{new['sha16']} "
                           f"({old['bytes']}B->{new['bytes']}B)")
        elif new["mtime"] != old["mtime"]:
            touched.append(f"{path} 仅 mtime 变（内容一致）")
    extra_paths = sorted(set(cur) - set(snap))
    if extra_paths:
        touched.append(f"保护目录内新增 {len(extra_paths)} 个文件: {extra_paths[:5]}")

    leaked = sorted(p for p in _recent_writes(man) if p not in scope)
    print(f"tag={args.tag} 越界写入 {len(leaked)} 处 / 保护对象改动 {len(changed)} 处")
    for line in changed:
        print(f"  [FAIL] {line}")
    for line in leaked:
        print(f"  [FAIL] 写面之外被改：{line}")
    for line in touched:
        print(f"  [warn] {line}")
    if not changed and not leaked:
        print("  [OK] 写面守住了，保护对象零改动")
    return 1 if (changed or leaked) else 0


def _recent_writes(man: dict) -> list[str]:
    """列 data/compendium_rag 与 data/knowledge 里比 plan 时刻新的文件（不含 manifest 自身目录）。"""
    planned = datetime.fromisoformat(man["planned_at"]).timestamp()
    hits = []
    for base in (ROOT / "data" / "compendium_rag", ROOT / "data" / "knowledge"):
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            if rel.startswith("data/compendium_rag/reports/p9_fanout/"):
                continue
            if p.stat().st_mtime > planned:
                hits.append(rel)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a1 = sub.add_parser("plan", help="枚举期望批次并落 manifest")
    a1.add_argument("--tag", required=True)
    a1.add_argument("--in-dir", type=Path, required=True)
    a1.add_argument("--in-glob", default="*.json")
    a1.add_argument("--qid-key", default="qid")
    a1.add_argument("--out-dir", type=Path, required=True)
    a1.add_argument("--out-pattern", default="{stem}.json",
                    help="产物命名，{stem} = 输入文件 stem（评审批次用 {stem}_review.json）")
    a1.add_argument("--protect", type=Path, action="append", default=[],
                    help="冻结保护路径（文件或目录，可多次），guard 据此判越界")
    a1.add_argument("--force", action="store_true")
    a1.set_defaults(func=cmd_plan)

    a2 = sub.add_parser("check", help="按 qid-set 校验完成度 + 判存活")
    a2.add_argument("--tag", required=True)
    a2.add_argument("--stale-min", type=float, default=18.0,
                    help="产物冻结多少分钟才算死（P8 标定值，短了会误报慢代理）")
    a2.add_argument("--fresh-min", type=float, default=3.0,
                    help="多少分钟内写过就判为活代理槽位，禁止手工编辑")
    a2.set_defaults(func=cmd_check)

    a3 = sub.add_parser("guard", help="核对写面与保护对象")
    a3.add_argument("--tag", required=True)
    a3.set_defaults(func=cmd_guard)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
