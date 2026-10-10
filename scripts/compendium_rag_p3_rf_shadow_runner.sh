#!/usr/bin/env bash
# v9-P3 · 角色域过滤影子评测 runner（脱离会话生命周期，理由同 me_curve_runner）。
# 用法：
#   powershell -Command "Start-Process -WindowStyle Hidden -FilePath bash `
#     -ArgumentList 'scripts/compendium_rag_p3_rf_shadow_runner.sh'"
# 重跑安全：逐题产物 reports/p3_rf_shadow/{tag}_w{档}.jsonl 按 qid 续跑。
# 判死活别看日志（stdout 块缓冲），看 jsonl 行数在不在长。
set -u
cd "$(dirname "$0")/.." || exit 1
export PYTHONHASHSEED=0 CMPRAG_LEX_WEIGHT=1.0 CMPRAG_RRF_K=1 CMPRAG_LEX_FIRST=0
R=data/compendium_rag/reports
LOG=$R/_p3_rf_shadow_runner.log
PY=.venv/Scripts/python.exe
GSHA=$("$PY" -c "import hashlib;print(hashlib.sha256(open('data/compendium_rag/graph.json','rb').read()).hexdigest()[:16])")
echo "=== shadow start $(date -Is) graph=$GSHA ===" >> "$LOG"
"$PY" -X utf8 scripts/compendium_rag_p3_rolefilter_shadow.py >> "$LOG" 2>&1
echo "=== shadow exit=$? $(date -Is) ===" >> "$LOG"
