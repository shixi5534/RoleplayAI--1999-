#!/usr/bin/env bash
# r11 回归闸门：三主数（300cn / blind206 / gen120）串行跑，产出落在
# data/compendium_rag/reports/eval_*_r11.{json,log}，进度看 _r11_gate_runner.log。
#
# 与 r10 版（compendium_rag_r10_regression_gate.sh）的关系：
#   - 结构照抄，只换题集产物名与图锚点；r10 产物是只读历史件，不得覆盖。
#   - r11 = V9P5，相对 r10(V9P4) 只删了 1 条边
#     `集体潜意识-[包含]->迷思海`（用户 2026-10-10 正典裁决），
#     图 sha16 fb7322dd4f558e7c -> 911bb538160db80e，边 27111 -> 27110。
#   - L3 的 679 题 prompt/context/judge-in 实测与 r10 逐字节相同，
#     但三主数题集不同，仍须本 runner 现算，不得沿用 r10 读数。
#
# 用法（务必脱离会话生命周期）：
#   powershell -Command "Start-Process -WindowStyle Hidden -FilePath bash `
#     -ArgumentList 'scripts/compendium_rag_r11_regression_gate.sh'"
set -u
cd "$(dirname "$0")/.." || exit 1
export PYTHONHASHSEED=0 CMPRAG_LEX_WEIGHT=1.0 CMPRAG_RRF_K=1 CMPRAG_LEX_FIRST=0
R=data/compendium_rag/reports
LOG=$R/_r11_gate_runner.log
PY=.venv/Scripts/python.exe

GSHA=$("$PY" -c "import hashlib;print(hashlib.sha256(open('data/compendium_rag/graph.json','rb').read()).hexdigest()[:16])")
echo "=== r11 gate start $(date -Is) graph=$GSHA ===" >> "$LOG"
if [ "$GSHA" != "911bb538160db80e" ]; then
  echo "!!! FATAL graph sha16=$GSHA != 911bb538160db80e (r11) — abort" >> "$LOG"
  exit 2
fi

run() {  # $1=题集路径  $2=产物名
  echo "--- $2 set=$1 start $(date -Is)" >> "$LOG"
  "$PY" -X utf8 scripts/compendium_rag_eval300.py --set "$1" --out "$R/$2.json" \
        > "$R/$2.log" 2>&1
  echo "--- $2 exit=$? end $(date -Is)" >> "$LOG"
}

run data/knowledge/_audit/rag_testset_300_cn.json          eval_300cn_k1_r11
run data/knowledge/_audit/blind_v1/questions_strict.json   eval_blind_k1_r11
run data/knowledge/_audit/rag_testset_gen_r1r2.json        eval_gen120_k1_r11

echo "=== r11 gate done $(date -Is) ===" >> "$LOG"
