#!/usr/bin/env bash
# v9-P3 · graph_max_edges 五档曲线 runner（脱离会话生命周期）。
# 为什么单独一个 runner：CLI 后台任务在会话重启时会打断外层，但 python 子进程变孤儿
# 继续跑，下一轮再启动就出现「两个进程写同一批 jsonl」的竞态（本会话踩过）。
# 串行 + 记 exit + 进度看 _p3_me_runner.log，让这件事可查、可重放。
#
# 用法：
#   powershell -Command "Start-Process -WindowStyle Hidden -FilePath bash `
#     -ArgumentList 'scripts/compendium_rag_p3_me_curve_runner.sh'"
# 重跑安全：逐题产物 p3_me/{tag}_me{档}.jsonl 按 qid 续跑，不会重复计费。
set -u
cd "$(dirname "$0")/.." || exit 1
export PYTHONHASHSEED=0 CMPRAG_LEX_WEIGHT=1.0 CMPRAG_RRF_K=1 CMPRAG_LEX_FIRST=0
R=data/compendium_rag/reports
LOG=$R/_p3_me_runner.log
PY=.venv/Scripts/python.exe
GSHA=$("$PY" -c "import hashlib;print(hashlib.sha256(open('data/compendium_rag/graph.json','rb').read()).hexdigest()[:16])")
echo "=== curve start $(date -Is) graph=$GSHA ===" >> "$LOG"
"$PY" -X utf8 scripts/compendium_rag_p3_max_edges_curve.py >> "$LOG" 2>&1
echo "=== curve exit=$? $(date -Is) ===" >> "$LOG"
