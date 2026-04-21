#!/usr/bin/env bash
# P0 verification matrix — research-guided, publish-ready.
# Based on 2026-04-21 follow-up deep research:
#   - MoESD arXiv 2505.19645 / Utility-Driven SD 2506.20675 / MoE-SpeQ 2511.14102 confirm
#     that A3B-class MoE spec-decode is theoretically net-negative at small K.
#   - Classic draft must use Qwen3.5-0.8B (vocab 248320), NOT Qwen3:0.6B (vocab 151936).
#   - Metric `predicted_per_second` is correct, but must be reported WITH draft stats.
#
# This matrix adds:
#   P0-1: Classic draft w/ Qwen3.5-0.8B (REPLACES original invalid qwen3:0.6b run),
#         sweeping --draft-max {8, 16, 32}
#   P0-2: Output tokens 1000 (gives ngram caches runway to build)
#   P1:   ngram-mod --spec-ngram-size-n sweep {8, 12, 16, 20, 24, 32}
#
# Note: `-fa off` variant SKIPPED — requires fp16 KV (cannot combine with -ctk q8),
#       and our research confirmed FA is not the bottleneck.

set -uo pipefail  # dropped -e so partial failures don't kill the whole matrix

OUT=${OUT:-"$(dirname "$0")/results/verify"}
RUNNER="$(dirname "$0")/bench_runner.py"
PY=${PY:-/home/reachym/dev/reachy-agent/robot/.venv/bin/python}
DRAFT="$HOME/benchmarks/models/qwen3.5-0.8b/Qwen3.5-0.8B-Q4_K_M.gguf"
mkdir -p "$OUT"

run() {
    local name="$1" ; shift
    echo ""
    echo "=============================================="
    echo " $name"
    echo "=============================================="
    "$PY" "$RUNNER" --config "$name" --gpu 1 --output "$OUT/$name.json" "$@" || echo "(failed $name; continuing)"
}

# ── P0-1: classic draft with CORRECT vocab Qwen3.5-0.8B ─────────────────────
for DM in 8 16 32; do
    run "draft-q35-08b-max$DM" --server-args "-md $DRAFT -ngld 99 --draft-max $DM --draft-min 4"
done

# ── P0-2: 1000-token output variants ─────────────────────────────────────────
run "baseline-1000tok" --max-tokens 1000
run "ngcache-1000tok"  --max-tokens 1000 --server-args '--spec-type ngram-cache'
run "ngmod-n24-1000tok" --max-tokens 1000 --server-args '--spec-type ngram-mod --spec-ngram-size-n 24 --draft-min 48 --draft-max 64'
run "draft-q35-08b-1000tok" --max-tokens 1000 --server-args "-md $DRAFT -ngld 99 --draft-max 16 --draft-min 4"

# ── P1: ngram-mod N sweep ───────────────────────────────────────────────────
for N in 8 12 16 20 32; do
    run "ngmod-n$N" --server-args "--spec-type ngram-mod --spec-ngram-size-n $N --draft-min 48 --draft-max 64"
done

# ── P1: KV fp16 control (with fa on — fa can't be off with kv q8) ──────────
run "ngcache-kv-fp16" --kv-fp16 --server-args '--spec-type ngram-cache'

echo ""
echo "=== P0 MATRIX COMPLETE ==="
ls -la "$OUT"
