#!/usr/bin/env bash
# v9-P1 回归闸门：三主数（300cn / blind206 / gen120）串行跑，产出落在
# data/compendium_rag/reports/eval_*_v9p1.{json,log}，进度看 _v9p1_gate_runner.log。
#
# 为什么单独一个 runner：CLI 后台任务在会话重启时会被打断，但它的 python 子进程
# 会变成孤儿继续跑，下一轮再启动就出现「两个进程写同一个产物」的竞态。
# 串行 + 产物对账（每步记 exit）让这件事可查、可重放。
#
# 用法（务必脱离会话生命周期）：
#   powershell -Command "Start-Process -WindowStyle Hidden -FilePath bash `
#     -ArgumentList 'scripts/compendium_rag_v9p1_regression_gate.sh'"
set -u
cd "$(dirname "$0")/.." || exit 1
export PYTHONHASHSEED=0 CMPRAG_LEX_WEIGHT=1.0 CMPRAG_RRF_K=1 CMPRAG_LEX_FIRST=0
R=data/compendium_rag/reports
LOG=$R/_v9p1_gate_runner.log
PY=.venv/Scripts/python.exe

GSHA=$("$PY" -c "import hashlib;print(hashlib.sha256(open('data/compendium_rag/graph.json','rb').read()).hexdigest()[:16])")
echo "=== gate start $(date -Is) graph=$GSHA ===" >> "$LOG"

run() {  # $1=题集路径  $2=产物名
  echo "--- $2 set=$1 $(date -Is)" >> "$LOG"
  "$PY" -X utf8 scripts/compendium_rag_eval300.py --set "$1" --out "$R/$2.json" \
        > "$R/$2.log" 2>&1
  echo "--- $2 exit=$? $(date -Is)" >> "$LOG"
}

run data/knowledge/_audit/rag_testset_300_cn.json          eval_300cn_k1_v9p1
run data/knowledge/_audit/blind_v1/questions_strict.json   eval_blind_k1_v9p1
run data/knowledge/_audit/rag_testset_gen_r1r2.json        eval_gen120_k1_v9p1

echo "=== gate done $(date -Is) ===" >> "$LOG"
