#!/usr/bin/env bash
# r10 回归闸门：三主数（300cn / blind206 / gen120）串行跑，产出落在
# data/compendium_rag/reports/eval_*_r10.{json,log}，进度看 _r10_gate_runner.log。
#
# 与 v9p1 版（compendium_rag_v9p1_regression_gate.sh）的关系：
#   - 结构照抄，只换题集产物名与图锚点；v9p1 产物是 vendored 只读历史件，不得覆盖。
#   - v9p1 三份 eval 的 corpus 是 r8(27151 边)，不是现行 r10(27111 边)；
#     P7 delta 表必须以本 runner 的 r10 读数为权威。
#
# 用法（务必脱离会话生命周期）：
#   powershell -Command "Start-Process -WindowStyle Hidden -FilePath bash `
#     -ArgumentList 'scripts/compendium_rag_r10_regression_gate.sh'"
set -u
cd "$(dirname "$0")/.." || exit 1
export PYTHONHASHSEED=0 CMPRAG_LEX_WEIGHT=1.0 CMPRAG_RRF_K=1 CMPRAG_LEX_FIRST=0
R=data/compendium_rag/reports
LOG=$R/_r10_gate_runner.log
PY=.venv/Scripts/python.exe

GSHA=$("$PY" -c "import hashlib;print(hashlib.sha256(open('data/compendium_rag/graph.json','rb').read()).hexdigest()[:16])")
echo "=== r10 gate start $(date -Is) graph=$GSHA ===" >> "$LOG"

run() {  # $1=题集路径  $2=产物名
  echo "--- $2 set=$1 start $(date -Is)" >> "$LOG"
  "$PY" -X utf8 scripts/compendium_rag_eval300.py --set "$1" --out "$R/$2.json" \
        > "$R/$2.log" 2>&1
  echo "--- $2 exit=$? end $(date -Is)" >> "$LOG"
}

run data/knowledge/_audit/rag_testset_300_cn.json          eval_300cn_k1_r10
run data/knowledge/_audit/blind_v1/questions_strict.json   eval_blind_k1_r10
run data/knowledge/_audit/rag_testset_gen_r1r2.json        eval_gen120_k1_r10

echo "=== r10 gate done $(date -Is) ===" >> "$LOG"
