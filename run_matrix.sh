#!/usr/bin/env bash
# Qwen3.6-35B-A3B spec-decode matrix on RTX 3090
# Bench each config sequentially; llama-server is restarted between configs.
# All configs pinned to GPU 1 (CUDA_VISIBLE_DEVICES=1) so GPU 0 stays free for Ollama.

set -euo pipefail

OUT=${OUT:-"$(dirname "$0")/results"}
RUNNER="$(dirname "$0")/bench_runner.py"
PY=${PY:-/home/reachym/dev/reachy-agent/robot/.venv/bin/python}

mkdir -p "$OUT"

echo "=========================================="
echo " Matrix: baseline | ngram-cache | ngram-mod (srogmann params) | classic-draft"
echo "=========================================="

# 1. Baseline — no spec decode
"$PY" "$RUNNER" \
    --config "baseline" \
    --output "$OUT/baseline.json"

# 2. ngram-cache (llama.cpp classic n-gram lookup)
"$PY" "$RUNNER" \
    --config "ngram-cache" \
    --output "$OUT/ngram-cache.json" \
    --server-args --spec-type ngram-cache

# 3. ngram-mod with srogmann's recommended params (from PR #19493 comment)
"$PY" "$RUNNER" \
    --config "ngram-mod-n24" \
    --output "$OUT/ngram-mod.json" \
    --server-args --spec-type ngram-mod --spec-ngram-size-n 24 --draft-min 48 --draft-max 64

# 4. Classic external draft with qwen3:0.6b (pulled locally via Ollama, re-export GGUF)
#    → qwen3:0.6b is already in Ollama, but we need llama.cpp GGUF. Try auto-download from HF:
"$PY" "$RUNNER" \
    --config "draft-qwen3-0.6b" \
    --output "$OUT/draft-qwen3-0.6b.json" \
    --server-args --model-draft "$HOME/benchmarks/models/qwen3-0.6b/Qwen3-0.6B-Q4_K_M.gguf" --draft-max 16 --draft-min 4

echo ""
echo "=== MATRIX COMPLETE ==="
ls -la "$OUT"/
