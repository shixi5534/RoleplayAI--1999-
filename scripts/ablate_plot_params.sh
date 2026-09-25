#!/usr/bin/env bash
# 剧情层参数消融批跑（串行，避免争抢 ollama）
# 关键指标：inject_pass（产品真实口径）；strict_pass 仅参考
set -u
cd "$(dirname "$0")/.." || exit 1
PY=./.venv/Scripts/python.exe
TS=data/knowledge/_audit/rag_testset_300_clean.json
OUTDIR=data/knowledge/_audit

run() {
  local envs="$1" name="$2"
  echo "=============================================================="
  echo "[ablate] $name  env: $envs"
  echo "=============================================================="
  env $envs "$PY" -X utf8 scripts/eval_plot_rag.py \
    --testset "$TS" --evidence-override "" --top 6 \
    --out "$OUTDIR/ablate_${name}.json" --quiet 2>&1 | tail -6
}

run "ROLEPLAY_PLOT_WEIGHT_SEMANTIC=2.0" "wsem2"
run "ROLEPLAY_PLOT_PPR_NODE_SPECIFICITY=true" "nodespec"
run "ROLEPLAY_PLOT_MAX_HOPS=1" "hops1"

echo "=============================================================="
echo "[ablate] 全部完成"
