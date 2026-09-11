# -*- coding: utf-8 -*-
"""剧情图谱验收测试（服务层 R15–R18，真实运行环境）。

真实 `uvicorn` 拉起 roleplay.main:app（真实依赖：真实图谱文件 5095 实体 / 4302 边、
真实 SQLite、真实 Ollama 后端），通过 HTTP 打真实端点，覆盖：
  R15 服务可启动 + stats 与落盘一致
  R16 检索接口端到端可用（含证据与溯源）
  R17 异常场景：空查询 / 超长 / 特殊字符 / 不存在角色 / 越界参数 → 不得 5xx
  R18 性能：单次检索 P95

为避免限流干扰，测试进程用 ROLEPLAY_RATE_LIMIT_PER_MINUTE=0 启动。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/acceptance_service.py
  .venv/Scripts/python.exe -X utf8 scripts/acceptance_service.py --port 8123
产物：docs/剧情图谱验收报告-服务层.md
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = "wu_ming_zhe"
GRAPH = ROOT / "data" / "knowledge" / f"plot_graph_{CHARACTER}.json"
RESULTS: list[dict] = []


def _free_port(preferred: int) -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1] if preferred == 0 else preferred


def _get(base: str, path: str, params: dict | None = None, timeout: int = 60):
    """返回 (status, json_or_text)。HTTPError 也折算成 status，不抛异常。"""
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except OSError:
            body = ""  # 连接被重置时响应体已不可读，只保留状态码
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def record(rid: str, title: str, source: str, ok: bool, detail: str):
    RESULTS.append({"id": rid, "title": title, "source": source, "ok": ok, "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {rid} {title} — {detail}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8123, help="0 = 自动选空闲端口")
    args = ap.parse_args()
    port = _free_port(args.port)
    base = f"http://127.0.0.1:{port}"

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    exp_ents, exp_edges = len(graph["entities"]), len(graph["edges"])

    env = dict(os.environ)
    env["ROLEPLAY_RATE_LIMIT_PER_MINUTE"] = "0"  # 验收期间关限流，避免 429 干扰
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(ROOT / "src")  # 未以可编辑模式安装，需显式给模块搜索路径
    py = str(ROOT / ".venv" / "Scripts" / "python.exe")
    log_path = ROOT / "data" / "knowledge" / "_audit" / "acceptance_service.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[service] 启动 uvicorn → {base}")
    logf = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [py, "-X", "utf8", "-m", "uvicorn", "roleplay.main:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=str(ROOT), env=env, stdout=logf, stderr=subprocess.STDOUT,
    )

    # 等待就绪
    ready, waited = False, 0.0
    while waited < 90:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                ready = True
                break
        except OSError:
            time.sleep(1.0)
            waited += 1.0
    if not ready:
        print(f"[FATAL] 服务 {waited:.0f}s 未就绪，日志见 {log_path}")
        proc.terminate()
        return 1
    time.sleep(2.0)  # 等 lifespan 完成

    try:
        # ---------------- R15 ----------------
        st, body = _get(base, "/api/knowledge/plot-graph/stats", {"character_id": CHARACTER})
        if st == 200 and isinstance(body, dict):
            # peek() 返回的是嵌套结构：corpus_stats / graph_stats
            gs = body.get("graph_stats") or {}
            got_ents = gs.get("entities")
            got_edges = gs.get("edges")
            ok = (got_ents == exp_ents and got_edges == exp_edges)
            record("R15", "服务可启动 + stats 与落盘一致", "S5 服务能力", ok,
                   f"HTTP {st}，API 返回 entities={got_ents}/edges={got_edges}，"
                   f"落盘 {exp_ents}/{exp_edges}")
        else:
            record("R15", "服务可启动 + stats 与落盘一致", "S5 服务能力", False,
                   f"HTTP {st}，响应 {str(body)[:120]}")

        # ---------------- R16 ----------------
        st, body = _get(base, "/api/knowledge/plot-graph/search",
                        {"q": "无名者是谁", "character_id": CHARACTER, "top_k": 3})
        ok = st == 200 and isinstance(body, dict) and body.get("results")
        if ok:
            r0 = body["results"][0]
            has_edge = bool(r0.get("edge"))
            has_src = bool((r0.get("meta") or {}).get("doc_id"))
            ok = has_edge and has_src
            detail = (f"HTTP {st}，返回 {len(body['results'])} 条，"
                      f"首条 edge={r0.get('edge')}，doc_id 可溯源={has_src}")
        else:
            detail = f"HTTP {st}，响应 {str(body)[:120]}"
        record("R16", "检索接口端到端可用（证据 + 溯源）", "S5 服务能力", ok, detail)

        # ---------------- R17 异常场景 ----------------
        cases = [
            ("空查询", {"q": ""}),
            ("超长查询(10000字符)", {"q": "暴雨" * 5000}),
            ("SQL注入串", {"q": "'; DROP TABLE entities;--"}),
            ("特殊字符/emoji", {"q": "<script>alert(1)</script>\U0001f480\u0000"}),
            ("不存在角色", {"q": "暴雨", "character_id": "no_such_character"}),
            ("top_k=0（越界）", {"q": "暴雨", "top_k": 0}),
            ("top_k=999（越界）", {"q": "暴雨", "top_k": 999}),
            ("纯空白查询", {"q": "   "}),
        ]
        app_5xx, transport_reset, detail_lines = [], [], []
        for name, params in cases:
            p = {"character_id": CHARACTER} if "character_id" not in params else {}
            p.update(params)
            st, body = _get(base, "/api/knowledge/plot-graph/search", p, timeout=90)
            detail_lines.append(f"{name}→{st}")
            if st >= 500:
                app_5xx.append((name, st, str(body)[:80]))
            elif st == -1:
                # 请求行过长 → 未进入应用层就被 HTTP 服务器拒绝（连接重置）
                transport_reset.append((name, str(body)[:60]))
        # 关键：异常请求之后服务必须仍然健康
        st_alive, _ = _get(base, "/api/knowledge/plot-graph/search",
                           {"q": "暴雨", "character_id": CHARACTER})
        alive = st_alive == 200
        ok = not app_5xx and alive
        record("R17", "异常场景：无应用层 5xx 且服务保持存活", "S5 安全", ok,
               "，".join(detail_lines) + f"｜异常后存活检查={st_alive}"
               + (f"｜5xx: {app_5xx}" if app_5xx else "")
               + (f"｜传输层拒绝: {[t[0] for t in transport_reset]}" if transport_reset else ""))

        # ---------------- R18 性能 ----------------
        lat, perf_fail = [], []
        for q in ["无名者是谁", "暴雨发生了什么", "圣洛夫基金会", "重塑之手", "金预言",
                  "潘家园", "Ms. Stranger", "SPDM"] * 3:
            t0 = time.perf_counter()
            st, _ = _get(base, "/api/knowledge/plot-graph/search",
                         {"q": q, "character_id": CHARACTER, "top_k": 3})
            dt = (time.perf_counter() - t0) * 1000
            if st != 200:
                perf_fail.append((q, st))
            lat.append(dt)
        p95 = statistics.quantiles(lat, n=20)[18] if len(lat) >= 20 else max(lat)
        ok = p95 <= 2000 and not perf_fail
        record("R18", "性能：单次检索 P95 ≤ 2000ms", "S5 性能", ok,
               f"n={len(lat)}，均值 {statistics.mean(lat):.0f}ms，"
               f"P95 {p95:.0f}ms，最大 {max(lat):.0f}ms｜非200: {perf_fail[:3]}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        logf.flush()
        logf.close()

    # ---------------- 报告 ----------------
    passed = sum(1 for r in RESULTS if r["ok"])
    failed = [r for r in RESULTS if not r["ok"]]
    lines = [
        "# 剧情图谱验收报告 · 服务层（R15–R18，真实运行环境）",
        "",
        f"- 执行时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 运行方式：真实 `uvicorn roleplay.main:app`（127.0.0.1:{port}），"
        f"真实图谱 {exp_ents} 实体 / {exp_edges} 边，限流已关闭以排除干扰",
        f"- 结果：**通过 {passed} / 失败 {len(failed)}**",
        "",
        "| ID | 需求 | 依据 | 结果 | 证据 |",
        "|---|---|---|---|---|",
    ]
    for r in RESULTS:
        lines.append(
            f"| {r['id']} | {r['title']} | {r['source']} | "
            f"{'✅ PASS' if r['ok'] else '❌ FAIL'} | {r['detail']} |"
        )
    lines += ["", "## 服务端日志（uvicorn，warning 级）", "", "```"]
    tail = log_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-40:]
    lines += (tail or ["（无输出）"])
    lines += ["```"]
    out = ROOT / "docs" / "剧情图谱验收报告-服务层.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[service] 报告 → {out}")
    print(f"[service] 通过 {passed} / 失败 {len(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
